#ifndef __CCSHFACTORY_H__
#define __CCSHFACTORY_H__

#include "Log.h"
#include "IonNode.h"
#include "Sensor.h"
#include "Actuator.h"
#include "IonServer.h"
#include "ionconstants.h"
#include "LinkedList.h"
#include "CcshConfig.h"

class IonFactory {

public :
    IonFactory(); 
    ~IonFactory();
    Sensor createSensor(const char* name) ; 
    Actuator createActuator(const char* name, const char* action); 

    Actuator createActuator(String name, const char* action); 

    void run() ; 

    void setPort(int port) { server -> setPort(port);}

    void start() ; 
    void dispatch() {server -> publish();} 
    void receive(bool (*callback)(String)) 
        {server -> handleIncoming(callback);}

private : 
    IonServer* server ;
    IonNode* node ; 
    char* addrOnly ;
    IonConfig* configuration ; 
    LinkedList<IonThing*>* things_created ;
    LinkedList<char*>* names_created ; 
    QLogger * logger ; 
    void saveEntities();
    void init(); 


};
#endif 