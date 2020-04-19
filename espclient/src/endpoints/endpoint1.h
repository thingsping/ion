#ifndef __BLINK_H__
#define __BLINK_H__

#include "Log.h"
#include "Actuator.h"
#include "Sensor.h"
#include "IonNode.h"
#include "IonServer.h"
#include "IonFactory.h"

extern void endpoint_setup() {
    QLogger :: getInstance() -> setLevel(QLogger ::LEVEL_DEBUG);
    Actuator* act1;
    Sensor* sens1;
    IonNode* node1; 
    IonServer* srv1;
    IonFactory* factory1;
    Serial.begin(9600);
    pinMode(D4,OUTPUT);
}

extern void endpoint_loop() {  
  digitalWrite(D4, 0); 
  delay(500);
  digitalWrite(D4,1); 
  delay(500);
  Serial.println("Finished blinking...");

}

#endif