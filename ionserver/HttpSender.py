'''
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
 '''

__author__ = "raghu"
__date__ = "$July 1st, 2019 "

import threading, time, requests, json
from .constants import *
from .DBManager import DBManager
from .CredsManager import CredsManager
from .FirebaseManager import FirebaseManager

## This class is a misnomer. We were only using this 
## to send control messages to end points using HTTP and
## hence the name. Now it is has become more of a device "CONTROLLER"
class HttpSender(threading.Thread):

    PendingRequests = {} 

    def setParameters(self, url, json, updatefb=True):
        self._url = url 
        self._json = json 
        #print("Controller. Json=({})".format(json))
        self._responses = {}
        self._fbm = FirebaseManager.get_manager()
        self._isupdatefb = updatefb
        print("Number of pending requests = {}".format(len(HttpSender.PendingRequests)))
        

    def run(self):
        #print("Posting to {}. Payload {}".format(self._url, self._json))
        try :
            if self._json[HDR_CONTROLMETHOD] == CONTROLMETHOD_POLL :
                devid = self._json[HDR_DEVID]
                thingname = self._json[HDR_DATA][0][HDR_NAME]
                HttpSender.PendingRequests["{}.{}".format(devid, thingname)] = self._json
                print("This device {}.{} only supports polling. will wait for poll request".format(devid, thingname))
                pdict = {}
                pdict[DBHDR_DEVID] = devid 
                # Write to the database to indicate that this device has control messages
                # waiting - The UDP poll checker will use this. 
                gc = DBManager.getGlobalCollection(DB_CONTROL_POLL)
                gc.insert_one(pdict)

            else :
                self._json.pop(HDR_CONTROLMETHOD)
                #print("HTTP Sender - {}".format(self._json))
                response = requests.post(self._url, json=self._json)
                response = response.json()
                print("Response of control from {} = {}".format(self._url, response))
                self._responses[self.name] = response 
                if response[HDR_TYPE] == STATUS_OK_CODE :
                    if self._isupdatefb:
                        self._fbm.update(self._json, TYPE_CTL)
                else : 
                    print("Err: Could not succesfully send control message to {}. "\
                        "Response status = {}".format(self._url, response[HDR_TYPE]))
        except OSError as e: 
            print ("Err: Could not send control message to {}. Excpetion = {}".format(self._url, e))

    def get_response(self, name):
        if name in self._responses :
            retString = json.dumps(self._responses.pop(name), skipkeys=True)
            return retString
        else :
            return json.dumps({"Type" : 404, "RespClause" : "No response available"})

    def process_poll_request(self, msg):
        devid = msg[HDR_DEVID]
        status = {}
        status[HDR_MSGID] = msg[HDR_MSGID]
        status[HDR_TIME] = int(time.time())
        status[HDR_FROM] = get_self_address()
        status[HDR_VER] = VER_VALUE
        status[HDR_DEVID] = devid
        cm = CredsManager.getCredsManager()
        isauth = cm.check_device(devid, msg[HDR_KEY])
        if isauth:  
            darray = []
            removearray = []
            pendingcount = 0 
            for key in HttpSender.PendingRequests.keys():
                if (key.startswith("{}.".format(devid))):
                    pendingcount = pendingcount + 1
                    req = HttpSender.PendingRequests[key]
                    removearray.append(key)
                    for data in req[HDR_DATA] :
                        darray.append(data)
            for rem in removearray :
                HttpSender.PendingRequests.pop(rem)        
            if (pendingcount > 0):
                status[HDR_TYPE] = TYPE_CTL
                status[HDR_DATA] = darray
                pdict = {}
                pdict[DBHDR_DEVID] = devid 
                gc = DBManager.getGlobalCollection(DB_CONTROL_POLL)
                gc.delete_many(pdict)
            else :
                status[HDR_TYPE] = EXCP_NOTFOUND_CODE
        else:
            status[HDR_TYPE] = EXCP_FORBIDDEN_CODE
        response = json.dumps(status, skipkeys=True); 
        #print ("Returning response of {}".format(response))
        return response

