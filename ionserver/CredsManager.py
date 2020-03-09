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
__date__ = "$June 22, 2019 "

import hashlib
from .constants import * 
from .DBManager import DBManager
from .IonExceptions import ForbiddenException

class CredsManager():

    __globalcreds = None

    '''
    Effect of singleton
    '''
    @staticmethod 
    def getCredsManager() :
        if (CredsManager.__globalcreds is None):
            print("Creating Credentials object...")
            CredsManager.__globalcreds = CredsManager() 
        return CredsManager.__globalcreds 

    def __init__(self): 
        self.credscoln = DBManager.getGlobalCollection(DB_CREDS_COLN)

    def check_device(self, devid, key, hasher=None): 
        devquery = { DBHDR_DEVID : devid}
        devresult = self.credscoln.find_one(devquery)
        if (devresult is None):
            raise ForbiddenException() 
        else :
            dbkey = devresult[HDR_KEY]
            isauth = False
            if hasher is None:
                isauth = (dbkey == key )
            else : 
                str = "{}|{}".format(dbkey, hasher)
                dbhash = hashlib.md5(str.encode()).hexdigest()
                isauth = (dbhash == key)
            return isauth
            