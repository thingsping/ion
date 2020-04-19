#ifndef __SENSOR_SIMULATOR_H__
#define __SENSOR_SIMULATOR_H__

#include "CcshConfig.h"
#include "Log.h"
#include "IonFactory.h"

/* 
* Set the following lines to match your environment details 
* and then uncomment the following lines 
* TIP : You may also set these values in the platformio.ini file
#define MYSSID  "homerouter"
#define MYSSIDPWD "home123"
#define IONSERVER 10.1.1.1:5000
*/
#define DEVICEKEY "2cf4test!@#"

float temperature = 20; 
float humidity = 40; 

IonFactory * factory;
IonConfig * config ; 
QLogger * logger ; 

void readDHT(float* temp, float* hum){
    static int ctr = 1 ; 
    int i = ctr % 22 ; 
    *temp = 20 + i/2 ; 
    *hum = 43 + i ; 
    ctr++;
}

extern void endpoint_setup() {    
    logger = QLogger :: getInstance() ; 
    logger -> setLevel(QLogger :: LEVEL_DEBUG); 
    config = IonConfig :: getConfiguration() ;
    config -> setServer(IONSERVER); 
    config -> setSsidDetails(MYSSID, MYSSIDPWD); 
    config -> setDeviceKey(DEVICEKEY);

    config -> addThing("DHT1", "Bedroom", "");
    factory = new IonFactory() ; 
    Sensor dhtSimulator = factory -> createSensor("DHT1"); 
    dhtSimulator.addReturnDefinition("Temperature", &temperature); 
    dhtSimulator.addReturnDefinition("Humidity", &humidity); 
    factory -> run();
}

extern void endpoint_loop() {
    readDHT(&temperature, &humidity); // This will be the actual 
            // procedure to read from the sensors. 
    logger -> debug("Completed reading DHT . t=" + String(temperature) + 
        "; h=" + String(humidity)); 
    factory -> dispatch() ; 
    logger ->  debug("Finished dispatching..."); 
    delay(10000);
}

#endif 