#ifndef __SENSOR_H__
#define __SENSOR_H__
#include "IonThing.h"

class Sensor : public IonThing {
public :
    Sensor(const char* name, String location) : 
          IonThing(SensorDevice, name, location)  {}
} ;


#endif 