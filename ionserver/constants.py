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
import socket 

## Constants for JSON Headers
HDR_TYPE = "Type"
HDR_KEY = "Key"
HDR_VER = "Ver"
HDR_FROM = "From"
HDR_DEVID = "Nid"
DBHDR_DEVID = "DevId"
HDR_MSGID = "Mid"
HDR_TIME = "Time"
HDR_EXPIRES = "Expires"
HDR_TARGET = "TargetId"
HDR_RESPONSECLAUSE = "RespClause"
HDR_DATA = "Data"
HDR_CAPABILITIES = "Capabilities"
HDR_CONTACT = "Contact"
HDR_NAME = "Name"
HDR_LOCATION = "Location"
HDR_LOCATIONS = "Locations"
HDR_DEVICES = "Devices"
HDR_NODETYPE = "NodeType"
HDR_CONTROLMETHOD = "ControlMethod"
HDR_ISACTIVE = "Active"
HDR_EVENT = "Event"
HDR_ACTION = "Action"
HDR_PARAM = "Parameter"
HDR_PARAMS = "Parameters"
HDR_RETURN = "Return"
HDR_COND = "Condition"
HDR_CONDVALUE = "CondValue"
HDR_VER = "Ver"
HDR_VALUE = "Value"
HDR_NONCE = "Nonce"
HDR_CONFIG = "Config"
HDR_CONFIGHASH = "Chash"

#Output node or sensor node?
NODETYPE_SENSOR = "Sensor"
NODETYPE_OUTPUT = "OutputDevice"

#Enumeration for type of controll method
CONTROLMETHOD_POLL = "Poll"
CONTROLMETHOD_DEAMON = "Deamon"

VER_VALUE = "0.8"

# Different JSON Types
TYPE_REG = "REGISTER"
TYPE_AD = "ADVERTISE"
TYPE_PUB = "PUBLISH"
TYPE_CTL = "CONTROL"
TYPE_CTLPOLL = "POLLCONTROL"
TYPE_NOTIFY = "NOTIFY"
TYPE_SUB = "SUBSCRIBE"
TYPE_QUERY = "QUERY"
TYPE_GETCFG = "GETCONFIG"
TYPE_SAVEBLOCKLY = "SAVEBLOCKLY"
TYPE_GETBLOCKLY = "GETBLOCKLY"
TYPE_GETSUMMARY = "GETSUMMARY"
TYPE_DELETESTALE = "DELETESTALE"
TYPE_LOG = "LOG"

## DB constants
GLOBAL_DB_NAME = "thingspingion"

DB_CREDS_COLN = "credentials"
DB_REGS_COLN = "registrations"
DB_ADS_COLN = "advertisements"
DB_PUBLISHEE_COLN = "publisheddata"
DB_SUBSCRIPTIONS_COLN = "subscriptions"
DB_BLOCKLY_COLN = "blockly"
DB_CONFIG_COLN = "configs"
DB_CONTROL_POLL = "controlpoll"

## Response codes 
EXCP_FORBIDDEN_CODE = 403
EXCP_FORBIDDEN = "Forbidden"
EXCP_UNAUTH_CODE = 401 
EXCP_UNAUTH_INIT = "Provide Authentication"
EXCP_UNAUTH_FIN = "Authentication Failed" 
EXCP_NOTFOUND_CODE = 404
EXCP_NOTFOUND = "Not Found"
EXCP_BADFORMAT = 400

STATUS_OK = "OK"
STATUS_OK_CODE = 200

STATUS_ACCEPTED = "Accepted"
STATUS_ACCEPTED_CODE = 202

# Type of parameter - used in blockly and advertisements
PARAMTYPESTRING = "String"
PARAMTYPEBOOL = "Boolean"
PARAMTYPEFLOAT = "Float"
PARAMTYPEINT = "Integer"

DEFAULTEXPIRES = 3600
REREGTIME = DEFAULTEXPIRES/2

#Constant for config file & others
CKEY_DBNAME = "DbName"
CKEY_MODULENAME = "ModuleName"
CKEY_SELF_IP = "SELF_IP_ADDR"
CKEY_BASEPATH = "BasePath"
CKEY_FBSERVICEFILE = "FirebaseServiceFile"
CKEY_FBDBURL = "FirebaseUrl"
CKEY_POLLRESPPORT = "ControlPollPort"
CKEY_SERVERFQDN = "ServerFQDN"
CKEY_EVTCORD_HOST = "Eventcoordhost" 
CKEY_EVTCORD_KEY = "Eventcoordkey"
OSKEY_FBSERVICEFILE = "FIREBASESERVICEFILE"

def get_self_address():
    req_ip=None
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('100.1.1.255', 1))
        req_ip = s.getsockname()[0]
    except:
        from .userconfig import config
        req_ip = config[CKEY_SELF_IP]
    finally:
        s.close()
        return req_ip