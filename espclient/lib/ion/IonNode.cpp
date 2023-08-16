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
#include "IonNode.h"

IonNode :: IonNode(String devid,  String k)          
{
    int ldevid = devid.length() ; 
    deviceId = (char*)malloc ( sizeof(char) * (ldevid +1) ); 
    strcpy(deviceId, devid.c_str()); 
    deviceId[ldevid] = 0; 
    // this -> deviceId = devid ; 
    
    lastRegTime = 0l; 
    lastAdTime = 0l ; 
    lastPubTime = 0l ;
    logger = QLogger::getInstance() ; 
}

IonNode :: ~IonNode() {
    if (deviceId)
        free((char*)deviceId); 
    if (deviceKey)
        free (deviceKey);
    if (allThings) {
        allThings -> ~LinkedList<IonThing*>(); 
    } 
}

void IonNode :: addThing(IonThing* thing){
    //QLogger :: getInstance() -> debug(String("Adding thing - ") + thing -> getName());
    allThings ->add(thing); 
}

IonThing* IonNode :: getThing() {
    if (allThings -> size() > 0){
        return allThings -> get(0); 
    }else {
        return 0 ; 
    }
}

bool IonNode :: hasOutputDevice() {
    return false ; 
}

IonThing* IonNode :: getThing(int idx){
    if (allThings -> size() >= idx){
        return allThings -> get(idx);
    } else {
        return 0 ; 
    }
}

IonThing* IonNode :: getThingByName(String name){
    // The best way I could think of - as tags are getting
    // embedded into the name. Can't change the protocol 
    // to include 'tag' as it will start making the protocol
    // to have too many things. 
    IonThing* alternateThing = 0 ;
    int sz = allThings -> size();  
    for (int i = 0 ; i < sz; i++) {
        IonThing* thing = allThings -> get(i);
        String thingName = thing -> getName();
        if (thingName.equals(name)){
            return thing ;
        }
        // If we've got here then it means we have not yet found what we want
        // just keep an alternative ready
        if (!alternateThing) { // If we have already an alternate thing 
            // then let's not waste time again. 
            String tag =  thing -> getTag() ; 
            if (!tag.equals("")) {
                thingName.concat("-"); 
                thingName.concat(tag); 
                if (thingName.equals(name)){
                    alternateThing = thing ; 
                }
            }
        }
        // Even if we have found an alternate thing we will continue to find
        // for the thing with given name. If a direct match with name is found
        // that has highest precedence. 
    }
    return alternateThing ; 
}

int IonNode :: getThingsCount() {
    return allThings -> size() ; 
}

String IonNode :: getRegJson() {
    return "{}";
}

String IonNode :: getAdJson() {
    return "{}";
}

String IonNode :: processControlJson(String ctljson, bool checkForAuth){
    // Have to rewrite this method to address issue where control message does not
    // have full cotnent. 
}




