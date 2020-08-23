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
from .IonExceptions import * 
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
        allMandatory = True
        mandatoryClause = "" 
        for data in addata :
            if (not HDR_LOCATION in data or not HDR_NAME in data) :
                allMandatory = False 
                mandatoryClause = "Name/Location not specified"                        
                break 
            nodetype = data[HDR_NODETYPE]
            if nodetype == NODETYPE_SENSOR and not HDR_RETURN in data:
                allMandatory = False
                mandatoryClause = "Return definition not specified"
                break

        if not allMandatory:
            self._status[HDR_TYPE] = EXCP_BADFORMAT
            self._status[HDR_RESPONSECLAUSE] = mandatoryClause
        else : 
          #First find if there is a registration with the said MID
          reqd_regs = self._reg.get_registration(mid)
          if (reqd_regs is None or key != reqd_regs[HDR_KEY]):
            self._status[HDR_TYPE] = EXCP_FORBIDDEN_CODE
            self._status[HDR_RESPONSECLAUSE] = EXCP_FORBIDDEN
          else :
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
            self._status[HDR_TYPE] = STATUS_ACCEPTED_CODE
            self._status[HDR_RESPONSECLAUSE] = STATUS_ACCEPTED
            self._status[HDR_FROM] = get_self_address()
        self._status[HDR_TIME] = req_time

    def query(self, reqkeys, get_key=False):
        self._status = copy.deepcopy(reqkeys)
        print(self._status)
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
                isAuth = False 
                if not HDR_KEY in self._status :
                    isAuth = False
                else:
                    try:
                        isAuth =self._reg.isAuthenticated(self._status[HDR_DEVID], self._status[HDR_KEY])
                    except ForbiddenException: 
                        isAuth = False
                if (isAuth):
                    datas = self._reg.get_query_item(reqd_regs)
                    datacount = 0 
                    for data in datas :
                        if (data is not None):
                            #Key will ONLY be send in case of individual queries
                            if(get_key):
                                data[HDR_KEY] = reqd_regs[HDR_KEY]
                            dataarr.append(data)
                            datacount = datacount + 1
                    if (datacount != 0 ):
                        self._status[HDR_DATA] = dataarr
                        self._status[HDR_TYPE] = STATUS_OK_CODE
                        self._status[HDR_RESPONSECLAUSE] = STATUS_OK
                    else : 
                        self._status[HDR_TYPE] = EXCP_NOTFOUND_CODE
                        self._status[HDR_RESPONSECLAUSE] = EXCP_NOTFOUND
                else :
                    self._status[HDR_TYPE] = EXCP_FORBIDDEN_CODE
                    self._status[HDR_RESPONSECLAUSE] = EXCP_FORBIDDEN
                  
        self._status[HDR_FROM] = get_self_address()
        self._status[HDR_TIME] = req_time
        return self._status

    def addActuatorState(self, inctlmsg):
        #print("Received Actuator state update. Json=({})".format(inctlmsg))
        # Without the next line, the original calling json gets messed up
        # and bad things happen in the HTTPSender class
        ctlmsg = copy.deepcopy(inctlmsg)
        devid = ctlmsg[HDR_DEVID]
        ctldata = ctlmsg[HDR_DATA]
        #print("In data={}".format(ctldata))
        for item in ctldata:
            statesjson = {}
            devname = item[HDR_NAME]            
            devloc = self.get_location(devname, devid)
            item[HDR_LOCATION] = devloc
            item[DBHDR_DEVID] = devid

            devStates = DBManager.find_one(DB_DEVICESTATES_COLN, {HDR_NAME : devname, HDR_LOCATION : devloc})
            if devStates is not None : 
                #print("Deleting previous state to create afresh")
                DBManager.delete_many(DB_DEVICESTATES_COLN, {HDR_NAME : devname, HDR_LOCATION : devloc})
            print("Now inserting in device states - {}".format(item))
            DBManager.insert_one(DB_DEVICESTATES_COLN, item)

    def get_deviceid(self, devname, devloc):
        filter = { "{}.{}".format(HDR_DATA, HDR_NAME) : devname , 
            "{}.{}".format(HDR_DATA, HDR_LOCATION) : devloc }
        #print ("Filter for getting device id = {}".format(filter))
        devidresult = DBManager.find_one(DB_ADS_COLN, filter)
        if devidresult is None:
            return None
        else:
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
                    tm = -1
                    if devdetails[HDR_NODETYPE] == NODETYPE_SENSOR :
                        #find all the return values for this sensor
                        all_returns = list(data[HDR_RETURN].keys())
                        
                        if len(all_returns) != 0 :
                            queryparam = all_returns[0]
                            val = self._pubmgr.get_latest_reading(devdetails[HDR_NAME], 
                                devdetails[HDR_LOCATION], queryparam)
                            tm = self._pubmgr.get_latest_reading_time(
                                devdetails[HDR_NAME], devdetails[HDR_LOCATION])

                            # Issue #73 still exists and has to be addressed
                    else :
                        val = "" #We'll see how to handle last state of actuator later on
                        tm = -1 
                    devdetails[HDR_VALUE] = val 
                    devdetails[HDR_TIME] = tm
                    alldevs.append(devdetails)
        return alldevs             
                
    def response(self) :
        strret = json.dumps(self._status, skipkeys=True)
        return  strret 
