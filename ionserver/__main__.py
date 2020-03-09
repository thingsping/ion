# -*- coding: utf-8 -*-
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

import sys, argparse, json, os, subprocess, time, requests, psutil
from flask import Flask, abort, request
from .BlockGenerator import *
from .userconfig import config
from .constants import * 

app = Flask(__name__)

if __name__ == '__main__':
    print("Starting as standalone script...")
    os.environ['ISCCSHFROMMODULE']='True'
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--daemon",
      help="Start as a service", action="store_true")
    parser.add_argument("-b", "--blockly",
      help="Generate blockly files", action="store_true")
    parser.add_argument("-f", "--file",
      help="Specify file",  default="")
    parser.add_argument("-p", "--pattern", 
      help="Generate from a pattern", default="")
    parser.add_argument("-t", "--target",
      help="Specify target directory where Blockly UI is present",  default=".")
    parser.add_argument("-D", "--database", 
      help="Read from database", action="store_true")
    parser.add_argument("-u", "--pollserver",
      help = "Poll server which repsonds to client when a control message is avaialble", 
      action="store_true")

    args = parser.parse_args()
    print(args)
    if args.daemon:
      path = os.path.dirname(__file__)
      print ("Starting as deamon from %s" %(path))
      os.environ["FLASK_APP"] = path + "/iond.py"
      flargs = ['flask', 'run', '--host=0.0.0.0']
      #flargs = ['flask', 'run']
      subprocess.call(flargs) 

    elif args.blockly:
      print("Generating blockly files..");
      print (args.file) 
      print (args.pattern)
      if ((args.file and args.pattern) or (args.file and args.database) 
          or (args.pattern and args.databse)) :
        print ("Can only specifiy one of - Database, target or File")
      elif args.file :
        jf = args.file
        print("Picking up from file={}".format(jf) )
        dct = fromJsonFile(jf)[1]
        #print(dct)
      elif args.pattern:
        jd = args.pattern 
        fromPattern(jd, args.target)
      elif args.database :
        fromDB(args.target)

    elif args.pollserver:
      from .UdpPollResponder import *
      launch_pollserver()

    elif args.watchdog:
      #NOTE : For testing watchdog, use the same tests as that of mediaserver. 
      # Later on we'll write separately
      running_process=None
      shouldStart = False
      module_name = config[CKEY_MODULENAME]
      print ("Module from config = {}".format(module_name))
      
      