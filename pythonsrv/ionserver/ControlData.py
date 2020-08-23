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
__date__ = "$August 22, 2020 "

import time

class ControlData:
    def __init__(self, controldata, uid=None, updateFB = True, updateDB = True): 
        self._ctldata = controldata
        self._isFbUpdateRequired = updateFB
        self._isDbUpdateRequired = updateDB
        if (uid is None):
            self._uniqueId = "ctl-{}".format(time.time())
        else :
            self._uniqueId = uid

    def getUID(self):
        return self._uniqueId

    def getControlData(self):
        return self._ctldata

    def isFbUpdateRequired(self):
        return self._isFbUpdateRequired

    def isDbUpdateRequired(self):
        return self._isDbUpdateRequired
