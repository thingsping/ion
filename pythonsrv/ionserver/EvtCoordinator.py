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
__date__ = "$June 26, 2019 "

import threading, time
from .constants import *
from .DBManager import DBManager
from .AdManager import AdManager
from .HttpSender import HttpSender
from .userconfig import config

class EvtCoordinator(threading.Thread):

    def set_event(self, deviceid, entityname, publisheddata ):

       self._devid = deviceid
       self._entity = entityname
       self._pubdata = publisheddata
       self._pubmgr = None

    def run(self):

        admgr = AdManager.get_AdManager()
        location = admgr.get_location(self._entity, self._devid)
        filter = { HDR_EVENT + "." + HDR_LOCATION  : location , 
            HDR_EVENT +"." + HDR_NAME : self._entity }
        #print("Filter = {}".format(filter))
        res = DBManager.find(DB_SUBSCRIPTIONS_COLN, filter)
        req_time = int(time.time())

        #if (res.count() == 0) :
          #print("No subscriptions found for")
          #print(filter)
        if self._pubmgr == None :
          from .Publishee import Publishee
          self._pubmgr = Publishee.get_publishee() 

        for item in res:
          evtparam = item[HDR_EVENT][HDR_PARAM]
          readparam = self._pubdata[evtparam]
          if (readparam is not None):
            cond = item[HDR_EVENT][HDR_COND]
            condvalue = item[HDR_EVENT][HDR_CONDVALUE]
            #print("CONDITION IS - {} {} {} ".format(readparam, cond, condvalue))
            if isinstance(readparam, str):
              is_satisfied = eval('"%s" %s "%s"' %(readparam, cond, condvalue))
            else:
              is_satisfied = eval("%s %s %s" %(readparam, cond, condvalue))
            if (is_satisfied):
              actions = item[HDR_ACTION]
              print("Condition for {} {} {} is satisfied. Action count = {}".format(
                readparam, cond, condvalue, len(actions)))
              for action in actions : 
                #print("Action  : {}".format(action))
                req_name = action[HDR_NAME]
                req_location = action[HDR_LOCATION]
                req_devid = admgr.get_deviceid(req_name, req_location)
                query_dict = {}
                query_dict[HDR_VER] = VER_VALUE
                query_dict[HDR_MSGID] = "evtcordinator-{}".format(req_time)
                query_dict[HDR_TYPE] = TYPE_QUERY
                query_dict[HDR_FROM] = "localhost"
                query_dict[HDR_DEVID] = config[CKEY_EVTCORD_HOST]
                query_dict[HDR_KEY] = config[CKEY_EVTCORD_KEY]
                query_dict[HDR_TARGET] = req_devid
                query_dict[HDR_TIME] = req_time
                devdetails = admgr.query(query_dict, get_key=True)
                #print("Control query = {}".format(devdetails))
                elapsed = 0  
                starttime = time.time()
                THREADTIMEOUT = 0.1 
                ## There is no reason to call another class just to construct the control message
                ## After all the event coordinator exists to process events and alongside take action
                if devdetails is None or devdetails[HDR_TYPE] != STATUS_OK_CODE:
                    print("Unable to control {}.{}".format(req_name,req_location) ) 
                else :
                  # Following while loop due to issueL
                  # https://github.com/thingsping/sparkcapstone/issues/14
                  # Smells like a timing issue with Python threads. The following line
                  # should have never happened
                  # In any case the following should be called in a separate thread. 
                  while elapsed < THREADTIMEOUT : 
                    if (devdetails[HDR_TYPE] == STATUS_OK_CODE):
                      break  # We are all good 
                    else :
                      elapsed =  time.time() - starttime
                      time.sleep(.01)
                  if (devdetails[HDR_TYPE] != STATUS_OK_CODE):    
                    print("Unable to control {}.{}".format(req_name,req_location) ) 
                  else :
                    # Remember that there could be multiple capabilities associated with a single 
                    # physical device
                    all_data =   devdetails[HDR_DATA]
                    for data in all_data :
                        devname = data[HDR_NAME]
                        print ("Attempting control device - {}-{}".format(devname,devdetails))
                        if (req_name == devname) :
                          ctr_dict = {}
                          ctr_dict[HDR_TYPE] = TYPE_CTL
                          ctr_dict[HDR_VER] = VER_VALUE
                          ctr_dict[HDR_FROM] = get_self_address()
                          ctr_dict[HDR_DEVID] = req_devid
                          ctr_dict[HDR_MSGID] = query_dict[HDR_MSGID]
                          ctr_dict[HDR_TIME] = req_time
                          ctr_dict[HDR_KEY] = data[HDR_KEY]        
                          ctr_dict[HDR_CONTROLMETHOD] = data[HDR_CONTROLMETHOD]
                          ctr_data = {}
                          ctr_data[HDR_LOCATION] = req_location
                          ctr_data[HDR_NAME] = action[HDR_NAME]
                          ctr_data[HDR_ACTION] = data[HDR_ACTION] 
                          reqd_params = action[HDR_PARAMS]
                          #print("Parameters for {} - {}".format(action[HDR_NAME], reqd_params))
                          for actionparam in reqd_params:
                            reqd_paramvalue = reqd_params[actionparam]
                            if (type(reqd_paramvalue) is dict):
                              queriedloc = reqd_paramvalue[HDR_LOCATION]
                              queriedname = reqd_paramvalue[HDR_NAME]
                              queriedparameter = reqd_paramvalue[HDR_PARAM]

                              '''
                              #print("Need to query - {}, {} and {}".format(queriedloc, queriedname, queriedparameter))
                              devid = admgr.get_deviceid (queriedname, queriedloc)
                              #print("DEVICE ID = {}".format(devid))
                              #sensorfilter = { DBHDR_DEVID : devid }     
                              sensorfilter = {DBHDR_DEVID : devid, HDR_NAME  : queriedname}
                              firstreading = DBManager.find_first(DB_PUBLISHEE_COLN, sensorfilter)
                              print("First reading = {}".format(firstreading))
                              reqd_paramvalue = firstreading[HDR_DATA][queriedparameter]
                              '''
                              
                              reqd_paramvalue =  self._pubmgr.get_latest_reading(queriedname, queriedloc, queriedparameter)
                              #print("Translated param value = {}".format(reqd_paramvalue))

                              dtype = data[HDR_PARAMS][actionparam]
                              #In case of string, we don't do any checks in blockly and 
                              #allow all types to be attached here. 
                              if (dtype == PARAMTYPESTRING):
                                reqd_paramvalue = str(reqd_paramvalue)
                              reqd_params[actionparam] = reqd_paramvalue

                          ctr_data[HDR_PARAMS] = action[HDR_PARAMS]

                          # currently we will only send one data message in 
                          # one control request. However protocol supports
                          # multiple control messages to the same entity to wrapped
                          # in one message. SO wrap it in an array
                          ctr_dict[HDR_DATA] = [ctr_data]

                          tgt = data[HDR_CONTACT]
                          
                          print("All set now. Will send CONTROL message - {} to {}".format(ctr_dict,tgt))
                          #print (ctr_dict)    
                          sender = HttpSender(name = "ctlsender-{}-{}".format(HDR_MSGID, time.time()))
                          sender.setParameters("http://{}".format(tgt), ctr_dict)
                          sender.start()
                          break #Now that's it this action is completed
                        else :
                          print("Req name = {}; Device Name = {}".format(req_name, devname) )
            else :
              print("Condition not satisfied - %s %s %s " %(readparam, cond, condvalue ))
          else : 
            print ("No event definition for [%s]" %(self._pubdata[evt_param]))

              
