#ifndef __CCSHTHING_H__
#define __CCSHTHING_H__

#include "Arduino.h"
#include "ionconstants.h"
#include "EnumHelper.h"
#include "LinkedList.h"
#include "Log.h"


// This structure is used to denote a minimal 'attribute' 
// subset of the IonThing class. Used in configuration
struct ThingDetails {
    String name;
    String location;
    String tag ; 
    LinkedList<String>* keys = 0 ; 
    LinkedList<String>* vals = 0 ; 

    ThingDetails(String n, String l, String t) {
        name = n; 
        location = l ;
        tag = t; 
    }

    
};

class IonThing {

public : 
    
    ~IonThing(); 

    // void setLocation(const char* loc) {this -> location = loc ; } 
    void addCapability(const char* );

    /**
     * Set if the entity just accepts a string which is 'one' of predefined list
     * or a multiple parameters. By default entities can accept multiple parameters
     * @param A boolean value that dictates if the entity accepts multiple parameters
     * or just one. 
     * 
     * There are two types of parameters. 
     * 
     * a) One in which the value is one of several c strings. 
     *  An example of the JSON value for such an entity using this kind of 
     *  parameters is 
     * {  ...... "Data" : { .... "Parameters" : ["ON", "OFF"] } }
     * 
     * b) The entity accepts multiple named parameters. Example Json for such an 
     * entity is
     * {  ...... "Data" : { .... "Parameters" : 
     *     {"SoundTrack" : "MySong.mp3", "Volume" : 12} }  ....}
     */
    void setMultipleParameters(bool areMulti); 

    /**
     *  Define the possible parameter values for this entity.  Parameters are
     *  typically used by Output devices like relays and actuators.
     *  This can only be  called if the setMultipleParameters() has been 
     *  set to False.
     *  @param values An array of c-strings representing the allowed values for 
     *  parameters. 
     *   
     * 
     *  @see setMultipleParameters
     */
    void defineParameters(const char**, int size) ; 
    
    const char* getName() {return thingname;}
    String getLocation() {return location;}
    String getTag() {return thingtag; }
    void setTag(String t) {this -> thingtag = t; } 

    /**
     * Get a JSON String representing the capabilities. 
     * This string will be used in the JSon Serializer of the CcshNode class. 
     * It becomes a lot simpler for the Node class to use the 'Json'ified 
     * string rather than trying to construct the json object itself. 
     */
    String getCapabilitiesJson(); 
    NodeType getNodeType() {return nType; } 

    const char* getAction() { return action; }
    /**
     * Get a JSON String representing the parameters for this 'thing'
     * 
     */
    String getParameterValuesJson() ; 
    String getParameterDefinitionsJson() ; 

    /**
     * Get a JSON String representing the return value for this 'thing'
     * 
     */
    String getReturnValuesJson() ; 
    String getReturnDefinitionsJson() ; 

     /**
     * Add a set of items to the return values - The name for this return value
     * and the Variables holding the return value. An example of  
     *  the JSON value of a Music Player is 
     *  { ........"Data" : {  ..........   
     *     "SoundTrack" : "String", "Volume" : "Int"
     *     } ..... } ... }
     * 
     *  @param Name of the return tyoe 
     *  (in the above example, "SoundTrack" and "Volume")
     *  @param Value type for the item returned. 
     *  Type has to be one of the values defined in the ValueType enumeration.
     *  @param The variable into which the value for this return item will be stored
     *  This value will typically be declared in the global scope by the developer.
     *  When (s)he makes any change in the code and sets this variable's value, 
     *  the library will know how to automatically pickup this value and send it to 
     *  the infrastructure. 
     *  Let's say that the job of this entity is to measure Temperature. 
     *  The main sketch defines a String variable, say, 
     *       float temperature; 
     *  and passes the address of the variable to this method. 
     *  
     * 
     *  When the entity keeps measuring the temperature, it needs to just set the 
     *  value of the variable in its own program. It has to worry about 
     *  NOTHING ELSE. 
     *  It then has to notify the Ccsh Server that the data is ready to send
     *  The Ccsh Server does all the dirty work of constructing the proper JSON
     *  stream and sending it across. 
     * 
    */
    void addReturnDefinition(const char* name, ValueType valtype, 
        void* returnVariable);
     /**
      * A developer friendly overload for the @see addReturnDefinition(const char*, ValueType, void*)
      * method. 
     * Add an int return variable with name . For example say that this 'Thing' 
     * measures the light level
     *  A part of the JSON for this Sensor is 
     *  { ........"Data" : {  ..........   
     *     "LightLevel" : "Int"
     *     } ..... } ... }
     * 
     *  @param Name of the return tyoe 
     *  (in the above example, "LightLevel")
     * 
     *  @param The variable into which the value for this return item will be stored
     *  This value will typically be declared in the global scope by the developer.
     *  When (s)he makes any change in the code and sets this variable's value, 
     *  the library will know how to automatically pickup this value and send it to 
     *  the infrastructure. 
     * 
     *   In case of the above example, the developer would first define an int 
     *   variable, 
     *        int level ; 
     *   right at the beginning of the sketch - even before the setup() method 
     *   When the sensor keeps measuring the value, it simply keeps updating the
     *   variable. It has to worry about NOTHING ELSE. 
     *  It then has to notify the Ccsh Server that the data is ready to send
     *  The Ccsh Server does all the dirty work of constructing the proper JSON
     *  stream and sending it across. 
     * 
    */
    void addReturnDefinition(const char* name, int* returnVariable) 
        { addReturnDefinition(name, Int, (void*)returnVariable);}

    /**
      * A developer friendly overload for the @see addReturnDefinition(const char*, ValueType, void*)
      * method. 
     * Add an boolean return variable with name . For example say that this 'Thing' 
     * checks for motion. 
     *  A part of the JSON for this Sensor is 
     *  { ........"Data" : {  ..........   
     *     "Is there motion?" : "Bool"
     *     } ..... } ... }
     * 
     *  @param Name of the return tyoe 
     *  (in the above example, "Is there motion?")
     * 
     *  @param The variable into which the value for this return item will be stored
     *  This value will typically be declared in the global scope by the developer.
     *  When (s)he makes any change in the code and sets this variable's value, 
     *  the library will know how to automatically pickup this value and send it to 
     *  the infrastructure. 
     * 
     *   In case of the above example, the developer would first define an int 
     *   variable, 
     *        bool isMotion ; 
     *   right at the beginning of the sketch - even before the setup() method 
     *   When the sensor keeps measuring the value, it simply keeps updating the
     *   variable. It has to worry about NOTHING ELSE. 
     *  It then has to notify the Ccsh Server that the data is ready to send
     *  The Ccsh Server does all the dirty work of constructing the proper JSON
     *  stream and sending it across. 
     * 
    */        
    void addReturnDefinition(const char* name, bool* returnVariable)
        { addReturnDefinition(name, Boolean, (void*)returnVariable);}

    /**
      * A developer friendly overload for the @see addReturnDefinition(const char*, ValueType, void*)
      * method. 
     * Add a float return variable with name . For example say that this 'Thing' 
     * measures temperature and humidity 
     *  A part of the JSON for this Sensor is 
     *  { ........"Data" : {  ..........   
     *     "Temperature" : "Float", "Humidity" : "Float" 
     *     } ..... } ... }
     * 
     *  @param Name of the return tyoe 
     *  (in the above example, could either be "Temperature" or "Humidity")
     * 
     *  @param The variable into which the value for this return item will be stored
     *  This value will typically be declared in the global scope by the developer.
     *  When (s)he makes any change in the code and sets this variable's value, 
     *  the library will know how to automatically pickup this value and send it to 
     *  the infrastructure. 
     * 
     *   In case of the above example, the developer would first define two float 
     *   variables, 
     *        float temperature;
     *        float humidity ;  
     *   right at the beginning of the sketch - even before the setup() method 
     *  
     *   After that it would call this method twice - 
     *       addReturnDefinition("Temperature", &temperature); 
     *       addReturnDefinition("Humidity", &humidity);
     * 
     *   When the sensor keeps measuring the value, it simply keeps updating the
     *   variable. It has to worry about NOTHING ELSE. 
     *  It then has to notify the Ccsh Server that the data is ready to send
     *  The Ccsh Server does all the dirty work of constructing the proper JSON
     *  stream and sending it across. 
     * 
    */
    void addReturnDefinition(const char* name, float* returnVariable)
        { addReturnDefinition(name, Float, (void*)returnVariable);}   

    /**
     * A developer friendly overload for the @see addReturnDefinition(const char*, ValueType, void*)
     * method. 
     * Add a String return variable with name . For example say that this 'Thing' 
     * is a smart camera that can detect known faces. 
     *  A part of the JSON for this Sensor is 
     *  { ........"Data" : {  ..........   
     *     "Persom" : "String"
     *     } ..... } ... }
     * 
     *  @param Name of the return tyoe 
     *  (in the above example,  "Person")
     * 
     *  @param The String variable into which the value for this return item 
     *  will be stored. This value will typically be declared in the global 
     *  scope by the developer. When (s)he makes any change in the code and  
     *  sets this variable's value, the library will know how to automatically 
     *  pickup this value and send it to the infrastructure. 
     * 
     *   In case of the above example, the developer would first define a String 
     *   variable, 
     *        String person; 
     *   right at the beginning of the sketch - even before the setup() method 
     *  
     *   After that it would call this method
     *       addReturnDefinition("Str", &person); 
     * 
     *   When the camera finds known people it simply keeps updating the
     *   variable. It then has to notify the Ccsh Server that the data is ready 
     *   to send. It has to worry about NOTHING ELSE. 
     *  The Ccsh Server does all the dirty work of constructing the proper JSON
     *  stream and sending it across. 
     * 
    */
    void addReturnDefinition(const char* name, String* returnVariable)
        { addReturnDefinition(name, Str, (void*)returnVariable);}
   

    /**
     * Add details about a parameter - The name for this parameter 
     * and the Variable holding the parameter value. 
     * 
     * Typically Return values are for sensors while Parameters are 
     * for Actuators and other output devices. 
     * 
     * An example of  
     *  the JSON value of an LCD Display 
     *  { ........"Data" : {  ..........   
     *     "Message" : "String", "Brightness" : "Int"
     *     } ..... } ... }
     * 
     *  @param Name of the return tyoe 
     *  (in the above example, "Message" and "Brightness")
     *  @param Value type for the item returned. 
     *  Type has to be one of the values defined in the ValueType enumeration.
     *  @param The variable into which the value for this return item will be stored
     *  This value will typically be declared in the global scope by the developer.
     *  When (s)he makes any change in the code and sets this variable's value, 
     *  the library will know how to automatically pickup this value and send it to 
     *  the infrastructure. 
     *  Let's say that the job of this entity is to display Text. 
     *  The main sketch defines a String variable, say, 
     *       String dispText; 
     *  and passes the address of the variable to this method. 
     *  
     *  When the Ccsh Server recieves a command (over the network) to display 
     *  text, it simply sets the value of this variable to the appropriate 
     *  value. The entity can read this value and display the text. 
     *  It has to worry about NOTHING ELSE. 
     *  It then has to notify the Ccsh Server that the data is ready to send
     *  The Ccsh Server does all the dirty work of constructing the proper JSON
     *  stream and sending it across. 
     * 
    */
    void addParameterDefinition(const char* name, ValueType valtype, 
        void* paramVariable);

    /**
     * Add an int parameter to the set of parameters accepted by this 
     * entity 
     * 
     * This is a developer friendly overloaded form of the 
     * @see addParameterDefinition(const char*, ValueType, void*)
     * In this case, there is no need to explicitly pass the ValueType
     * argument. 
     * 
     * Typically Parameters are for Actuators and other output devices. 
     * 
     * An example of  
     *  the JSON value of a Fan whose speed can be controlled is  
     *  { ........"Data" : {  .......... 
     *      "Speed" : "Int"
     *  } ..... } ... }
     * 
     *  @param Name of the return tyoe 
     *  (in the above example, "Speed" )
     *  @param The variable into which the value for this return item will be stored
     *  This value will typically be declared in the global scope by the developer.
     *  When (s)he makes any change in the code and sets this variable's value, 
     *  the library will know how to automatically pickup this value and send it to 
     *  the infrastructure. 
     *  Let's say that the job of this entity is to display Text. 
     *  The main sketch defines a String variable, say, 
     *       int speed; 
     *  and passes the address of the variable to this method. 
     *  
     *  When the Ccsh Server recieves a command (over the network) to change  
     *  speed, it simply sets the value of this variable to the appropriate 
     *  value. The entity can read this value and display the text. 
     *  It has to worry about NOTHING ELSE. 
     *  It then has to notify the Ccsh Server that the data is ready to send
     *  The Ccsh Server does all the dirty work of constructing the proper JSON
     *  stream and sending it across. 
     * 
    */
    void addParameterDefinition(const char* name, int* returnVariable) {
        addParameterDefinition(name, Int, (void*)returnVariable);}

    /**
     * Add an boolean parameter to the set of parameters accepted by this 
     * entity 
     * 
     * This is a developer friendly overloaded form of the 
     * @see addParameterDefinition(const char*, ValueType, void*)
     * In this case, there is no need to explicitly pass the ValueType
     * argument. 
     * 
     * Typically Parameters are for Actuators and other output devices. 
     * 
     * An example of  
     *  the JSON value of a Switch that can be turned on or off is
     *  { ........"Data" : {  .......... 
     *      "Switch" : "Boolean"
     *  } ..... } ... }
     * 
     *  @param Name of the return tyoe 
     *  (in the above example, "Switch" )
     *  @param The variable into which the value for this return item will be stored
     *  This value will typically be declared in the global scope by the developer.
     *  When (s)he makes any change in the code and sets this variable's value, 
     *  the library will know how to automatically pickup this value and send it to 
     *  the infrastructure. 
     * 
     *  The main sketch defines a String variable, say, 
     *       bool state; 
     *  and passes the address of the variable to this method. 
     *  
     *  When the Ccsh Server recieves a command (over the network) to change  
     *  speed, it simply sets the value of this variable to the appropriate 
     *  value. The entity can read this value and display the text. 
     *  It has to worry about NOTHING ELSE. 
     *  It then has to notify the Ccsh Server that the data is ready to send
     *  The Ccsh Server does all the dirty work of constructing the proper JSON
     *  stream and sending it across. 
     * 
    */
    void addParameterDefinition(const char* name, bool* returnVariable){
        addParameterDefinition(name, Boolean, (void*)returnVariable);}

    /**
     * Add a String parameter to the set of parameters accepted by this 
     * entity 
     * 
     * This is a developer friendly overloaded form of the 
     * @see addParameterDefinition(const char*, ValueType, void*)
     * In this case, there is no need to explicitly pass the ValueType
     * argument. 
     * 
     * Typically Parameters are for Actuators and other output devices. 
     * 
     * An example of  
     *  the JSON value of an LCD Display is 
     *  { ........"Data" : {  .......... 
     *      "Display" : "Str"
     *  } ..... } ... }
     * 
     *  @param Name of the return tyoe 
     *  (in the above example, "Switch" )
     *  @param The variable into which the value for this return item will be stored
     *  This value will typically be declared in the global scope by the developer.
     *  When (s)he makes any change in the code and sets this variable's value, 
     *  the library will know how to automatically pickup this value and send it to 
     *  the infrastructure. 
     * 
     *  The main sketch defines a String variable, say, 
     *       String displayText; 
     *  and passes the address of the variable to this method. 
     *  
     *  When the Ccsh Server recieves a command (over the network) to display  
     *  text, it simply sets the value of this variable to the appropriate 
     *  value. The entity can read this value and display the text. 
     *  It has to worry about NOTHING ELSE. 
     *  It then has to notify the Ccsh Server that the data is ready to send
     *  The Ccsh Server does all the dirty work of constructing the proper JSON
     *  stream and sending it across. 
     * 
    */    
    void addParameterDefinition(const char* name, String* returnVariable){
        addParameterDefinition(name, Str, (void*)returnVariable);}

    /**
     * Add a float parameter to the set of parameters accepted by this 
     * entity 
     * 
     * This is a developer friendly overloaded form of the 
     * @see addParameterDefinition(const char*, ValueType, void*)
     * In this case, there is no need to explicitly pass the ValueType
     * argument. 
     * 
     * Typically Parameters are for Actuators and other output devices. 
     * 
     * An example of  
     *  the JSON value of a highly sensitive music player is 
     *  { ........"Data" : {  .......... 
     *      "Soundtrack" : "Str", "Volume", "Float"
     *  } ..... } ... }
     * 
     *  @param Name of the return tyoe 
     *  (in the above example, "Volume" )
     *  @param The variable into which the value for this return item will be stored
     *  This value will typically be declared in the global scope by the developer.
     *  When (s)he makes any change in the code and sets this variable's value, 
     *  the library will know how to automatically pickup this value and send it to 
     *  the infrastructure. 
     * 
     *  The main sketch defines a float variable, say, 
     *       float volume; 
     *  and passes the address of the variable to this method. 
     *  
     *  When the Ccsh Server recieves a command (over the network) to display  
     *  text, it simply sets the value of this variable to the appropriate 
     *  value. The entity can read this value and display the text. 
     *  It has to worry about NOTHING ELSE. 
     *  It then has to notify the Ccsh Server that the data is ready to send
     *  The Ccsh Server does all the dirty work of constructing the proper JSON
     *  stream and sending it across. 
     * 
    */  
    void addParameterDefinition(const char* name, float* returnVariable){
        addParameterDefinition(name, Float, (void*)returnVariable);}

    bool setParameterValue(const char*, bool); 
    bool setParameterValue(const char*, int ); 
    bool setParameterValue(const char*, float ); 
    bool setParameterValue(const char*, String ); 

    String getDebugString() ; 

protected : 
    IonThing(NodeType nt, const char* name, String location);
    // Only a subclass of the type OutputDevice can 
    void setAction(const char* action) ; 

private : 
    NodeType nType ; 
    const char* thingname ; 
    const char* action ; 
    String location ;
    String thingtag ; 
    LinkedList<const char*>* capabilities;

    // Let's uncomplicate. Instead of allowing the program to decide whether 
    // the parameters is an array or a dictionary , we'll specify this 
    bool areParametersObjects ; 


    const char** parameters_array ; 
    const char** parameter_names ; 
    const ValueType* parameter_types ; 
    void** parameter_values ; 
    const char* singleParam ;// only valid if areParametersObjects is false. 

    const char** return_names ; 
    const ValueType* return_types ; 
    void** return_values; 
    QLogger * logger ; 
    
    LinkedList<const char*>* returnNames ; 
    LinkedList<ValueType>* returnTypes ; 
    LinkedList<void*>* returnVariables ; 

    LinkedList<const char*>* paramNames ; 
    LinkedList<ValueType>* paramTypes ;  
    LinkedList<void*>* paramVariables ; 

    void init(NodeType nt, const char* name, String loc); 
    int findString(LinkedList<const char*>*, const char*); 
    int findString(const char* list[], const char* str);
    void addEmptyItemsToList(LinkedList<void*>* list, int idx);



};
#endif