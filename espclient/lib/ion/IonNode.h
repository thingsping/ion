#ifndef __IONNODE_H__
#define __IONNODE_H__
#include <Arduino.h>
#include "ionconstants.h"
#include "IonThing.h"
#include "LinkedList.h"
#include "ArduinoJson.h"
#include "CcshConfig.h"
#include "Log.h"

class IonNode {
public : 
    
    IonNode(String deviceid,  String key);
    ~IonNode(); 
    void setAddress(const char* addr) { this -> address = addr; }
    void setAddress(String addr){this -> address = addr.c_str();}

    /**
     * Add a IonThing to this node.  A node can have more than 
     * one entity. For example, the same node may have a temperature 
     * sensor and a smoke sensor attached to it. Although it is the same
     * device with a single microcontroller, it can perform two distinctly 
     * different tasks and will typically have two different sensors for this. 
     * To accomodate such an arrangement, the CCSH protocol allows definition of
     * multiple such 'things' connected to the same device. The Advertisement 
     * JSON for such an implementation would be : 
     * { ... "Data" : [
     *                    {  "Name" : "Temperature Sensor"  ..... }
     *                ],
     *                [
     *                    {  "Name" : "Smoke Sensor"  ..... }
     *                ]
     * }
     * 
     * @param A pointer to a IonThing object
     */
    void addThing(IonThing*);

    /**
     * Get the first thing of this entity
     * 
     * @return - the first (or only) Thing which this node contains 
     */
    IonThing* getThing() ; 

    /**
     * Get the thing at the specified index
     * 
     * @return - This node's Thing which is at the specified index
     */
    IonThing* getThing(int idx);

    IonThing* getThingByName(String name); 

    /**
     * Get the number of things which this Node contains. 
     */
    int getThingsCount();

    String processControlJson(String ctljson, bool checkForAuth=true); 

    String getRegJson();
    String getAdJson();  
    String getPublishJson() ; 
    String getControlError() {return ctlError;}
    String getCtlPollJson() ; 

    long getLastRegisteredTime(){return lastRegTime ; }
    void setLastRegisteredTime(long tm) {lastRegTime = tm;} 

    bool hasOutputDevice() ; 

private :
    String address; 
    char* deviceId;
    char* deviceKey; 
    const char* hashed; 
    String regMid;
    String lastMid;  
    LinkedList<IonThing*>* allThings ;
    long lastRegTime ; 
    long lastAdTime; 
    long lastPubTime ; 
    int expiresTime ; 

    // Note : Registration and Advertisement JSONs
    // will not change throughout the life time of this device
    // being alive. (unles you force a fresh registration with new
    // Message ID - probably unlikely). so let's keep a copy of this
    String regJsonString ; 
    String adJsonString ;

    String ctlError ; 
    QLogger* logger ; 

    void createRegJson();
    void createAdJson(); 

    void computeHash() ; 
    // void createPubJson();

}; 




#endif