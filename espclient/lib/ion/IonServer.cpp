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
         config = IonConfig :: getConfiguration() ; 
         lastPollTime = 0; 
         remotePollingPort = config -> getPollingPort() ; 

         String tmpString = "p" + config -> getDeviceId(); 
         pollString = (char*)(malloc(sizeof(char) * 14));  // 14 -> 1 + 12 + 1         
         strcpy(pollString, tmpString.c_str()); 
         pollString[13] = 0 ; 

         tmpString = "a" + config -> getDeviceId(); 
         ackString = (char*)(malloc(sizeof(char) * 14));  // 14 -> 1 + 12 + 1         
         strcpy(ackString, tmpString.c_str()); 
         ackString[13] = 0 ; 
         lastIncomingHandled = 0 ; 
         isPollAvailable = false ; 
         shouldIPoll = true ; 
         pollBeginTime = 0  ; 
         localUdpPort = UDPPOLLPORT ; 
         hasUdpBegan = false  ; 
         Udp.stop(); 
}

bool IonServer :: connectToWifi(const char* ssid, const char* ssidpwd) {
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, ssidpwd);
    long starttime = millis(); 
    while ( ( WiFi.status()  != WL_CONNECTED ) &&  (millis() - starttime < WIFITIMEOUT) )
    {
       yield() ; 
    }
    pinMode(2, OUTPUT); 
    if (WiFi.status()  != WL_CONNECTED ) {
        for (int i =0; i < 5; i++) {
          digitalWrite(ONBOARDLED, 1); 
          delay(300);
          digitalWrite(ONBOARDLED, 0); 
          delay(300); 
        }
        return false ; 
    } else {
        BoardSpecific :: setStatusLED(true) ; 
        localIp = WiFi.localIP().toString() ; 
        return true ; 
    }
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
    if (isPollAvailable){
                Udp.beginPacket(remoteaddr, remotePollingPort);
                logger -> debug("Writing ack string =" + String(ackString)); 
                Udp.print(ackString) ;

                Udp.endPacket();
                shouldIPoll = false ; // We actually have to make this to true because the 
                    // the server's poll table would have gone stale. But let's not do it now
                    // we'll wait for the command to be completed and that guy will turn this flag. 
    }
            
}

void IonServer :: handleIncoming(bool (*msgProcessor)(String)) {
    if ((millis() - lastIncomingHandled) < 100){ // Let's not do it too often 
        return ; 
    }
    lastIncomingHandled = millis() ; 
    
    if (config -> isLocalGateway())
    {
        WiFiClient client = server -> available();
        if (client) {
            BoardSpecific :: setStatusLED(false) ; 
            //logger -> debug("We have an incoming message! Let's check"); 
            client.setNoDelay(true); 
            int tStart = millis() ; 
            
            int tEnd = tStart; 
            
            String req = "";
            String payload ;
            String responsebody ; 
            String responseheaders = String(RESPONSETEMPLATE);
            payload = getPayload(client);
            payload.trim(); 
            //logger -> debug("Payload = ", payload); 
            
            responsebody = processControlHelper(payload, msgProcessor, true); 
            tEnd = millis(); 
            responseheaders.replace("%CONTENTLEN%", String(responsebody.length()));
            responseheaders.replace("%FREEMEM%", String((ESP.getFreeHeap()))) ; 
            responseheaders.replace("%TOTALTIME%", String(tEnd - tStart)) ;     
            responseheaders.replace("%UPTIME", String(tEnd/1000));
            responseheaders.concat(responsebody);
            client.println(responseheaders); 
            client.flush(); 
            client.stop(); 
        }
    } else {
        listenForPollResponses() ;
        if (isPollAvailable)
        {
            BoardSpecific :: setStatusLED(false) ; 
            isPollAvailable = false ; 
            String payload = node -> getCtlPollJson();      
            int ctime = (int)(millis()/1000);  
            //logger -> debug("Sending poll request - " + payload) ; 
            String response = sendToServer(payload);
            //logger -> debug("Received control message @" + String(ctime) + " = [", response, "]");         
            String rType =  getMessageType(response);
            if (rType.equalsIgnoreCase(TYPECTL)){                    
                String responsebody = processControlHelper(response, msgProcessor, false); 
                // /logger -> debug("Should send back status = ", responsebody);
                shouldIPoll = true ; // Now that the command has been processed, let's get ready to start checking again
                            // Remember that just before the ion server sends out the Control request in response to the 
                            // the sendserver, it would have cleared the control cache for this device. 
            } else {
                logger -> debug("Unexpected poll response = [", rType, "]; Was expecting=[", TYPECTL, "]") ; 
            }
        }
    }
    reregisterIfNeeded();
    BoardSpecific :: setStatusLED(true) ; 
}

String IonServer :: processControlHelper(String payload, bool (*callback)(String), bool checkForAuth){
    String responsebody = ""; 
    if (payload.equals("")){
        responsebody = JSON400; 
    } else {
        String result = node -> processControlJson(payload, checkForAuth);
        if (result.startsWith("{")){
            logger -> error("Process control error = " + node -> getControlError());
            responsebody = result ; 
        } else {
            bool isSuccess = (*callback)(result);
            if (isSuccess)
                responsebody = JSON200 ; 
            else 
                responsebody = JSON500; 
        }
    }
    return responsebody; 
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

void IonServer :: registerWithServer(int timeout, int attempts) {
    String payload = node -> getRegJson() ;
    int rType; 
    for (int i = 0 ; i < attempts; i++) {
        String resp =sendToServer(payload, timeout); 
        rType =  getResponseCode(resp);
        if (rType == RESPONSEOK || rType == RESPONSEFORBIDDEN || rType == RESPONSEUNAUTH) {
            break ; 
        }
        //delay(30000) ; // Wait for 30 seconds before trying again!
        //Anyways we have a long timeout and we will be trying for 3 times.
        // So no need to wait for an additional 30 seconds. 
    }
    if (rType == RESPONSEOK) {
        node -> setLastRegisteredTime(millis()); 
        payload = node -> getAdJson() ; 
        //logger->debug("Sending advertisement-" + payload);

        sendToServer(payload);
        for (int i = 0 ; i < MAXRETRIES; i++) {
            String resp =sendToServer(payload); 
            rType =  getResponseCode(resp);
            if (rType == RESPONSEACCEPTED || rType == RESPONSEFORBIDDEN || rType == RESPONSEUNAUTH) {
                break ; 
            }
            //delay(30000) ; // Wait for 30 seconds before trying again!
        }
        if (rType != RESPONSEACCEPTED){
            logger -> error("Bad response recieved while Advertising - " + String(rType));
            // What action to be taken here? let's decide.  
        }
    } else {
            logger -> error("Unknown response recieved while Registering - " + String(rType));

    }  
}

String IonServer :: sendToServer(String payload, int timeout) {  
  long t1 = millis();
  WiFiClient clientOut ;
  String resp = ""; 
  BoardSpecific :: setStatusLED(false) ; 

  bool connected = false ; 
  while (!connected && (millis() - t1) < timeout){
    connected = clientOut.connect(remoteaddr, remoteport);
    yield();
  }
  //logger -> debug("Tried to connecto to " + String(remoteaddr) + "; Connected?=" + connected); 
  if (connected)
  {
    // Simply send a plain POST request - be very very careful about the syntax
    // Apache is very unapologetic. I had an extra space between POST / and HTTP/1.1
    // and APache would send back a 400 bad request with nothing in its logs. 
    // Spent an hour almost to resolve this
    
    String msg = "POST / HTTP/1.1\r\nHost: "; 
    msg.concat(remoteaddr); 
    if (remoteport != DEFAULTPORT) {
        msg.concat(":"); 
        msg.concat(remoteport); 
    }
    msg.concat("\r\nAccept: */*"); 
    msg.concat("\r\nUser-Agent: CcshEspSender-0.1");
    msg.concat("\r\nContent-Type: application/json");
    msg.concat("\r\nX-freemem: ");
    msg.concat(String((ESP.getFreeHeap())));
    msg.concat("\r\nX-uptime: ");
    msg.concat(String(t1/1000));
    msg.concat("\r\nContent-Length: "); 
    //payload = "{\"name\" : \"god\", \"place\": \"heaven\" }" ; 
    msg.concat(payload.length());
    msg.concat("\r\n\r\n") ;
    msg.concat(payload); 

    //logger -> debug("Sending msg=", msg); 

    clientOut.println(msg);
    int elapsed = 0 ;
    resp = getPayload(clientOut); 
  } else {
      logger -> error("Could not connect to server - ", String(remoteaddr),  ":", String(remoteport) +
            "Time tried = " + String(millis() - t1)); 
  }
  BoardSpecific :: setStatusLED(true) ; 
  return resp;
}

void IonServer :: reregisterIfNeeded() {
    long prevRegTime = node -> getLastRegisteredTime() ; 
    long curTime = millis()/1000; 
    if (prevRegTime == 0) { // That is, initial registration failed!
        logger -> error ("Initial Registration attempt has failed! Server down? Keeping it quick") ; 
        registerWithServer(10000, 1) ; 
    }
    else if (prevRegTime > curTime || (curTime - prevRegTime)  >= DEFEXPIRESTIME/2) {
        registerWithServer(); 
    }
}

String IonServer :: getPayload(WiFiClient client) {
    HttpData hd = getHttpData(client); 
    return hd.payload; 
}

HttpData IonServer :: getHttpData(WiFiClient client) {
    return getHttpData(client, 30) ;
}


HttpData IonServer :: getHttpData(WiFiClient client, int timeout) {
    String req = "" ; 
    String payload = "" ;
    String headers ; 
    int avail;
    long tStart = millis() ; 
    int elapsed = 0 ; 
    
    /*
    In case we are trying to get the payload for the 
    response of an outgoing connection, then just wait till 
    data is available on the wire or till a timeout
    elapses. 
    If it is an incoming request - when this method is called 
    the client will always be available and hence this loop 
    will never be called. 
    */
    // Using client.setTimeout() didn't seem to work. So I am resorting
    // to old school method of reading bytes iteratively in the loop
    avail = client.available(); 
    while (!avail &&  elapsed < timeout*1000)
    {
        elapsed = millis() - tStart; 
        avail = client.available() ; 
        delay(10); 
    }
    /*
    if (elapsed > 15) {
        QLogger :: getInstance() -> debug ("It took ", String(elapsed),
         " millisecs before ", String(client.available()), " bytes of data was available on the wire ");
    }
    */

    // Theoritically the following loop should not be required. However I have seen that 
    // sometimes, the client.available() starts increasing slowly even after the first 
    // few bytes are 'available'. The next do-while takes care of that
    do{
        avail = client.available() ;
        delay(10);
    } while ( (avail != client.available()));
    
    if (avail) {
        int bytesToRead = avail > 2048 ? 2048 : avail ;
        char tbuffer[bytesToRead];
        client.readBytes(tbuffer, bytesToRead);
        String strTemp = String(tbuffer);
        //Don't ask why - Without the below statement, some extra junk
        // characters are read into the buffer.
        strTemp = strTemp.substring(0, bytesToRead);        
        strTemp.replace("\r\n", "\n");// Some clients like curl send "\r\n"
        req.concat(strTemp);
    }
    
    HttpMethod met ; 
    if (req.startsWith("GET ")){
        met = Get; 
    } else if (req.startsWith("POST ")){
        met = Post ;
    } else if (req.startsWith("HTTP/")) {
        met = Response ; 
    }
    else {
        QLogger :: getInstance() -> debug("Unknown method-[", req, "]"); 
    }
    String path = ""; 
    int idx = req.indexOf(" ");
    int idx2 = req.indexOf(" HTTP");
    if (idx != -1 && idx2 != -1) {
        path = req.substring(idx, idx2+1);
        path.trim(); 
    }
    idx = req.indexOf("\n\n");
    if (idx != -1) {
        headers = req.substring(0, idx+1);
        payload = req.substring(idx+1);
    }
    else {
        payload = "" ; 
    }
    HttpData data ; 
    data.payload = payload ; 
    data.path  = path; 
    data.method = met ;  

    return data ; 
}

String IonServer :: getMessageType(String jsonpayload){
    String resp ; 
    //StaticJsonDocument<400> respDoc;
    DynamicJsonDocument respDoc(CTLSIZE);

    DeserializationError err = deserializeJson(respDoc, jsonpayload);
    
    if (err) {
        resp = "" ; 
        logger -> error("Error in json response : ", String(err.c_str()), 
            ";Incoming payload=[" ,  jsonpayload + "]"); 
    } else {
        resp = respDoc[HDRTYPE].as<String>() ;   
    }
    return resp ; 
}

int IonServer :: getResponseCode(String jsonpayload){
    int resp ; 
    if(jsonpayload.equals("")) {
        resp = -1 ; 
    } else {
        String mType = getMessageType(jsonpayload);
        resp = mType.toInt() ; 
    }
    return resp ;           
}

