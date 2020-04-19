#include "textutils.h"


void TextUtils :: getKeyValPair(KeyValPair &kvp, const char* fulltext, const char* key, 
    char pairsep, char keyvalsep) {
    String txtAsString = fulltext; 
    String valString = ""; 
    int idx = txtAsString.indexOf(key); 
    
    if (idx != -1 ) {
      valString = txtAsString.substring(idx); 
      idx = valString.indexOf(pairsep); 
      if (idx != -1) {
          valString = valString.substring(0, idx); 
      }
      idx = valString.indexOf(keyvalsep);
      if (idx != -1) {
          valString = valString.substring(idx+1); 
      }else {
          valString = ""; 
      }
    }
    kvp.key = key ; 
    kvp.value = valString; 
} 

int TextUtils :: listContains(LinkedList<String>* list, String search) {
    int sz = list -> size() ;
    int found = -1 ; 
    for (int i = 0 ; i < sz; i++){
        String s  = list -> get(i); 
        if (s.equals(search)){
            found = i ; 
            break ;  
        }
        yield() ; 
    }
    return found ; 
}