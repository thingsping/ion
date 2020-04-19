#ifndef __CCSHSERVER_H__
#define __CCSHSERVER_H__

#include "Arduino.h"
//#include <ESP8266WiFi.h>
#include "CcshConfig.h"
#include "ionconstants.h"
#include "IonNode.h"
#include "ArduinoJson.h"
#include "Log.h"
#include "BoardSpecific.h"
#include <WiFiUdp.h>

#define WIFITIMEOUT 10000
#define UDPMAPPINGREFRESHTIME (1 * 60 * 1000 - 1000) //#RFC 4787 mandates time to be alteast 2 minutes. 
                                                    // Using 1 minute and Setting this to 1 second less

struct HttpData
{
    String payload;
    String path;
    HttpMethod method; 
};

class IonServer {

public:
    IonServer(const char* addr, int port=80);
    
    static String getPayload(WiFiClient) ;
    static HttpData getHttpData(WiFiClient); 
    static HttpData getHttpData(WiFiClient, int timeout); 

    void setPort(int port) {this -> remoteport = port ; }
    bool connectToWifi(const char* ssid, const char* ssidpwd) ;
    void handleIncoming(bool (*f)(String)); 
    void setNode(IonNode* node);
    String getLocalIP() {return localIp;} ; 
    void publish() ; 
    void registerWithServer(int timeout=DEFAULTTIMEOUT, int attempts=MAXRETRIES) ; 

private: 
    WiFiServer* server;
    WiFiUDP Udp;
    IonNode* node ; 
    const char* remoteaddr ; 
    int remoteport ; 
    int remotePollingPort ; 
    String localIp ; 
    int localUdpPort ; 
    QLogger * logger ; 
    IonConfig* config ; 
    char* pollString ; 
    char* ackString ;
    bool isPollAvailable ; 
    bool hasUdpBegan; 
    bool shouldIPoll ; 
    long pollBeginTime ;
    long lastPollTime ; 
    long lastIncomingHandled ;  
    void listenForPollResponses() ; 

    String getMessageType(String jsonpayload);
    int getResponseCode(String jsonpayload);
    String sendToServer(String payload, int timeout=DEFAULTTIMEOUT);
    String processControlHelper(String payload, bool (*callback)(String), bool checkForAuth );
    void reregisterIfNeeded();
    void begin(int port = 80); 

};

#endif