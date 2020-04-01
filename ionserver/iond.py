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

#probably an antipattern but simplest way not to break anything
# when trying to work with flask
# The following section is required to allow the server to be 
# called from flask
import os,sys
from pathlib import Path
from urllib.parse import urlparse

##is_from_module=os.environ['ISCCSHFROMMODUE'] # Don't use this
  # syntax - it throws keyerror
is_from_module=os.environ.get('ISCCSHFROMMODULE')
if (is_from_module != "True") :
  file = Path(__file__).resolve()
  parent, top = file.parent, file.parents[1]
  sys.path.append(str(parent))
  sys.path.append(str(top))
  packageFile = open("{}/packagefile".format(parent), "r")
  pfcont = packageFile.read()
  exec(pfcont)

  from .constants import *
  from .userconfig import config
  os.environ[OSKEY_FBSERVICEFILE] = "{}/{}".format(config[CKEY_BASEPATH],config[CKEY_FBSERVICEFILE]) 
  print("Running as WSGI for {}".format(config[CKEY_SERVERFQDN]))
else :
  from .constants import *
  from .userconfig import config
  os.environ[OSKEY_FBSERVICEFILE] = "./{}".format(config[CKEY_FBSERVICEFILE]) 
  print("Running as a local python module for {}".format(config[CKEY_SERVERFQDN]))
  

# Till here for allowing flask to run as WSGI
#######################################

from flask import Flask, abort, request
import json, time
from .Registrar import Registrar
from .AdManager import AdManager
from .Publishee import Publishee
from .HttpSender import HttpSender
from .DBManager import DBManager
from .HttpSender import HttpSender
from .constants import *
from .userconfig import config


app = Flask(__name__)
reg = None
ad = None
pub = None
lastespprinttime  = 0

@app.route("/", methods=['POST'])
def receive():
  global reg 
  global ad
  global pub
  global lastespprinttime

  retstring = "" 
  #print(format(request.data))
  if not request.json:    
    print ("Incoming data = {}".format(request.data))
    abort(400)  
  msg = request.json
  if (isinstance(msg, str)):
    print ("Incoming http is string coded! Try to convert...")
    try : 
      msg = json.loads(msg)
    except json.decoder.JSONDecodeError as je :
      print(je)
      abort(400)

  #clientip = request.environ['REMOTE_ADDR']
  headers = request.headers 
  #print(headers)
  #print(msg)
  referrer = request.referrer
  parsed_uri = urlparse(referrer)
  referrer = parsed_uri.netloc 
  freemem = None
  uptime= None
  if ( time.time() - lastespprinttime > 60):
    if ('X-freemem' in headers):
      freemem = headers['X-freemem']
    if ("X-uptime" in headers):
      uptime = headers['X-uptime']

    if freemem is not None:
      print("ESP Free memory = {}; Uptime = {} seconds".format(freemem, uptime) )
    lastespprinttime = time.time() 

  remoteaddr = request.remote_addr
  
  '''
  For certain types of requests like QUERY, SUBSCRIBE and NOTIFY
  we will only allow from localhost in the first version (till we 
  can address the security concerns). So find out if the request was
  from localhost or not
  '''
  if ( remoteaddr == "127.0.0.1" or remoteaddr == "localhost" ):
    isLocal = True
  else :
    isLocal = False 
  #print("Is local =  %s" %(isLocal))
  reqtype = msg[HDR_TYPE].upper()
  if (reqtype == TYPE_REG) :
    reg = Registrar.getRegistrar()
    reg.register(msg)
    retstring = reg.response() 
  elif (reqtype == TYPE_QUERY ) :
    devid = msg[HDR_TARGET]
    isallowed = True
    if (devid == '*' and not isLocal ):
      isallowed = False
    if (isallowed):
      ad = AdManager.get_AdManager() 
      ad.query(msg)
      retstring = ad.response() 
    else :
      retstring = "Unknown message type %s\n" %(reqtype)
      print("Received unknown message = {}, or invalid sender - {} or " \
        "invalid referrer - {}".format(reqtype, remoteaddr, referrer) )
  elif (reqtype == TYPE_AD):
    ad = AdManager.get_AdManager() 
    ad.post_ad(msg)  
    retstring = ad.response() 
  elif (reqtype == TYPE_PUB):
    pub = Publishee.get_publishee() 
    pub.receive_data(msg)
    retstring = pub.response() 
  elif (reqtype == TYPE_CTL and isLocal):
    tgturl = "http://{}".format(target)
    print("Send to {} -\n{}".format(tgturl, msg))
    threadname =  "ctlsender-{}-{}".format(HDR_MSGID, int(time.time()))
    sender = HttpSender(name = threadname)
    sender.setParameters("http://{}".format(target), msg)
    sender.start()
    sender.join()
    retstring = sender.get_response(threadname)
  elif (reqtype == TYPE_CTLPOLL):
    threadname = "ctlpoll-{}-{}".format(HDR_MSGID, int(time.time()))
    sender = HttpSender(name = threadname )
    ## In this case we don't care about setting the parameters 
    ## for the HttpSender class
    retstring = sender.process_poll_request(msg)

  elif (reqtype == TYPE_SAVEBLOCKLY and referrer==get_self_address()):
    del msg[HDR_TYPE]
    #print("Now going to save blockly config - {}".format(msg))
    filter = {HDR_NAME : msg[HDR_NAME]}
    DBManager.replace_one(DB_BLOCKLY_COLN, msg, filter)

    subscriptions = msg[DB_SUBSCRIPTIONS_COLN]; 
    for subscription in subscriptions:
      subscription[HDR_NAME] = msg[HDR_NAME]; 
    #print("subscriptions={}".format(subscriptions))
    DBManager.delete_many(DB_SUBSCRIPTIONS_COLN, filter)
    DBManager.insert_many(DB_SUBSCRIPTIONS_COLN, subscriptions)    
    retstring = "Saved!"

  elif reqtype == TYPE_GETBLOCKLY :
    if referrer==get_self_address() or referrer == config[CKEY_SERVERFQDN] or \
      remoteaddr==get_self_address():
      # Either referrer or sender has to be the same as this machine
      del msg[HDR_TYPE]
      dataarr = []
      datas = DBManager.find(DB_BLOCKLY_COLN)
      for data in datas : 
        if (data is not None):
          del data["_id"] # We don't wan't mongo's internal ID
          dataarr.append(data)
      #print("Result = {}".format(dataarr))
      retstring = json.dumps(dataarr, skipkeys=True)
    else :
      retstring = "Unknown message type %s\n" %(reqtype)
      print("Received unknown message = {}, or invalid sender - {} or " \
      "invalid referrer - {}".format(reqtype, remoteaddr, referrer) )  

  
  
  else : 
    retstring = "Unknown message type %s\n" %(reqtype)
    print("Received unknown message = {}, or invalid sender - {} or " \
      "invalid referrer - {}".format(reqtype, remoteaddr, referrer) )
  return retstring + "\n"
