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

import os,pyrebase, threading, time, requests, ssl, OpenSSL.crypto, traceback
from .constants import *
from .userconfig import config
from .DBManager import DBManager
from .Registrar import Registrar
from httplib2 import ServerNotFoundError


#allitems = db.child("")

class FirebaseManager(threading.Thread) :

    __globalfbmgr = None 
    __hasstarted__ = False

    def get_manager():
      if FirebaseManager.__globalfbmgr is None:
        while FirebaseManager.__hasstarted__ == True :
            time.sleep(1)
            print("Do I realy get called? Huh! The initialization takes some time. let's wait" )
        
        FirebaseManager.__globalfbmgr = FirebaseManager()
        FirebaseManager.__hasstarted__ = False 
        FirebaseManager.__globalfbmgr.start()
      
      return FirebaseManager.__globalfbmgr

    def __init__(self):
      FirebaseManager.__hasstarted__ = True
      print(" I should be called ONCE and only ONCE - {}".format(FirebaseManager.__hasstarted__))
      if (FirebaseManager.__globalfbmgr is not None):
        raise ReferenceError("Do not call the constructor directly")

      self.lastupdatetime = 0 
      self.config = {
        "apiKey": "",
        "authDomain": "",
        "databaseURL": config[CKEY_FBDBURL] ,
        "storageBucket": "",
        "serviceAccount": os.environ[OSKEY_FBSERVICEFILE] 
      }

      super(FirebaseManager, self).__init__()
      self.firebase = None
      self.updatequeue = {}
      self.retry = True 
      self.on_db_error() #Technically there is no error. But this function will call all the methods
        #required to setup the firebase connection
      
    
    def on_db_error(self):
      if self.retry :
        print ("Attempting to connect to firebase ....")  
        try :
          if self.firebase is None:
            firebase = pyrebase.initialize_app(self.config)
          self.db = firebase.database()
          self.timestampserver = self.db.child("META/tsserver").get().val()
          self.retry = False 
        except (FileNotFoundError, OpenSSL.crypto.Error) as e:
          self.db = None
          self.timestampserver = None
          self.retry = False  # This is a fatal error. No point in continueing to try
          print("Problem with Firebase authentication file - {}".format(e))
        except (ServerNotFoundError, requests.exceptions.HTTPError) as e:
          self.db = None
          self.timestampserver = None
          self.retry = True  # We can try later on to see if it can be reached
          print("Could not connect to firebase-{}".format(e))
        
      else:
        print ("We couldn't create a firebase db object. Have given up!")

    def run(self) :
      while True:
        try :
          if (len(self.updatequeue) > 0 ):
            print("updatequeue={}".format(self.updatequeue))
            if self.db is None: 
              self. on_db_error()
            if self.db is None and not self.retry: 
              print("Not trying to update to cloud. Have given up!")
              break 
            elif self.db is None:
              print("Will reattempt firebase...")
              time.sleep(10)
              continue
            #else : 
              #This means that the db has been initialized and we can move on 
              # to the block after the if-then-else block. 
          else : #Means nothing to update to firebase. Just check if firebase has something for us
            self.__check_appmodified()
            time.sleep(.1)
            continue
          
          if (TYPE_AD in self.updatequeue):
            adstoupdate= self.updatequeue.pop(TYPE_AD)
            print("Need to update - {}".format(adstoupdate))
            for item in adstoupdate:
              dataarr = item[HDR_DATA]
              for data in dataarr : 
                if data[HDR_NODETYPE] == NODETYPE_SENSOR:
                  print("Ignoring advertisement for sensors")
                else :
                  loc = data[HDR_LOCATION]
                  name = data[HDR_NAME]
                  name = self.removesplchars(name)
                  params = data[HDR_PARAMS]
                  action = data[HDR_ACTION]
                  print ("Storing to firebase:{}".format(data))
                  dbloc = "LOCATIONS/{}/Actuators/{}".format(loc, name)
                  self.db.child(dbloc).update({HDR_ACTION : action})
                  if not params is None: #Should actually never happen!
                    for key, val in params.items() :
                      key = self.removesplchars(key)
                      print("Storing {} to {}".format(key, val))
                      self.db.child(dbloc).update({key : val})
                      #db.child("Front Desk").set({'Actuators': {'ceiling light': False}}

          if (TYPE_PUB in self.updatequeue):
            datatoupdate= self.updatequeue.pop(TYPE_PUB)
            for item in datatoupdate:
              '''
              filter = {DBHDR_DEVID :item[DBHDR_DEVID], 
              "{}.{}".format(HDR_DATA, HDR_NAME) : item[HDR_NAME]}, \
                  {"{}.$".format(HDR_DATA) : 1}
              '''
              name = item[HDR_NAME]
              filter = {DBHDR_DEVID :item[DBHDR_DEVID], 
              "{}.{}".format(HDR_DATA, HDR_NAME) : name}
              #print("Filter for {} = {}".format(DB_ADS_COLN, filter))
              reqd_ad = DBManager.find_one(DB_ADS_COLN, filter)
              #print("Found items for filter = {}".format(reqd_ad))
              if reqd_ad is not None:
                datas = reqd_ad[HDR_DATA]
                data = None
                for data in datas : 
                  if data[HDR_NAME] == name:
                    break
                loc = data[HDR_LOCATION]
                name = self.removesplchars(name)
                retvalues = item[HDR_DATA]
                #print ("Storing to firebase:{}".format(data))
                dbloc = "LOCATIONS/{}/Sensors/{}".format(loc, name)
                for key, val in retvalues.items() :
                  key = self.removesplchars(key)
                  #print("Storing {} to {} @ {}".format(key, val, dbloc))
                  self.db.child(dbloc).update({key : val})
          
          if (TYPE_CTL in self.updatequeue):
            datatoupdate= self.updatequeue.pop(TYPE_CTL)
            print("Need to update firebase with {}".format(datatoupdate))
            for item in datatoupdate:
              for data in item[HDR_DATA]:
                  devname = data[HDR_NAME]
                  devname = self.removesplchars(devname)
                  devloc = data[HDR_LOCATION]
                  params = data[HDR_PARAMS]
                  '''
                  filter = {DBHDR_DEVID : devid, 
                      "{}.{}".format(HDR_DATA, HDR_NAME) : devname} 
                  reqd_ad = DBManager.find_one(DB_ADS_COLN, filter) 
                  
                  if reqd_ad is not None:
                    devdata = None
                    devdatas = reqd_ad[HDR_DATA]
                    for devdata in devdatas : 
                        if devdata[HDR_NAME] == devname:
                          break

                    loc = devdata[HDR_LOCATION]
                    ''' 

                    
                  for paramname, paramvalue in params.items(): 
                      dbloc = "LOCATIONS/{}/ActuatorStates/{}".format(devloc, devname, paramname)
                      print("DB location = {}. Val={}".format(dbloc, {paramname:paramvalue}))
                      self.db.child(dbloc).update({paramname:paramvalue})

                      print ("Storing to firebase:{}".format(data))

                      #dbloc = "{}/Sensors/{}".format(loc, name)
                      #for key, val in retvalues.items() :
                      #  key = self.removesplchars(key)
                      #  print("Storing {} to {} @ {}".format(key, val, dbloc))
                      # self.db.child(dbloc).update({key : val})

          self.__check_appmodified()
        except Exception as e:
          print("Error in main loop of firebase manager - {}".format(e))
          traceback.print_exc
          pass # Just ignore this time and try again
        time.sleep(1)
    
    def __check_appmodified(self):
      tsurl="https://{}".format(self.timestampserver)
      tsupdatetime = int(requests.get(tsurl).text)
      if (tsupdatetime > self.lastupdatetime):
        print("last update={}; server time={}".format(self.lastupdatetime, tsupdatetime))
        self.lastupdatetime = tsupdatetime
        appmodified = self.db.child("APPMODIFIED").get()
        if appmodified.val() is not None:
          for modified in appmodified.each():
            devloc = modified.key()
            devdetails = modified.val()
            print("Will now control the device - {}-{}".format(devloc, devdetails))
            #print(type(devdetails))

            for devname, params  in devdetails.items() :
                ctlmsg ={}
                ctlmsg[HDR_TYPE] = TYPE_CTL 
                ctlmsg[HDR_VER] = VER_VALUE
                ctlmsg[HDR_FROM] = get_self_address()
                ctlmsg[HDR_TIME] = int(time.time())

                filter = {"{}.{}".format(HDR_DATA, HDR_LOCATION) : devloc, 
                  "{}.{}".format(HDR_DATA, HDR_NAME) : devname}
                reqd_ad = DBManager.find_one(DB_ADS_COLN, filter) 
                if reqd_ad is not None:  
                  devdata = None
                  devdatas = reqd_ad[HDR_DATA]
                  
                  for devdata in devdatas : 
                      if devdata[HDR_NAME] == devname:
                        break
                  
                  ctlmsg[HDR_DEVID] = reqd_ad[DBHDR_DEVID]
                  ctlmsg[HDR_MSGID] = "{}_{}".format(ctlmsg[HDR_DEVID], int(time.time()))
                  if (HDR_CONTROLMETHOD in reqd_ad):
                    ctlmsg[HDR_CONTROLMETHOD] = reqd_ad[HDR_CONTROLMETHOD]
                  else :
                    print("ControlMethod not defined. Setting to default")
                    ctlmsg[HDR_CONTROLMETHOD] = CONTROLMETHOD_DEAMON
                  registrar = Registrar.getRegistrar()
                  reqd_regs = registrar.get_registration(ctlmsg[HDR_DEVID], 
                      keytype=DBHDR_DEVID)
                  if (reqd_regs is None) :
                      print("Error : No active registration found for {}".format(devname) )
                  else :
                      data = {}
                      ctlmsg[HDR_KEY] = reqd_regs[HDR_KEY]
                      ctlmsg[HDR_CONTACT] = reqd_regs[HDR_FROM]
                      data[HDR_NAME] = devname
                      data[HDR_PARAMS] = params
                      data[HDR_ACTION] = devdata[HDR_ACTION]
                      ctlmsg[HDR_DATA] = [data]
                      # Don't try to put this in the begining. we have
                      # cyclic dependancies and s@$t __WILL__ happen
                      from .HttpSender import HttpSender
                      sender = HttpSender(name = "ctlsender-{}-{}".format(devname, time.time()))
                      sender.setParameters("http://{}".format(ctlmsg[HDR_CONTACT]), ctlmsg, False)
                        ## The last parameter is false because we read these from the APP Db itself
                        ## There is no point in updating the same value back to the APP DB> 
                      sender.start()
                      #print("Sending control message = {}. Target = {}".format(ctlmsg, ctlmsg[HDR_CONTACT]))

                    # We should actually be checking for response before deleting 
                    #- Issue #28 - https://github.com/thingsping/sparkcapstone/issues/28
                self.db.child("APPMODIFIED").child(devloc).child(devname).remove()
      elif tsupdatetime < self.lastupdatetime:
        print("RUN AWAY NOW! Time space continum disrupted. " \
          "My time ={}.Their time={} ".format(self.lastupdatetime, tsupdatetime))

    def update(self, dbdict, dbtype):
      if not dbtype in self.updatequeue :
        self.updatequeue[dbtype] = []
      queItems = self.updatequeue[dbtype]
      if (dbtype == TYPE_AD):
        curDevId = dbdict[DBHDR_DEVID]
        for item in queItems:
          queDevId = item[DBHDR_DEVID]
          if (queDevId == curDevId):
            queItems.remove(item)
            # Technically you can break here. You should only have one 
            # item with this device id in the queue already
        self.updatequeue[dbtype].append(dbdict)
      elif (dbtype == TYPE_PUB):
        curDevId = dbdict[DBHDR_DEVID]
        for updateitem in dbdict[HDR_DATA]:
          curPubName = updateitem[HDR_NAME]
          for item in queItems:
            queDevId = item[DBHDR_DEVID]
            quePubname = item[HDR_NAME]
            #print("Before remove - update queue = {}".format(self.updatequeue))
            if (queDevId == curDevId and quePubname == curPubName):
              queItems.remove(item)
            #print("After remove - update queue = {}".format(self.updatequeue))
          itemToAdd = {}
          itemToAdd[DBHDR_DEVID] = curDevId
          itemToAdd[HDR_NAME] = curPubName
          itemToAdd[HDR_DATA] = updateitem
          self.updatequeue[dbtype].append(itemToAdd)
      elif dbtype == TYPE_CTL :
        curDevName = dbdict[HDR_DATA][0][HDR_NAME] 
        curDevLoc = dbdict[HDR_DATA][0][HDR_LOCATION] 

        for item in queItems:
          queName = item[HDR_DATA][0][HDR_NAME]
          queLoc = item[HDR_DATA][0][HDR_LOCATION]
          if (queName == curDevName and queLoc == curDevLoc):
            queItems.remove(item)          
        self.updatequeue[dbtype].append(dbdict)  

    def removesplchars(self, key):
      key = key.replace("#", "num")
      # Add other values
      return key 