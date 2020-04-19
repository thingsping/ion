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
#include "EnumHelper.h"

const char* EnumHelper :: getValueTypeString(ValueType vt){
    if (vt == Boolean) 
        return "Boolean"; 
    else if(vt == Int) 
        return "Integer"; 
    else if (vt == Float) 
        return "Float";
    else if (vt == Str) 
        return "String"; 
    else 
        return "Unknown";
}


LogLevel EnumHelper::getLogLevel(String s){
    if (s.equalsIgnoreCase("INFO")) {
        return LevelInfolog; 
    } else if (s.equalsIgnoreCase("DEBUG")){
        return LevelDebuglog ; 
    } else if (s.equalsIgnoreCase("ERROR")) {
        return LevelErrlog; 
    } else if (s.equalsIgnoreCase("INFO")) {
        return LevelInfolog; 
    }
    return LevelNoLogging; 
} 