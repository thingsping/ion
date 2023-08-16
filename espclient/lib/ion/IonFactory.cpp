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
#include "IonFactory.h"

IonFactory :: IonFactory() {
    server = 0 ; 
    node = 0 ; 
    addrOnly= 0  ; 
    logger = QLogger :: getInstance() ; 
    init();
}

IonFactory :: ~IonFactory() {
    if (server) 
        delete server ; 
    if (node) 
        delete node ; 
    if (addrOnly)
        free(addrOnly); 
    int sz = things_created -> size();
    for (int i =0 ; i < sz; i++){
        delete things_created -> get(i);
    }
    sz = names_created -> size();
    for (int i =0 ; i < sz; i++){
        free (names_created -> get(i));
    } 
}

void IonFactory :: saveEntities() {
    // To be implemented
}

void IonFactory :: init( ) {
       //TBI
}

Sensor IonFactory :: createSensor(const char* name) {
    String loc =configuration -> getLocation(name);
    String tag = configuration -> getTag(name) ;  
    Sensor* sr = new Sensor(name, loc);
    sr -> setTag(tag);  
    node -> addThing(sr);
    things_created -> add(sr);
    return *sr ; 
}

Actuator IonFactory :: createActuator(String name, const char* action) {
    int l = name.length() ; 
    char* new_name = (char*) (malloc (sizeof(char) * (l+1))); 
    strcpy(new_name, name.c_str()); 
    new_name[l] = 0; 
    names_created -> add(new_name); 
    return createActuator(new_name, action) ; 
}
