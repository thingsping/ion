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
try :
    from .constants import * 
except :
    from constants import * 

config = {
    CKEY_DBNAME : "qantomion",
    CKEY_MODULENAME : "ionserver", 
    CKEY_SELF_IP : "put_server_address_here",
    CKEY_BASEPATH : "/var/www/html/ionserver", 
    CKEY_FBSERVICEFILE : "service.json",
    CKEY_FBDBURL : "put_url_of_firebase",
    CKEY_SERVERFQDN : "FQDN_of_server",
    CKEY_POLLRESPPORT : 10560, 
}