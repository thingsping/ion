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
#include "IonThing.h"

IonThing :: IonThing(NodeType nt, const char* name, String loc) {
    init(nt, name, loc); 
}

IonThing :: ~IonThing() {
    //Lets do the honours of destruction here. 

}


void IonThing :: init(NodeType nt, const char* name, String loc) {
    this -> nType = nt ; 
    this -> thingname = name ; 
    this -> location = loc; 
    this -> thingtag = "" ; 
    areParametersObjects = true ; 
    this -> action = 0 ; 
    capabilities = new LinkedList<const char*>();
    parameters_array = 0 ; 
    parameter_names = 0 ; 
    parameter_types = 0 ; 
    parameter_values = 0 ; 
    logger = QLogger :: getInstance(); 

    returnNames = new LinkedList<const char*>();
    returnTypes = new LinkedList<ValueType>();
    returnVariables = new LinkedList<void*>();

    paramNames = new LinkedList<const char*>();
    paramTypes = new LinkedList<ValueType>();
    paramVariables = new LinkedList<void*>() ; 
}

void IonThing :: setAction(const char* action) {
    this -> action = action ; 
}

void IonThing :: addCapability(const char* capability) {
    capabilities -> add(capability);
}

void IonThing :: setMultipleParameters(bool areMulti) {
    areParametersObjects = areMulti; 
}

void IonThing :: defineParameters(const char** arr, int size) {
    parameters_array = arr;
    //parameter_count = size ;
}

void IonThing :: addReturnDefinition(const char* name, ValueType valtype, 
        void* returnVariable) {    
    returnNames -> add(name); 
    returnTypes -> add(valtype); 
    returnVariables -> add(returnVariable);
}

void IonThing :: addParameterDefinition(const char* name, ValueType valtype, 
        void* paramVariable){
    paramNames -> add(name); 
    paramTypes -> add(valtype); 
    paramVariables -> add(paramVariable); 

}

bool IonThing :: setParameterValue(const char* skey, bool value){
    int idx = findString(paramNames, skey);
    bool isSuccess = false ; 
    if(idx >= 0){
        isSuccess = paramTypes -> get(idx) == Boolean ; 
        if (isSuccess){
            void* v1 = paramVariables -> get(idx);
            *((bool*)v1) = value ; 
        }
    } else {
        logger -> error("Error while setting for ", String(idx), "; [", String(skey) + "]"); 
    }
    return isSuccess ; 
}


bool IonThing :: setParameterValue(const char* skey, int value){
    int idx = findString(paramNames, skey);
    bool isSuccess = false ; 
    if(idx >= 0){
        isSuccess = (paramTypes -> get(idx) == Int) ||
                (paramTypes -> get(idx) == Float) ; 
        if (isSuccess){
            void* v1 = paramVariables -> get(idx);
            *((int*)v1) = value ; 
        } 
    } 
    return isSuccess ; 
}
bool IonThing :: setParameterValue(const char* skey, float value){
    int idx = findString(paramNames, skey);
    bool isSuccess = false ; 
    if(idx >= 0){
        isSuccess = paramTypes -> get(idx) == Float ; 
        if (isSuccess){
            void* v1 = paramVariables -> get(idx);
            *((float*)v1) = value ; 
        } else {
            isSuccess = paramTypes -> get(idx) == Int ;
            // The server sometimes sends out ints as floats. Let's
            // take care of that
            if (isSuccess){
                void* v1 = paramVariables -> get(idx);
                *((int*)v1) = value ; 
            }
        }
    } 
    return isSuccess ; 
} 
bool IonThing :: setParameterValue(const char* skey, String value){
    int idx = findString(paramNames, skey);
    bool isSuccess = false ;  
    if(idx >= 0){
        isSuccess = paramTypes -> get(idx) == Str ; 
        if (isSuccess){
            void* v1 = paramVariables -> get(idx);
            *((String*)v1) = value ; 
        }
    } 
    return isSuccess ; 
}

String IonThing :: getParameterDefinitionsJson() {
    String params ; 
    if (areParametersObjects) {
        params = "{"; 
        int parameter_count = paramNames -> size() ; 
        for (int i = 0 ; i < parameter_count; i++ ) {
            if (i != 0 ){
                params.concat(",");
            }
            params.concat("\""); 
            params.concat (paramNames ->get(i));
            params.concat("\":\"");
            params.concat(EnumHelper :: getValueTypeString(paramTypes->get(i)));
            params.concat("\"");
        }
        params.concat("}");
    } else {
        params = "["; 
        int parameter_count = 0 ; // Need to find a better way for ths
        for (int i = 0 ; i < parameter_count; i++ ) {
            if (i != 0 ){
                params.concat(",");
            }
            params.concat("\"");
            params.concat(parameters_array[i]);
            params.concat("\""); 
        }
        params.concat("]");

    }
    return params ; 
}

String IonThing :: getParameterValuesJson() {
    String params ; 
    if (areParametersObjects) {
        params = "{"; 
        int parameter_count = paramNames -> size(); 
        for (int i = 0 ; i < parameter_count; i++ ) {
            if (i != 0 ){
                params.concat(",");
            }
            params.concat("\"");
            params.concat(paramNames -> get(i));
            params.concat("\":");
            ValueType pt = paramTypes -> get(i); 
            void* v1 = paramVariables -> get(i);

            if (pt == Int ){
                int pv = *((int *)v1);
                params.concat(pv); 
            } else if (pt == Boolean) {
                int pv = *((int *)v1) ; 
                params.concat(pv ? "true" : "false" ); 
            } else if (pt == Float) {
                float pv = *((float*)v1); 
                params.concat(pv); 
            } 
            else if (pt == Str) {
                String pv = *((String*)v1);
                params.concat("\""); 
                params.concat(pv) ;
                params.concat("\""); 
            }
        }
        params.concat("}");
    } else {
        params = "["; 
        int parameter_count = 0 ; // Have to fix this.
        for (int i = 0 ; i < parameter_count; i++ ) {
            if (i != 0 ){
                params.concat(",");
            }
            params.concat("\"");
            params.concat(parameters_array[i]);
            params.concat("\""); 
        }
        params.concat("]");

    }
    return params ; 
}

String IonThing :: getReturnValuesJson() {
    String retJson = "{\"" ; 
    retJson.concat(HDRNAME); 
    retJson.concat("\":\""); 
    retJson.concat(thingname); 
    if (!thingtag.equals("")) {
        retJson.concat("-"); 
        retJson.concat(thingtag); 
    }
    retJson.concat("\"");
    int return_count = returnNames -> size(); 
    for (int i = 0 ; i < return_count; i++ ) {
        retJson.concat(",");
        retJson.concat("\"");
        //retJson.concat(return_names[i]); 
        retJson.concat(returnNames -> get(i));
        retJson.concat("\":");
        //ValueType rt = return_types[i]; 
        //void* v1 = return_values[i];

        ValueType rt = returnTypes -> get(i);
        void* v1 = returnVariables -> get(i); 

        if (rt == Int ){
            int pv = *((int *)v1);
            retJson.concat(pv); 
        } else if (rt == Boolean) {
            int pv = *((int *)v1) ; 
            retJson.concat(pv ? "true" : "false" ); 
        } 
        else if (rt == Float) {
            float pv = *((float *)v1);
            retJson.concat(pv) ; 
        } else if (rt == Str) {
            String pv = *((String*)v1);
            retJson.concat("\""); 
            retJson.concat(pv) ;
            retJson.concat("\""); 
        }
    }
    retJson.concat("}");
    return retJson; 
}

String IonThing :: getReturnDefinitionsJson() {
    String retDefs ; 
    retDefs = "{"; 
    int return_count = returnNames->size(); 
    for (int i = 0 ; i < return_count; i++ ) {
        if (i != 0 ){
            retDefs.concat(",");
        }
        retDefs.concat("\"");
        //retDefs.concat(return_names[i]); 
        retDefs.concat(returnNames -> get(i));
        retDefs.concat("\":\"");
        //retDefs.concat(EnumHelper :: getValueTypeString(return_types[i]));
        retDefs.concat(EnumHelper :: getValueTypeString(returnTypes -> get(i)));
        retDefs.concat("\"");
    }
    retDefs.concat("}");
    return retDefs ; 
}

String IonThing :: getCapabilitiesJson() {
    String cap = "["; 
    for (int i = 0; i<capabilities -> size(); i++) {
        if (i != 0) {
            cap.concat(",");
        }
        cap.concat("\""); 
        cap.concat(capabilities -> get(i)); 
        cap.concat("\""); 
    }
    cap.concat("]");
    return cap; 
}

////////////////////////////////
/// Utility/Helper methods
////////////////////////////////

void IonThing :: addEmptyItemsToList(LinkedList<void*>* list, int idx){
    int sz = list -> size() ; 
    if (sz < idx) {
        for (int i = sz; i < idx; i++){
            list -> add(0); 
        }
    }
}

int IonThing :: findString(LinkedList<const char*>* list, const char* search){
    
    for (int i = 0 ; i < list -> size(); i++){
        if (strcmp(list->get(i), search) == 0){
            return i ; 
        }
    }
    return -1; 
}


String IonThing :: getDebugString() {
    String str(" ------ Parameters ---------\n") ; 
    str.concat(getParameterValuesJson());
    str.concat("\n--- Return Values --- \n "); 
    str.concat(getReturnValuesJson());
    str.concat("\n");

    return str; 
}   

