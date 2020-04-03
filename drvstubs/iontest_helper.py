import importlib, time, requests,copy, json, pymongo, argparse

importlib.import_module("testconstants")
from testconstants import *

passcount = 0 
failcount = 0 
rtime = 0 

dbclient = pymongo.MongoClient("mongodb://localhost:27017/") 
db = dbclient[SITEDB]
coln_reg = db["registrations"]
coln_ad = db["advertisements"]
coln_publish = db["publish"]

def get_results():
    return (passcount, failcount)

def get_response(server, reg_req):
    global rtime
    if "Time" in reg_req : 
        rtime=reg_req["Time"]
    else :
        rtime = "NOTANNT"
    if rtime is not int:
        rtime = int(round(time.time()))
        reg_req["Time"] = rtime
    r = requests.post(server, json=reg_req)
    respjson = r.json()
    return respjson

def test_helper(server, regdata, allexp=None):
    global passcount, failcount, rtime
    resp = get_response(server, regdata)
    print (resp)
    if allexp :
        devid = regdata["Nid"]
        if "Expires" in regdata:
            expires = regdata["Expires"]
        else :
            expires = 3600
        for exp in allexp :
            #print(exp)
            if (exp == "DBNOREGFOUND"):                        
                res = coln_reg.find_one({"DevId" : devid})
                if res is None :
                    passcount = passcount + 1 
                else :
                    failcount = failcount + 1 
                    print("Expected that all registrations would "
                        "have been deleted, but found {}".format(res))
            elif (exp == "DBEXPIRES"): 
                res = coln_reg.find_one({"DevId" : devid})
                # Note : we need a grace time of 1 second. Even though it is the same
                # server, because we are using int and rounding off + given some time 
                # for communication, there sometimes is a one second difference
                if abs(rtime + expires - res["Expires"]) <= 1 :
                    passcount = passcount + 1
                else : 
                    failcount = failcount + 1 
                    print ("Expected expires = {}; Actual = {}"
                        .format(rtime+expires,res["Expires"] ))
            elif (exp == "RESPEXPIRES") :
                resp_expires = resp["Expires"]
                if(expires == resp_expires):
                    passcount = passcount + 1
                else :
                    failcount = failcount + 1
                    print("Expected expires = {}, actual={}".format(expires, resp_expires))
            elif (type(exp) == str and exp.startswith("TYPE")):
                resp_type = resp["Type"]
                req_type = int(exp[4:])
                if (resp_type == req_type):
                    passcount = passcount + 1
                else :
                    failcount = failcount + 1
                    print("Expected type={}, actual={}".format(req_type, resp_type))
            elif(type(exp) == dict):
                for k, v in exp.items() :
                    if k in resp:
                        reqdrespval = resp[k]
                        if (reqdrespval == v):
                            passcount = passcount + 1
                        else :
                            failcount = failcount + 1
                            print("Exp = {}\nAct={}".format(v, reqdrespval))
                    else :
                        print("Response does not have key {} at all".format(k))
                        failcount = failcount + 1

            else :
                print("Unknown exp value - {}".format(type(exp)))

def test_from_template(server, reg_tpl_dict, ctr, exp_code, devname, testname="", key=None):
    global passcount, failcount
    reg_dict = copy.deepcopy(reg_tpl_dict)
    for k, v in reg_tpl_dict.items() :
        newval = v 
        if ("$devname" in str(v)):
            newval = str(newval).replace("$devname", devname)
            reg_dict[k] = newval
        if ("$ctr" in str(v)):
            reg_dict[k] = v.replace("$ctr", str(ctr))
        if (v == "$time"):
            millis = int(round(time.time() * 1000))
            reg_dict[k] = millis
    if key is not None:
        reg_dict["Key"] = key
    #print(reg_dict)
        
    strsend = json.dumps(reg_dict, skipkeys=True)
    #strsend = strsend.replace('"', "'")    
    #print(strsend)
    r = requests.post(server,json=strsend)
    respjson = r.json()
    resptype = respjson["Type"]
    if resptype == exp_code : 
        passcount = passcount + 1
    else :
        failcount = failcount + 1
        print("For {}, expected = {}. Actual = {}".format(testname, exp_code, resptype))


def test_file(server, regfile):         
    with open(regfile) as json_file:  
        data = json.load(json_file)
        if (type(data) is list):
            for item in data:
                if ("iondata" in item):
                    regdata = item["iondata"]
                    exp = None
                    if ("exp" in item):
                        exp = item["exp"]
                    test_helper(server, regdata, exp)
                elif ("sleep" in item):
                    sltime = item["sleep"]
                    time.sleep(sltime)

        elif (type(data) is dict):
            if "regdata" in data:
                regdata = data["iondata"]
            else :
                regdata = data 
            if "exp" in data:
                exp = data["exp"]
            else:
                exp = None
            test_helper(server, regdata, exp)      

        else :
            print("Unknown content in file")


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-ra", "--regall",
      help="Register all and run tests", action="store_true")
    
    parser.add_argument("-s", "--server",
      help="Address of server",  default=DEFAULTSRV)

    parser.add_argument("-f", "--file", 
      help="Choose an individual test file", default="")
    
    return parser.parse_args()

def cleanup_db():
    coln_reg.drop()
    coln_ad.drop()
    coln_publish.drop()