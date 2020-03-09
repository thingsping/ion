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
__date__ = "$June 22, 2019"

from .constants import * 
from .DBManager import DBManager
from .CredsManager import CredsManager
from .IonExceptions import ForbiddenException
import copy, time, json

class Registrar():

  __globalreg = None 

  '''
  Like a singleton class. Well it is not possible to implement a pure singleton 
  class in python but by using the following technique we can come close to that
  We need to be careful to never call the class initialization ever. 
  '''
  @staticmethod 
  def getRegistrar() :
    if (Registrar.__globalreg is None):
      print("Creating registrar object...")
      Registrar.__globalreg = Registrar()
    return Registrar.__globalreg 

  def __init__(self): 
    self._status = None
    self._tempregdict = {}
    #self._regcoln = DBManager.getCollection(DB_REGS_COLN)
   
  def register(self, regkeys):
    self._regdict = regkeys
    self._status = copy.deepcopy(regkeys)
    self._expires = 0 
    del self._status[HDR_EXPIRES]
    del self._status[HDR_KEY]
    req_time = int(time.time())
    creds = CredsManager.getCredsManager()
    # First check if there was an initial request for this devid without key
    mid = self._regdict[HDR_MSGID]
    if (mid in self._tempregdict):
      print("In this version we don't support HASH based authentication")
    else : 
      try : 
        self.isAuth = creds.check_device(self._regdict[HDR_DEVID], self._regdict[HDR_KEY])  
        if (self.isAuth):
          self._expires = self._regdict[HDR_EXPIRES]
          self._status[HDR_TYPE] = STATUS_OK_CODE
          self._status[HDR_RESPONSECLAUSE] = STATUS_OK

          dbdict = {} 
          dbdict[HDR_FROM] = self._regdict[HDR_FROM]
          dbdict[DBHDR_DEVID] = self._regdict[HDR_DEVID]
          dbdict[HDR_MSGID] = self._regdict[HDR_MSGID]
          dbdict[HDR_KEY] = self._regdict[HDR_KEY]
          dbdict[HDR_EXPIRES] = req_time + self._expires


          ''' 
          #Actually delete all previous registrations for this
          #device id. Before we were only deleting those with a different
          #message id. 
          #First delete any entries for the same Device ID but with a 
          # different message ID. 
          filter = { "$and" : [ {DBHDR_DEVID : dbdict[DBHDR_DEVID]}, 
            { HDR_MSGID : {"$ne": dbdict[HDR_MSGID]}} ] } 
          '''
          filter = {DBHDR_DEVID : dbdict[DBHDR_DEVID]}
          DBManager.delete_many(DB_REGS_COLN, filter)
          
          print ("Creating/updating entry in the registration db - %s" 
              %(dbdict[DBHDR_DEVID]))
          filter = {HDR_MSGID : dbdict[HDR_MSGID]}
          DBManager.replace_one(DB_REGS_COLN, dbdict, filter)
        else :
          self._status[HDR_TYPE] = EXCP_UNAUTH_CODE
          self._status[HDR_RESPONSECLAUSE] = EXCP_UNAUTH_FIN

      except ForbiddenException as e :
        self._status[HDR_TYPE] = e.code()
        self._status[HDR_RESPONSECLAUSE] = e.message()
      self._status[HDR_FROM] = get_self_address()
      self._status[HDR_TIME] = req_time

  def get_registration(self, mid, keytype=HDR_MSGID):
     filter = {keytype : mid}
     #res = self._regcoln.find_one(filter)
     res = DBManager.find_one(DB_REGS_COLN, filter)
     if (res is None ):
       print("No entry found at all with said filter")
       return None 
     expires = res[HDR_EXPIRES]
     cur_time = int(time.time())
     if ((expires - cur_time) > 0) :
       return res 
     else :
       print("Registration already expired! for {}".format(mid))
       return None

  def get_active_registrations(self):
    cur_time = int(time.time())
    filter = { HDR_EXPIRES : { '$gt' : cur_time } }
    #res = self._regcoln.find(filter)
    res = DBManager.find(DB_REGS_COLN, filter)
    if (res is not None and res.count() != 0 ):
      return res 
    else : 
      return None

  def is_active(self, devid):
    filter = {DBHDR_DEVID : devid}
    res = DBManager.find_one(DB_REGS_COLN, filter)
    if (res is not None ):
      expires = res[HDR_EXPIRES]; 
      if expires > int(time.time()):
        return True 
      else :
        return False 
    else :
      return False 

  def get_query_item(self, reg):
      filter = {DBHDR_DEVID : reg[DBHDR_DEVID]}
      res = DBManager.find_one(DB_ADS_COLN, filter)
      datas = []
      if (res is not None):
          for data in res[HDR_DATA]:
              #data = res[HDR_DATA]
              data[HDR_DEVID] = res[DBHDR_DEVID]
              data[HDR_CONTACT] = reg[HDR_FROM]
              data[HDR_EXPIRES] = reg[HDR_EXPIRES]
              datas.append(data)
      return datas

  def response(self) :
    strret = json.dumps(self._status, skipkeys=True)
    return  strret


'''
FOR REGISTRATION : 
  { 
    # These remain same as in request     
     “Ver” : “0.5”, “Nid” : “Idev1”, “Mid” : “Idev1001”, 
     
     #The following headers will change based on the processing 
     “Type” : 200, 
     “RespClause” : “OK”,   
     “Time” : time at registration 
     “From” : IP Address of server

     # The following has to be removed from the response
     “Expires” : 3600  
     "Key"
  }

{ 
    "Ver" : "0.5", "Nid" : "Idev1", "Mid" : "Idev1001", 
    "Type" : "REGISTER", 
    "From" : "10.1.1.101",
    "Time" : %TIME%, 
    "Key"  : "some key 
}
'''