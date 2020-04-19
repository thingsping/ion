#ifndef __ENUMHElPER_H__
#define __ENUMHElPER_H__

#include "Arduino.h"
#include "ionconstants.h"

class EnumHelper {
public : 
    static const char* getNodeTypeString(NodeType); 
    static const char* getValueTypeString(ValueType); 
    static LogLevel getLogLevel(String); 
}; 


#endif