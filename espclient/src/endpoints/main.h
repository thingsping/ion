
#ifndef __MAIN_ENDPOINTS_H__
#define __MAIN_ENDPOINTS_H__

/* 
*  IMPORTANT - README FIRST
*  In the following lines, retain the #include for ONE and ONLY ONE 
*  end point implementation when you compile the code and build the firmware
*  Inside each .h file, there should be atleast two methods :
*      main_h_setup()  AND
*      main_h_loop() 
*  In these libraries you should put in the code that you would normally put in the 
*  loop() method and setup() method respectively of the Arduino code. 
*/

//#include "endpoint1.h"
#include "actuator_simulator.h"
//#include "endpoint2.h"
//...
//#include "endpointN.h"

extern void main_h_setup() {
  endpoint_setup() ;
}

extern void main_h_loop() {
  endpoint_loop() ;
}

#endif
