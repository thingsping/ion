#ifndef __ACTUATOR_H__
#define __ACTUATOR_H__
#include "IonThing.h"

class Actuator : public IonThing {
public :
    Actuator(const char* name, String location, const char* action) : 
          IonThing(OutputDevice, name, location)  { this -> setAction(action);}


} ;


#endif 