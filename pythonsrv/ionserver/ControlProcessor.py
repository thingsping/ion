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
__date__ = "$August 22nd, 2020 "
# Original file was HttpSender. 

import threading, time, requests, json, copy, traceback
from .constants import *
from .DBManager import DBManager
from .CredsManager import CredsManager
from .AdManager import AdManager
from .ControlData import ControlData

class ControlProcessor(threading.Thread):
    __globalctlproc = None 
    __hasstarted__ = False

    def get_processor():
      if ControlProcessor.__globalctlproc is None:
        while ControlProcessor.__hasstarted__ == True :
            time.sleep(1)
            print("Do I, the control processor realy get called? Huh! The initialization takes some time. let's wait" )        
        ControlProcessor.__globalctlproc  = ControlProcessor()
        ControlProcessor.__hasstarted__ = False 
        ControlProcessor.__globalctlproc.start()
      return ControlProcessor.__globalctlproc

    def __init__(self):
      ControlProcessor.__hasstarted__ = True    
      if (ControlProcessor.__globalctlproc is not None):
        raise ReferenceError("Do not call the constructor directly")
      super(ControlProcessor, self).__init__()
      self._admgr = AdManager.get_AdManager()
      self._pendingRequests = []       
      self._responses = {}     
      self._pendingPolls = {}      
      try :
        DBManager.dropGlobal(DB_CONTROL_POLL) # Let's start by cleaning up previous issues
      except:
        traceback.print_exc()
        pass # do nothing. we don't really care
      

    def addControlMessage(self, json, uid=None, updatefb=True, updatedb=True):
        ctldata = ControlData(json, uid, updatefb, updatedb)
        self._pendingRequests.append(ctldata)
        print("Number of pending control requests = {}".format(len(self._pendingRequests)))


    def run(self) :
      while True:
        try :
            pendingMsgs = len(self._pendingRequests)
            if (pendingMsgs > 0):
                curCtlMsg = self._pendingRequests.pop()
                curJson = curCtlMsg.getControlData()
                isupdatefb = curCtlMsg.isFbUpdateRequired()
                isupdatedb = curCtlMsg.isDbUpdateRequired()
                if isupdatedb:
                    self._admgr.addActuatorState(curJson)
                # The Type of control message is not required by the client
                ctlmethod = curJson.pop(HDR_CONTROLMETHOD)
                if ctlmethod == CONTROLMETHOD_POLL :
                    curdevid = curJson[HDR_DEVID]
                    curdevname = curJson[HDR_DATA][0][HDR_NAME]
                    print("This device {} only supports polling. will wait for poll request".format(curdevid))
                    poppers = []
                    addControlFlag = True
                    if (curdevid in self._pendingPolls):
                        alreadyPending = self._pendingPolls[curdevid]
                        for i in range(len(alreadyPending)):
                            pendname = alreadyPending[i][HDR_DATA][0][HDR_NAME]
                            if (curdevname == pendname):
                                poppers.append(i)
                        # Need to do second iteration to prevent index out of bound errors
                        for i in poppers:
                            alreadyPending.pop(i)
                            #It means that this request is a modification of 
                            # a previous pending state request and we are just 
                            # modifying the values. So need to write to the flag
                            # db. 
                            addControlFlag = False 

                        alreadyPending.append(curJson)    
                    else:
                        alreadyPending = [curJson]
                        #print("Creating new array={}".format(alreadyPending))
                    
                    self._pendingPolls[curdevid] = alreadyPending
                    if addControlFlag:
                        pdict = {}
                        pdict[DBHDR_DEVID] = curdevid 
                        # Write to the database to indicate that this device has control messages
                        # waiting - The UDP poll checker will use this. 
                        gc = DBManager.getGlobalCollection(DB_CONTROL_POLL)
                        gc.insert_one(pdict)
                else :                    
                    print("Will now send out control message - {}".format(curJson))
                    url = "http://{}".format(curJson[HDR_CONTACT])
                    
                    curUid = curCtlMsg.getUID()
                    response = requests.post(url, json=curJson)
                    response = response.json()
                    print("Response of control from {} = {}".format(url, response))


                    self._responses[curUid] = response 
                    if response[HDR_TYPE] != STATUS_OK_CODE :
                        print("Err: Could not succesfully send control message to \
                         {}. Response status = {}".format(self._url, response[HDR_TYPE]))
                         
            time.sleep(1)
        except Exception as e:
            print("Exception in ControlProcessor - {}. Will wait for one minute".format(e))
            traceback.print_exc()
            time.sleep(60)
            pass     

    def get_response(self, uid):
        if uid in self._responses :
            retString = json.dumps(self._responses.pop(uid), skipkeys=True)
            return retString
        else :
            return json.dumps({"Type" : 404, "RespClause" : "No response available"})

    def process_poll_request(self, msg):
        devid = msg[HDR_DEVID]
        reqdctl = {}
        cm = CredsManager.getCredsManager()
        isauth=False
        try :
            isauth = cm.check_device(devid, msg[HDR_KEY])
        except : 
            isauth = False
            reqdctl[HDR_TYPE] = EXCP_FORBIDDEN_CODE
        if isauth:  
            #darray = []
            #send_key= None
            if (devid in self._pendingPolls):
                allctlsfordev = self._pendingPolls[devid]                
                pdict = {}
                pdict[DBHDR_DEVID] = devid                 
                gc = DBManager.getGlobalCollection(DB_CONTROL_POLL)
                if (len(allctlsfordev) == 0):
                    # Usually means something really bad - amess up 
                    # between db.controllpoll and actual state of affairs. 
                    gc.delete_many(pdict)
                    reqdctl[HDR_TYPE] = EXCP_NOTFOUND_CODE
                else : 
                    ctlfordev = allctlsfordev.pop(0)
                    self._pendingPolls[devid] = allctlsfordev
                    if ctlfordev is not None:
                        reqdctl = ctlfordev
                    else :
                        reqdctl[HDR_TYPE] = EXCP_NOTFOUND_CODE     
                    gc.delete_one(pdict)
            else :
                reqdctl[HDR_TYPE] = EXCP_NOTFOUND_CODE
        else:
            reqdctl[HDR_TYPE] = EXCP_FORBIDDEN_CODE
        response = json.dumps(reqdctl, skipkeys=True); 
        return response

