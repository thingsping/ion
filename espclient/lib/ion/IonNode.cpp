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
    allThings = new LinkedList<IonThing*>() ; 
    int lkey = k.length(); 
    deviceKey = (char*)malloc ( sizeof(char) * (lkey +1) ); 
    strcpy(deviceKey, k.c_str());
    deviceKey[lkey] = 0 ; 
    this -> hashed = (const char*)deviceKey; 
    expiresTime = DEFEXPIRESTIME ; 
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
    for (int i = 0 ; i < allThings -> size(); i++) {
        if (allThings ->get(i) -> getNodeType() == OutputDevice) {
            return true ; 
        }
    }
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
    createRegJson();
    return regJsonString ; 
}

String IonNode :: getAdJson() {
    createAdJson() ;
    return adJsonString ; 
}

String IonNode :: processControlJson(String ctljson, bool checkForAuth){
    ctlError = "";
    DynamicJsonDocument ctlDoc(CTLSIZE);
    DeserializationError err = deserializeJson(ctlDoc, ctljson);
    
    if (err) {
        // No need to create a Json doc just to send back a known 
        // message. 
        ctlError = err.c_str(); 
        return JSON400 ; 
    } else {
        const char* checker =  ctlDoc[HDRTYPE];
        if ( strcasecmp(checker, TYPECTL) != 0 )  {
            ctlError = "Invalid message type -" + String(checker); 
            return JSON400 ;
        }
        if (checkForAuth){
            checker = ctlDoc[HDRKEY]; 
            if (strcmp(checker, hashed) != 0) 
                return JSON403;
        }

        // In the first version, we will allow only one control
        // request in each message
        JsonObject dataObj = ctlDoc[HDRDATA][0]; 
        if (dataObj.isNull()){
            ctlError = "Data object not proesent in message";
            return JSON400 ; 
        }

        checker = dataObj[HDRNAME]; 
        if (!checker) {
            ctlError ="Name not sent by controller"; 
            return JSON400 ;
        }  
        
        IonThing* thing = getThingByName(String(checker)); 
        if (!thing) {
            ctlError = "No Thing with name = [" + String(checker) + "]";
            return JSON404 ;
        } 
        JsonObject paramsObject = dataObj[HDRPARAMS];
        String tmpOutput; 
        serializeJson(paramsObject, tmpOutput);
        for(JsonPair kvp : paramsObject) 
        { 
            const char* key = kvp.key().c_str(); 
            JsonVariant value = kvp.value() ; 
            if (value.is<bool>()){
                bool bVal = value ; 
                if (!thing -> setParameterValue(key, bVal)) {
                    ctlError = ("Could not set Boolean value (" + String(bVal)  + ") for " + key); 
                    return JSON404;
                }
            /* NOTE : Check for int before you check for float
               Otherwise int value will also qualify as float and 
               bad things will happen. 
             */
            } else if (value.is<int>()) {
                int iVal = value ; 
                if (!thing -> setParameterValue(key, iVal)){
                    ctlError = ("Could not set Integer value (" + String(iVal) + ") for " + key); 
                    return JSON404;
                }
            } else if (value.is<float>()){
                float fVal = value ; 
                if (!thing -> setParameterValue(key, fVal)) {
                    ctlError = ("Could not set Float value (" + String(fVal) + ") for " + key); 
                    return JSON404;
                }
            } else if (value.is<char*>()){
                const char* sVal = value ; 
                if (!thing -> setParameterValue(key, String(sVal))) {
                    ctlError = ("Could not set String value (" + String(sVal) + ")" + " for " + key); 
                    return JSON404;
                }
            }

        }
        return String(checker); 

    }
}

void IonNode :: createRegJson(){
    if (lastRegTime == 0 ) {
        regMid = String(deviceId); 
        regMid.concat(TYPEREG); 
        regMid.concat((int)millis()/1000); 
        DynamicJsonDocument regJson(ADSIZE);
        regJson[HDRTYPE] = TYPEREG ;
        regJson[HDRVER] = VERVAL ; 
        regJson[HDRFROM] = address; 
        regJson[HDRDEVID] = (const char*)deviceId; 
        regJson[HDRKEY] = hashed; 
        regJson[HDRMID] = regMid ; 
        regJson[HDREXPIRES] = expiresTime ; 
        lastMid = regMid ; 
        regJson[HDRTIME] = (int)(millis()/1000);
        regJsonString.remove(0);
        serializeJson(regJson, regJsonString);
    }
}

void IonNode :: createAdJson() {
    if (lastAdTime == 0 ) {
        lastAdTime = millis() ; 
        DynamicJsonDocument adJson(ADSIZE);
        adJson[HDRTYPE] = TYPEADV ;
        adJson[HDRVER] = VERVAL ; 
        adJson[HDRFROM] = address; 
        adJson[HDRDEVID] = (const char*)deviceId; 
        adJson[HDRKEY] = hashed; 
        adJson[HDRMID] = regMid ; 
        bool isLocal = IonConfig::getConfiguration() -> isLocalGateway() ; 
        bool isCtrTypeAdded = false ; 
        lastMid = regMid ; 
        adJson[HDRTIME] = (int)lastAdTime/1000;
        JsonArray dataJson = adJson.createNestedArray(HDRDATA);
        for (int i = 0 ; i < allThings -> size(); i++) {
            String tmpStr; 
            const char* str1; 
            IonThing* thing = allThings -> get(i) ;
            JsonObject dataObj = dataJson.createNestedObject() ; 
            String thingName = thing -> getName() ; 
            String tag =  thing -> getTag() ; 
            if (!tag.equals("") ) {
                thingName.concat("-"); 
                thingName.concat(tag); 
            }
            //QLogger::getInstance() -> debug("creating ad json for " + thingName); 
            //dataObj[HDRNAME] = thing -> getName() ; 
            dataObj[HDRNAME] =thingName ; 
            /*
            serializeJson(dataObj, tmpStr);
            logger -> debug("After name - serialized = " + tmpStr); 
            yield() ; 
            */
            str1 = thing -> getAction(); 
            if (str1){
                dataObj[HDRACTION] = str1; 
            }
            String string1 = thing -> getLocation() ; 
            if (!string1.equals("")) {
                dataObj[HDRLOCATION] = string1; 
            }
            if (thing -> getNodeType() == SensorDevice) {
                dataObj[HDRNODETYPE] = "Sensor" ; 
            } else if (thing -> getNodeType() == OutputDevice) {
                dataObj[HDRNODETYPE] = "OutputDevice" ; 
                if (!isCtrTypeAdded)
                {
                    // The control type is for the device and not each individual
                    // device. We just need to add it once. 
                    if (isLocal){
                        adJson[HDRCONTROLMETHOD] = CONTROLMETHODDEAMON; 
                    } else {
                        adJson[HDRCONTROLMETHOD] = CONTROLMETHODPOLL; 
                    }
                    isCtrTypeAdded = true ; 
                }
                
                
            }
            dataObj[HDRCAPABILITIES] = serialized(thing -> getCapabilitiesJson()); 
            dataObj[HDRPARAMS] = serialized(thing -> getParameterDefinitionsJson());
            dataObj[HDRRETURN] = serialized(thing -> getReturnDefinitionsJson());
        }

        serializeJson(adJson, adJsonString);
        //logger -> debug("Ad string = ", adJsonString); 
        
    }  
}

String IonNode :: getCtlPollJson(){
    DynamicJsonDocument ctlJson(CTLSIZE);
    int ctime = (int)(millis()/1000); 
    lastMid = String(deviceId); 
    lastMid.concat(TYPECTLPOLL); 
    lastMid.concat(ctime); 
    ctlJson[HDRTYPE] = TYPECTLPOLL ;
    ctlJson[HDRVER] = VERVAL ; 
    ctlJson[HDRFROM] = address;
    ctlJson[HDRTIME] = ctime; 
    ctlJson[HDRDEVID] = (const char*)deviceId; 
    ctlJson[HDRKEY] = hashed; 
    ctlJson[HDRMID] = lastMid ;
    String output;
    serializeJson(ctlJson, output); 
    return output;
}

String IonNode :: getPublishJson() {
    DynamicJsonDocument adJson(ADSIZE);
    lastPubTime = millis() ; 
    lastMid = String(deviceId); 
    lastMid.concat(TYPEPUB); 
    lastMid.concat((int)millis()/1000); 
    adJson[HDRTYPE] = TYPEPUB ;
    adJson[HDRVER] = VERVAL ; 
    adJson[HDRFROM] = address; 
    adJson[HDRDEVID] = (const char*)deviceId; 
    adJson[HDRKEY] = hashed; 
    adJson[HDRMID] = lastMid ;
    adJson[HDRTIME] = (int)lastPubTime/1000;

    JsonArray dataJson = adJson.createNestedArray(HDRDATA);
    for (int i = 0 ; i < allThings -> size(); i++) {
        const char* str1; 
        IonThing* thing = allThings -> get(i) ;
        if (thing -> getNodeType() == SensorDevice)
            dataJson.add(serialized(thing -> getReturnValuesJson()));
    }
    String output; 
    serializeJson(adJson, output);
    return output; 
}


