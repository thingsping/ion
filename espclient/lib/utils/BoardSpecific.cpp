#include "BoardSpecific.h"

 void BoardSpecific :: setStatusLED(bool state){
     if (state){
        #if defined(ESP8266)
            digitalWrite(ONBOARDLED, 0); 
        #elif defined(ESP32)
            digitalWrite(ONBOARDLED, 1);
        #endif

     } else {
        #if defined(ESP8266)
            digitalWrite(ONBOARDLED, 1); 
        #elif defined(ESP32)
            digitalWrite(ONBOARDLED, 0);
        #endif
     }

 }