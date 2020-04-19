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
#include "IonFactory.h"

IonFactory :: IonFactory() {
    server = 0 ; 
    node = 0 ; 
    addrOnly= 0  ; 
    things_created = new LinkedList<IonThing*>() ; 
    names_created = new LinkedList<char*>(); 
    logger = QLogger :: getInstance() ; 
    init();
}

IonFactory :: ~IonFactory() {
    if (server) 
        delete server ; 
    if (node) 
        delete node ; 
    if (addrOnly)
        free(addrOnly); 
    int sz = things_created -> size();
    for (int i =0 ; i < sz; i++){
        delete things_created -> get(i);
    }
    sz = names_created -> size();
    for (int i =0 ; i < sz; i++){
        free (names_created -> get(i));
    } 
}

void IonFactory :: saveEntities() {
    String json = "[" ;
    int sz = things_created -> size(); 
    for (int i = 0 ; i < sz ; i++)
    {
        IonThing* thing = things_created -> get(i);  
        String name =  thing -> getName(); 
        String location = thing -> getLocation() ; 
        String tag = thing -> getTag() ; 
        if (i != 0)
            json += ",";
        json.concat(F("{\"Name\":\"")); 
        json.concat(name);
        json.concat(F("\", \"Location\" : \"") );
        json.concat(location); 
        json.concat(F("\", \"Tag\":\""));
    
        json.concat(tag); 
        json.concat(F("\"}")) ;  
    }
    json += "]";
    configuration -> setConfiguration(json.c_str()) ; 
}

void IonFactory :: init( ) {
        configuration = IonConfig :: getConfiguration() ;
        String srvaddr = configuration -> getServer() ; 
        logger -> debug("Server returned by config = " + String(srvaddr)); 
        int idx =  srvaddr.indexOf(":") ;  
        if (idx != -1) {
            if (addrOnly) {
                free(addrOnly); 
            }
            addrOnly = (char*)(malloc(sizeof(char) * (idx+1))); 
            strncpy(addrOnly, srvaddr.substring(0, idx).c_str(), idx ); 

            addrOnly[idx] = 0 ; 
            int port = 80;
            String portStr = srvaddr.substring(idx+1); 
            port = portStr.toInt(); // Validate - issue # 23
            server = new IonServer(addrOnly, port); 
         } else {
            if (addrOnly) {
                free(addrOnly); 
            }
            addrOnly = (char*)(malloc(sizeof(char) * srvaddr.length() +1)); 
            strcpy(addrOnly, srvaddr.c_str()); 
            server = new IonServer(addrOnly) ; 
         }
         node = new IonNode(configuration -> getDeviceId().c_str(), 
                 configuration -> getDeviceKey().c_str());
}

Sensor IonFactory :: createSensor(const char* name) {
    String loc =configuration -> getLocation(name);
    String tag = configuration -> getTag(name) ;  
    Sensor* sr = new Sensor(name, loc);
    sr -> setTag(tag);  
    node -> addThing(sr);
    things_created -> add(sr);
    return *sr ; 
}

Actuator IonFactory :: createActuator(String name, const char* action) {
    int l = name.length() ; 
    char* new_name = (char*) (malloc (sizeof(char) * (l+1))); 
    strcpy(new_name, name.c_str()); 
    new_name[l] = 0; 
    names_created -> add(new_name); 
    return createActuator(new_name, action) ; 
}

Actuator IonFactory :: createActuator(const char* name, const char* action) {
  
    String loc =configuration -> getLocation(name);
    String tag = configuration -> getTag(name) ;  
    Actuator * act = new Actuator(name, loc,  action);
    act -> setTag(tag);
    node -> addThing(act); 
    things_created -> add(act);
    return *act ; 
}

void IonFactory :: run(){    
    if (configuration -> isConfigEmpty()){ 
        saveEntities() ; 
    }
    
    BlinkType bt = NoBlink ; 
    bool isconnected = server -> connectToWifi((configuration -> getSsid()).c_str(), 
        (configuration -> getSsidPassword()).c_str()) ; 
    if (!isconnected){    
        bt = AirplaneBlink;
    } else {
        String a = server -> getLocalIP(); 
        logger -> debug("Connected to wifi - ", server -> getLocalIP());             
        // If we get out of the above call, it either means that the 
        // server doesn't have a new config for this device or the 
        // server doesn't even have a config for this device. 
        if (configuration -> isConfigValid()){
            node -> setAddress(server -> getLocalIP() ); 
            server -> setNode(node); 
            server -> registerWithServer();  
        } else {        
            bt = AirplaneBlink;
        }
        if (bt != NoBlink){
            
            while (true){
                if (bt == AirplaneBlink){
                    for (int i = 0 ; i < 5; i++){
                        BoardSpecific :: setStatusLED(1); 
                        delay(100); 
                        BoardSpecific :: setStatusLED(0); 
                        delay(100); 
                    }
                    BoardSpecific :: setStatusLED(1); 
                    delay(500); 
                    BoardSpecific :: setStatusLED(0); 
                    delay(500); 
                } else {
                    BoardSpecific :: setStatusLED(1); 
                    delay(500); 
                    BoardSpecific :: setStatusLED(0); 
                    delay(500); 
                }
            }
        }

    }
    

}