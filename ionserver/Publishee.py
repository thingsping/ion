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
__date__ = "$June 25, 2019"

from .constants import * 
from .DBManager import DBManager
from .Registrar import Registrar
from .AdManager import AdManager
from .EvtCoordinator import EvtCoordinator
from .FirebaseManager import FirebaseManager
import copy, time, json

class Publishee():

  __globalpub = None 

  '''
  Singleton-ish
  '''
  @staticmethod 
  def get_publishee() :
    if (Publishee.__globalpub is None):
      print("Creating Publishee object...")
      Publishee.__globalpub = Publishee()
    return Publishee.__globalpub

  def __init__(self): 
    self._status = None
    self._reg = Registrar.getRegistrar()
    self._status = None
    self._fbmgr = FirebaseManager.get_manager()
    self._admgr = AdManager.get_AdManager()

  def receive_data(self, pubkeys):
    self._pubdict = pubkeys
    print("Received data = {}".format(pubkeys))
    self._status = copy.deepcopy(pubkeys)
    self._expires = 0 
    req_time = int(time.time())
    devid = self._pubdict[HDR_DEVID]
    mid = self._pubdict[HDR_MSGID]
    reqd_reg = self._reg.get_registration(devid, keytype=DBHDR_DEVID)
    if (reqd_reg is None) :
        self._status[HDR_TYPE] = EXCP_FORBIDDEN_CODE
        self._status[HDR_RESPONSECLAUSE] = EXCP_FORBIDDEN
    else :
        self._status[HDR_TYPE] = STATUS_ACCEPTED_CODE
        self._status[HDR_RESPONSECLAUSE] = STATUS_ACCEPTED
        
        db_dict = {}
        db_dict[HDR_TIME] = req_time
        db_dict[DBHDR_DEVID] = devid

        pubdata_arr = self._pubdict[HDR_DATA]
        # The following is probably not the best way to go about. The right way would
        # be to update in the next for method. However it just isn't working and I have
        # no idea why - Just guessing it is some sort of race condition. 
        # So let me send the array itself for updating to the publish key
        # See issue #82

        #print ("Trying to request for {} - {}".format(db_dict[HDR_NAME], db_dict))
        tempdict = {} 
        tempdict[DBHDR_DEVID] = devid
        tempdict[HDR_DATA] = pubdata_arr
        self._fbmgr.update(tempdict, TYPE_PUB)

        for pubdata in pubdata_arr :
          db_dict[HDR_NAME] = pubdata[HDR_NAME]
          del pubdata[HDR_NAME]
          db_dict[HDR_DATA] = pubdata
          if ("_id" in db_dict):
            del db_dict['_id'] 
            ## If there were multiple values published by the end point
            ## then during the first insert to mongodb , mongodb would have given
            ## this collection a unique ID. If that's the case, then remove it. 

          DBManager.insert_one(DB_PUBLISHEE_COLN, db_dict)

          ec = EvtCoordinator(name = "publishertrd-{}".format(mid))
          ec.set_event(devid, db_dict[HDR_NAME], pubdata)
          ec.start()

    del self._status[HDR_KEY]
    del self._status[HDR_DATA]
    self._status[HDR_FROM] = get_self_address()
    self._status[HDR_TIME] = req_time

  def get_latest_reading(self, thingname, thinglocation, queryparam):
    devid = self._admgr.get_deviceid (thingname, thinglocation)
    sensorfilter = {DBHDR_DEVID : devid, HDR_NAME  : thingname}
    lastresult = DBManager.find_first(DB_PUBLISHEE_COLN, sensorfilter)
    reqd_paramvalue = lastresult[HDR_DATA][queryparam]
    return reqd_paramvalue


  def response(self) :
    strret = json.dumps(self._status, skipkeys=True)
    return  strret 

'''
{  "Type" : "PUBLISH" , "Ver" : "0.5", "From" : "10.1.1.102",
         "Nid" : "Idev2", "Mid" : "Idev2003", "Time" : 55343213811, 
         "Key" : "keyIdev2", 
         "Data" : {"Name" : "TemperatureSensor", "Location":"Bedroom", 
            {"Temperature" : 25.4, "Humidity" : 60.5, 
             "HeatIndex" : 28.3 }
          }
      }
   “Type” : 202 
      “Mid” : Same ID sent by the request
      “Nid” : Same Device ID sent by request
      “Ver” : Version String – currently 0.5
      “Time” : Registrar's current time 
      “From” : Address of Gateway 



{  “Type” : “SUBSCRIBE” , “Ver” : “0.5”, “From” : “10.1.1.100”,
         “Nid” : “EventProc”, “Mid” : “EventProc001”, 
         “Time” : 55343214011,“Key” : “EventProc123”, 
         “Event” : { “Idev1” : [“Temperature”, “>” , 25.5] }
      }      

what if we write : 
    "Event" : {"DevId" : "Idev1", "Name" : "Temperature#1", "Parameter" : "Temperature", 
        "Condition" : ">", "Value" : Condition_value }     
'''