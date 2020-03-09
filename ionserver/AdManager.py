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
__date__ = "$June 24, 2019 "

from .constants import * 
from .DBManager import DBManager
from .Registrar import Registrar
from .FirebaseManager import FirebaseManager
import copy, json, time

class AdManager():

    __globalcreds = None

    '''
    Effect of singleton
    '''
    @staticmethod 
    def get_AdManager() :
        if (AdManager.__globalcreds is None):
            print("Creating AdManager object...")
            AdManager.__globalcreds = AdManager() 
        return AdManager.__globalcreds 

    def __init__(self): 
        #self._adscoln = DBManager.getCollection(DB_ADS_COLN)
        self._reg = Registrar.getRegistrar()
        self._status = None
        self._fbmgr = FirebaseManager.get_manager()
        self._pubmgr = None

    def post_ad(self, adkeys):
        self._addict = adkeys
        self._status = copy.deepcopy(adkeys)
        self._expires = 0 
        req_time = int(time.time())
        addata = self._addict[HDR_DATA]
        del self._status[HDR_KEY]
        del self._status[HDR_DATA]
        mid = self._addict[HDR_MSGID]
        key = self._addict[HDR_KEY]
        #First find if there is a registration with the said MID
        reqd_regs = self._reg.get_registration(mid)
        if (reqd_regs is None or key != reqd_regs[HDR_KEY]):
          self._status[HDR_TYPE] = EXCP_FORBIDDEN_CODE
          self._status[HDR_RESPONSECLAUSE] = EXCP_FORBIDDEN
        else :
          self._status[HDR_TYPE] = STATUS_ACCEPTED_CODE
          self._status[HDR_RESPONSECLAUSE] = STATUS_ACCEPTED

          dbdict = {} 
          dbdict[DBHDR_DEVID] = self._addict[HDR_DEVID]
          dbdict[HDR_DATA] = addata
          if (HDR_CONTROLMETHOD in self._addict):              
              dbdict[HDR_CONTROLMETHOD] =self._addict[HDR_CONTROLMETHOD]
          
          print ("Creating/Updating an entry in the Ad db - %s" 
              %(dbdict[DBHDR_DEVID]))
          filter = {DBHDR_DEVID : dbdict[DBHDR_DEVID]}
          #self._adscoln.replace_one(filter,dbdict, upsert=True)   
          DBManager.replace_one(DB_ADS_COLN, dbdict, filter)
          self._fbmgr.update(dbdict, TYPE_AD)
        self._status[HDR_FROM] = get_self_address()
        self._status[HDR_TIME] = req_time

    def query(self, reqkeys, get_key=False):
        self._status = copy.deepcopy(reqkeys)
        devid = reqkeys[HDR_TARGET]
        del self._status[HDR_TARGET]
        del self._status[HDR_MSGID]
        self._expires = 0 
        req_time = int(time.time())
        dataarr = []
        if (devid == "*"):
            reqd_regs = self._reg.get_active_registrations()
            if (reqd_regs is None):
                self._status[HDR_TYPE] = EXCP_NOTFOUND_CODE
                self._status[HDR_RESPONSECLAUSE] = EXCP_NOTFOUND
            else :
                self._status[HDR_TYPE] = STATUS_OK_CODE
                self._status[HDR_RESPONSECLAUSE] = STATUS_OK
                for reg in reqd_regs :
                  datas = self._reg.get_query_item(reg)
                  for data in datas : 
                    if (data is not None):
                        dataarr.append(data)

                self._status[HDR_DATA] = dataarr
        else :     
            reqd_regs = self._reg.get_registration(devid, keytype=DBHDR_DEVID)
            if (reqd_regs is None) :
                self._status[HDR_TYPE] = EXCP_NOTFOUND_CODE
                self._status[HDR_RESPONSECLAUSE] = EXCP_NOTFOUND
            else :
                self._status[HDR_TYPE] = STATUS_OK_CODE
                self._status[HDR_RESPONSECLAUSE] = STATUS_OK

                datas = self._reg.get_query_item(reqd_regs)
                for data in datas : 
                    if (data is not None):
                        #Key will ONLY be send in case of individual queries
                        if(get_key):
                            data[HDR_KEY] = reqd_regs[HDR_KEY]
                        dataarr.append(data)
                self._status[HDR_DATA] = dataarr
                  
        self._status[HDR_FROM] = get_self_address()
        self._status[HDR_TIME] = req_time
        return self._status

    def get_deviceid(self, devname, devloc):
        filter = { "{}.{}".format(HDR_DATA, HDR_NAME) : devname , 
            "{}.{}".format(HDR_DATA, HDR_LOCATION) : devloc }
        #print ("Filter for getting device id = {}".format(filter))
        devidresult = DBManager.find_one(DB_ADS_COLN, filter)
        return devidresult[DBHDR_DEVID]

    def get_location(self, devname, devid):
        filter = {DBHDR_DEVID : devid}
        devidresult = DBManager.find_one(DB_ADS_COLN, filter)
        datas = devidresult[HDR_DATA]
        res = None 
        for data in datas:
            if data[HDR_NAME] == devname:
                res = data[HDR_LOCATION]
                break 
        return res
    
    def get_all_locations(self):
        locationsarray = []
        results = DBManager.find(DB_ADS_COLN)
        for result in results : 
            if (result is not None):
                #del data["_id"] # We don't wan't mongo's internal ID
                datas = result[HDR_DATA]
                for data in datas:
                    loc = data[HDR_LOCATION]
                    if not loc in locationsarray:
                        locationsarray.append(loc)                    
        return locationsarray

    def get_all_devices(self):

        
        if self._pubmgr == None :
          from .Publishee import Publishee
          self._pubmgr = Publishee.get_publishee() 

        alldevs = []
        results = DBManager.find(DB_ADS_COLN)
        for result in results : 
            if (result is not None):
                devid = result[DBHDR_DEVID]
                isactive = self._reg.is_active(devid)
                datas = result[HDR_DATA]
                for data in datas:
                    devdetails = {}
                    devdetails[HDR_NAME] = data[HDR_NAME]
                    devdetails[HDR_LOCATION] = data[HDR_LOCATION]
                    devdetails[HDR_NODETYPE] = data[HDR_NODETYPE]
                    devdetails[HDR_ISACTIVE] = isactive
                    val = "" 
                    if devdetails[HDR_NODETYPE] == NODETYPE_SENSOR :
                        #find all the return values for this sensor
                        all_returns = list(data[HDR_RETURN].keys())
                        
                        if len(all_returns) != 0 :
                            queryparam = all_returns[0]
                            val = self._pubmgr.get_latest_reading(devdetails[HDR_NAME], 
                                devdetails[HDR_LOCATION], queryparam)

                            # Issue #73 still exists and has to be addressed
                    else :
                        val = "" #We'll see how to handle last state of actuator later on
                    devdetails[HDR_VALUE] = val 
                    alldevs.append(devdetails)
        return alldevs             
                
    def response(self) :
        strret = json.dumps(self._status, skipkeys=True)
        return  strret 

'''
FOR QUERIES : 
  Request:
 {
   “Ver” : “0.5”, “Mid” : “A_UNIQUE_VALUE”, 
   “Type” : “QUERY”,  “From” : “SELF_ADDRESS”,
    “Nid”  : “Device ID of the entity sending the message”,
    “TargetId” : “DEVICE_ID of Target", 
    “Time” : node's_time
  }
Response : 
“Type” : “200” 
      “Ver” : “0.5”
      “From” : “Address of server”
      “Mid” : MID Sent in original request
      “Time” : server's_time
      “Data” : ...

In the above request  Retained for Response are : 
  Ver, Mid

Following will be modified :
    “Type” : “200”  (or 404)
    “From” : “Address of server”
    “Time” : server's_time

Following are new : 
    "RespClause" : 
    A new header called "Data" has to be added for each 
    discovery. It will have a Json with :
        "Nid" : Copy from NID of Request 
        "Contact" : Get from registration db
        "Expires" : Get from registration db 
        "Capabilities" : Get from Advertisement DB

Remove from Request 
   "TargetId" : After copying into Data 
   "Nid"

'''

 
'''
{ 
    
    “Type” : “ADVERTISE” , “Ver” : “0.5”, “From” : “10.1.1.102”,
         “Nid” : “Idev2”, 
         “Mid” : “Idev2002”, 
         “Time” : 55343213711, 
         “Key” : “0a2468f2c5c6d69621afd7bedd3744d4”, 
         “Data” :  
             { “Name” : “TemperatureSensor”, “NodeType” : “Sensor”, 
               “Location” : “Bedroom”,
               “Capabilities” :[“Read Temperature”, “Read Humidity”], 
               “Parameters” : {“isFaranheit”: “Boolean”}, 
               “Return” : {“Temperature” : “Float”, 
                  “Humidity” : “Float”, “HeatIndex” : “Float” }
             }
      }

'''