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

      super(FirebaseManager, self).__init__()
      
      
    
    def on_db_error(self):      
        print ("We couldn't create a firebase db object. Have given up!")

    def run(self) :
      print("FB support removed. Please refer tracker issues")

    def update(self, dbdict, dbtype):
      print("Firebase integration is not yet implemented and is buggy. We are exploring alternatives...") ; 
