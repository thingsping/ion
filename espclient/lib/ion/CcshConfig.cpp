/*
 * Source code : all rights reserved
 * Copyright (c) 2019 onwards, 
 * Authors: Qantom Software Private Limited
 *
 * This program is free software (...)
 * You should have received a copy of the GNU Affero General Public License
 * along with this program (...)
 *
 * You must make all your source code available in case you release code
 * or any code that uses this code. You can be opt for a commercial license from  
 * Qantom software private limited, if you do not want to share your code and 
 * want a commercial license. Buying such a license is mandatory as soon as you
 * develop commercial activities involving the ionserver software without
 * disclosing the source code of your own applications (...)
 *
 */


#include "CcshConfig.h"


IonConfig* IonConfig :: instance = 0 ;

IonConfig::IonConfig(){
    logger = QLogger :: getInstance() ; 
    devId = getDeviceId(); 
    deviceKey = "" ;
    configcontents = "" ; 
    m_cfgvalid = true ; // We'll start with the assumption that config is valid. If 
                // endpoint chooses to set using JSON string, and if json is invalid, 
                // then we'll set this to false there. 
    things  = new LinkedList<ThingDetails*>();
}

 void IonConfig :: convertJSONToConfig() {
    DynamicJsonDocument ctlDoc(1024);
    DeserializationError err = deserializeJson(ctlDoc, configcontents);
     if (err) {
        m_cfgvalid = false ; 
        logger -> setLevel(QLogger :: LEVEL_DEBUG, true); // If the configuration is junk,
            //it is  possible that the level has been set to a junk value which is 
            // greater than DEBUG
        logger -> debug("Error in configuration details", String(err.c_str()), 
            "Contents = ", String(configcontents)); 
    } else {
        m_cfgvalid = true ; 
        //deviceKey = ctlDoc["DeviceKey"].as<String>();
        if (ctlDoc.containsKey("LogLevel")) {
            loglevel = ctlDoc["LogLevel"].as<int>() ;
        } else {
            loglevel = QLogger ::LEVEL_INFO ; 
        }
        logger -> setLevel(loglevel); 
        if (ctlDoc.containsKey("Server")) {
            server = ctlDoc["Server"].as<String>();      
        } else {
            server = DEFAULTSERVER ; 
        }
        
        if (ctlDoc.containsKey("PollingPort")) {
            pollingPort = ctlDoc["PollingPort"]; 
        }else {
            pollingPort = DEFAULTPOLLINGPORT; 
        }
        if (ctlDoc.containsKey("IsLocalGateway")){
            isLocalGw = ctlDoc["IsLocalGateway"]; 
        } else {
            isLocalGw = false ; 
        }

        if (ctlDoc.containsKey("IsRegistrationMandatory")){
            m_regMandatory = ctlDoc["IsRegistrationMandatory"];
        } else {
            m_regMandatory = false ; 
        }

        JsonArray arr = ctlDoc["Things"].as<JsonArray>();

        for (JsonObject repo : arr) { 
            String rname, rloc, rTag; 
            rname="";
            rloc = DEFAULTLOCATION ; 
            rTag = "" ; 
            int paramCount = repo.size(); 
            LinkedList<String>* pKeys = 0 ; 
            LinkedList<String>* pVals = 0 ;
            for (JsonPair kvp : repo){
                const char* key = kvp.key().c_str() ; 
                //logger -> debug("Key = " + String(key) + "; Val = " + repo[key].as<String>()); 
                if (strcmp(key, "Name") == 0){
                    rname = repo["Name"].as<String>();     
                } else if (strcmp(key, "Location") == 0){
                    rloc = repo["Location"].as<String>();   
                } else if (strcmp(key, "Tag") == 0){
                    rTag = repo["Tag"].as<String>();    
                } else {
                    if (pKeys == 0){
                        pKeys = new LinkedList<String>() ; 
                        pVals = new LinkedList<String>() ; 
                    }
                    pKeys -> add(String(key));
                    pVals -> add(repo[key].as<String>());
                    //logger -> debug ("Adding " + String(key) + "[" + repo[key].as<String>() + "]");
                }
            }
            ThingDetails *td  = new ThingDetails(rname, rloc, rTag); 
            td -> keys = pKeys; 
            td -> vals = pVals ; 
            things -> add(td); 
        }
        logger -> debug("Configuration initialized. Config = ", getConfigJson()); 
    }
}

IonConfig* IonConfig :: getConfiguration() {
    if (!instance) {        
        instance = new IonConfig() ; 
    }
    return instance ; 
}

void IonConfig :: setConfiguration(const char* thingsjson){
    // First check if the incoming contents is the same as the 
    // saved configuration :
    String cc = getConfigJsonBegin(); 
    cc.concat(thingsjson); 
    cc.concat("}");     
}

String IonConfig :: getConfigJsonBegin(){
    String cc = "{"; 
    cc.concat(F("\"LogLevel\" : ")); 
    cc.concat(String(loglevel)) ; 
    cc.concat(F(",  \"Server\":\"" )); 
    cc.concat(server); 
    cc.concat(F("\", \"IsLocalGateway\":")); 
    cc.concat(isLocalGw); 
    cc.concat(F(", \"Things\":")); 
    return cc;
}

String IonConfig :: getConfigJson() {
    String cc = getConfigJsonBegin(); 
    String thingsjson = "["; 
    int sz = things -> size(); 
    for (int i = 0 ; i < sz ; i++)
    {
        ThingDetails* thing = things -> get(i);  
        if (i != 0)
            thingsjson.concat(",") ;
        thingsjson.concat(F("{\"Name\":\"")); 
        thingsjson.concat(thing -> name);
        thingsjson.concat(F("\", \"Location\" : \"") );
        thingsjson.concat(thing -> location); 
        thingsjson.concat(F("\", \"Tag\":\""));
        thingsjson.concat(thing -> tag); 
        thingsjson.concat(F("\"}")) ;  
    }
    thingsjson.concat("]");
    cc.concat(thingsjson); 
    cc.concat("}"); 
    return cc; 
}

String IonConfig :: getDeviceId() {
    if (devId.equals("")) {
        byte mac[6];
        WiFi.macAddress(mac);
        for (int i = 0 ; i < 6; i++) {
            if (mac[i]  < 16) {
            devId.concat('0');
            devId.concat(String(mac[i], HEX)) ;
            }
            else {
            devId.concat(String(mac[i], HEX)) ;
            }
        }
    }
    return devId ;
}


int IonConfig :: getPollingPort() {
    return pollingPort ; 
}

String IonConfig :: getParamValue(const char* name, const char* key){
    String paramValue = "" ; 
    int sz = things -> size() ; 
    String nmString = String(name); 
    for (int i = 0 ; i < sz; i++) {
       ThingDetails* td = things -> get(i); 
       if (nmString.equals(td -> name)) {
           LinkedList<String>* keys = td ->keys ; 
           if (keys != 0 ) {
             int szkeys = keys -> size() ; 
             for (int j = 0 ; j < szkeys; j++){
                 String curkey = keys -> get(j); 
                 if (curkey.equals(key)){
                     paramValue = td ->vals -> get(j); 
                     break ; 
                 }

             }
           }
           break ; 
       }
    }
    return paramValue ; 
}

String IonConfig :: getLocation (const char* name){
   String loc  = "" ; 
   int sz = things -> size() ; 
   String nmString = String(name); 
   for (int i = 0 ; i < sz; i++) {
       ThingDetails* td = things -> get(i); 
       if (nmString.equals(td -> name)) {
           loc = td -> location ; 
           break ; 
       }
   }
   return loc;
}

String IonConfig :: getTag(const char* name){
    String tag  = "" ; 
    int sz = things -> size() ; 
    String nmString = String(name); 
    for (int i = 0 ; i < sz; i++) {
        ThingDetails* td = things -> get(i); 
        if (nmString.equals(td -> name)) {
            tag = td -> tag ; 
            break ; 
        }
    }
    return tag.c_str();
     
}

void IonConfig :: setSsidDetails(String ssid, String password){ 
    String ssidcontents = "{\"SSID\":\""; 
    ssidcontents.concat(ssid); 
    ssidcontents.concat("\", \"SsidPassword\":\"" );
    ssidcontents.concat(password); 
    ssidcontents.concat("\"}"); 
    this -> ssid = ssid ; 
    this -> ssidPassword = password ;
}

String IonConfig :: getDeviceKey() {
    return deviceKey; 
}

void IonConfig :: setDeviceKey(String devkey){
      deviceKey = devkey; 
}

int IonConfig :: getLogLevel() {
    return loglevel ; 
}

String IonConfig :: getSsid() {
    return ssid ; 
}

String IonConfig :: getSsidPassword() {
    return ssidPassword; 
} 

void IonConfig :: setTagAndLocation(int i, String tag, String loc){
    ThingDetails* td = things -> get(i); 
    td -> tag = tag; 
    td ->location = loc ; 

}

void IonConfig :: addThing(String name, String location, String tag=""){
    ThingDetails *td  = new ThingDetails(name, location, tag); 
    things -> add(td);     
}
