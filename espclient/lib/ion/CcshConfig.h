#ifndef __IONCONFIG_H__
#define __IONCONFIG_H__

#include "Arduino.h"
#include "ArduinoJson.h"
#include "ionconstants.h"
#include "IonThing.h"
#include "LinkedList.h"
#include "Log.h"
#include "QMD5.h"
#if defined(ESP8266)
  #include <ESP8266WiFi.h>
#elif defined(ESP32)
  #include <WiFi.h>
#endif

class IonConfig {
public : 
    /** 
     * Get the lone instance of configuration. This is a singleton class
     * and only instance can exist globally
     */
    static IonConfig* getConfiguration() ; 
    String getLocation (const char* name); 
    String getTag(const char* name); 
    String getParamValue(const char* name, const char* key); 
    void setConfiguration(const char* contents); 
    bool isConfigValid() { return m_cfgvalid;}
    String getDeviceId(); 
    String getDeviceKey() ; 
    void setDeviceId(String id) {devId = id; }
    void setDeviceKey(String devkey) ;  
    void setSsidDetails(String ssid, String password); 
    int getLogLevel() ;
    void setLogLevel(int l) {loglevel = l;}
    String getServer() {return server; } 
    void setServer(String s) {server = s; }
    int getPollingPort(); // No set method for this - this can only be set using remote config
    bool isLocalGateway(){return isLocalGw;};
    void setLocalGateway(bool b){isLocalGw = b;}
    String getSsid() ; 
    String getSsidPassword() ; 
    bool isRegistrationMandatory(){return m_regMandatory;}
    LinkedList<ThingDetails*>* getThingsList() { return things;}
    void setTagAndLocation(int, String, String);     
    void addThing(String, String, String);
    bool isConfigEmpty(){return strcmp("", configcontents) == 0 ;}
    

private : 
    IonConfig();
    IonConfig(IonConfig const&){};             // copy constructor is private
    IonConfig& operator=(IonConfig const&){ };  // assignment operator is private
    ~IonConfig();

    static IonConfig* instance ;
    const char* configcontents ;     
    String password ; 
    String devId ; 
    String deviceKey ;
    bool isLocalGw; 
    int loglevel ;
    String server; 
    int pollingPort ; 
    String ssid ; 
    String ssidPassword ; 
    bool m_regMandatory ; 
    LinkedList<ThingDetails*>* things ; 
    QLogger * logger ; 
    bool m_cfgvalid ; 
    void convertJSONToConfig() ; 
    void reset()  ; 
    String getConfigJson(); 
    String getConfigJsonBegin();
};

#endif 