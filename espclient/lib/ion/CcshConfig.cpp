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
}

 void IonConfig :: convertJSONToConfig() {
    //TBD - have to get this working with new support for ION 
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
    
    return cc;
}

String IonConfig :: getConfigJson() {
    String cc = getConfigJsonBegin(); 
    String thingsjson = "[]"; 
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
