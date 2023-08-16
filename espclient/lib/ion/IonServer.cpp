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

#include "IonServer.h"
 
 IonServer :: IonServer(const char* addr, int port)
 {
         this -> remoteaddr = addr;
         this -> remoteport = port ; 
         logger = QLogger :: getInstance(); 
         lastPollTime = 0; 
         remotePollingPort = 41245;

         String tmpString = "p" + config -> getDeviceId(); 
         pollString = tmpString.c_str();

         tmpString = "a" + config -> getDeviceId(); 
         ackString = tmpString.c_str(); 
}

void IonServer ::begin(int port) {
    server = new WiFiServer(port); 
    server -> begin() ; 
    pinMode(2, OUTPUT); 
}

void IonServer :: listenForPollResponses() {    
    if (pollBeginTime  != 0) { // Only if we have started the polling process  

        if (!hasUdpBegan ) {
            logger -> debug ("Starting UDP daemon on port " + String(localUdpPort));
            Udp.begin(localUdpPort); 
            hasUdpBegan = true ; 
        }
        int sz =  Udp.parsePacket();
        long sttime = millis() ; 
        //Udp.setTimeout(20);
        while (sz == 0 && (millis() - sttime) < 20){
            sz = Udp.parsePacket();
        }
        if (sz){          
            char incoming = Udp.read(); 
            //logger -> debug("Incoming = " + String(incoming)); 
            isPollAvailable = (incoming == 'Y' || incoming == 'y'); 
        }
    }
    // Either if we have exceeded the mapping time specified in RFC4787 or if we have already 
    // received a response for a previous poll, we need to redo the polling stuff. 
    shouldIPoll = shouldIPoll || pollBeginTime == 0 || (millis() - pollBeginTime) > UDPMAPPINGREFRESHTIME ;

    if (shouldIPoll)
    {
        Udp.beginPacket(remoteaddr, remotePollingPort);
        Udp.print(pollString) ;
        logger -> debug("Will now poll to ", String(remoteaddr), ":", String(remotePollingPort) + 
           "[" + String(pollString) +"]; Time since last poll = " + String(millis() - pollBeginTime)); 
        Udp.endPacket();
        pollBeginTime = millis() ; 
        
        // After it sends out a POLL request, it should receive either
        // Yes or No. If it doesn't it probably means that the message has not 
        // reached the server at all. So make sure we definitely receive something 
        // immediately after sending out the poll request
        int sz =  Udp.parsePacket();
        long sttime = millis() ; 
        //Udp.setTimeout(300);
        while (sz == 0 && (millis() - sttime) < 300){
            sz = Udp.parsePacket();
        }
        if (sz){          
            char incoming = Udp.read(); 
            //logger -> debug("Incoming = " + String(incoming)); 
            if(incoming == 'Y' || incoming == 'y'){
                isPollAvailable = true ; 
            }
            shouldIPoll = false ;
        } else {
            // This means that we didn't receive anything on the 
            // wire. Which probably means that our initial message
            // didn't reach the polling server. 
            shouldIPoll = true ; 
        }
    }
            
}

void IonServer :: handleIncoming(bool (*msgProcessor)(String)) {
    
    BoardSpecific :: setStatusLED(true) ; 
}


void IonServer :: setNode(IonNode* node){
    this -> node = node ; 
    if (node -> hasOutputDevice() && config -> isLocalGateway()) {
        begin() ; 
    }
}

void IonServer :: publish() {
    reregisterIfNeeded(); // For publish reregister must be done as the
        // first step. What if there was no data to publish for more than an hour?
    if (node -> getLastRegisteredTime() == 0) {
        logger -> error(F("Registration failed! Refusing to publish!")); 
    } else {
        String payload = node -> getPublishJson(); 
        sendToServer(payload);
    }
}


