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
from .constants import * 


class ForbiddenException(Exception):
    def __init__(self):
        Exception.__init__(self, EXCP_FORBIDDEN)
        self._code = EXCP_FORBIDDEN_CODE

    def code(self):
        return self._code 

    def message(self):
        return EXCP_FORBIDDEN