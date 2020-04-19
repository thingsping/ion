#ifndef __TEXTUTILS_H__
#define __TEXTUTILS_H__
#include "Arduino.h"
#include "LinkedList.h"

struct KeyValPair {
    String key ; 
    String value ;  
    // By using String instead of const char* we don't have to worry about 
    // memory management. When KVP goes out of scope or is reassigned, this will 
    // be taken care of by the memory manager

/* 
    const char* key ; 
    const char* value ; 

    KeyValPair() {
        key = 0 ; 
        value = 0 ; 
    }
    
    ~KeyValPair() {
        if (key)
            delete[] key ; 
        if (value)
            delete[] value ; 
    }
    */
};

class TextUtils {

  public :
    static void getKeyValPair(KeyValPair &kvp, const char* fulltext, const char* key, 
        char pairsep='\n', char keyvalsep='=');

    static int listContains(LinkedList<String>* list, String search); 

};



#endif
