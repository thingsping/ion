import requests,json,time, copy,argparse, importlib, pymongo

importlib.import_module("testconstants")
from testconstants import *

reg_tpl_dict= { 
    "Type": "Register", "Expires" : 3600,
    "From" : "10.1.1.1$ctr", 
    "Nid" : "$devname", 
    "Key" : "key$devname", 
    "Mid" : "$devname_1",
    "Time" : "$time"
}
passcount = 0 
failcount = 0 

rtime = 0 

dbclient = pymongo.MongoClient("mongodb://localhost:27017/") 
db = dbclient[SITEDB]
coln = db["registrations"]


def test_registration(ctr, exp_code, devname, testname="", key=None):
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
        print("Key specified = {}".format(key))
        reg_dict["Key"] = key
    #print(reg_dict)
        
    strsend = json.dumps(reg_dict, skipkeys=True)
    #strsend = strsend.replace('"', "'")    
    #print(strsend)
    r = requests.post(args.server,json=strsend)
    respjson = r.json()
    resptype = respjson["Type"]
    if resptype == exp_code : 
        passcount = passcount + 1
    else :
        failcount = failcount + 1
        print("For {}, expected = {}. Actual = {}".format(testname, exp_code, resptype))

def get_reg_response(reg_req):
    global rtime
    if "Time" in reg_req : 
        rtime=reg_req["Time"]
    else :
        rtime = "NOTANNT"
    if rtime is not int:
        rtime = int(round(time.time()))
        reg_req["Time"] = rtime
    #print(reg_req)
    r = requests.post(args.server,json=reg_req)
    respjson = r.json()
    return respjson

def all_tests():
    pass_in = [1, 2, 3, 4, 5, 6, 7, 8 ]
    pass_out = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    for ctr in pass_in:
        test_registration(ctr, 200, "Idev{}".format(ctr))
        time.sleep(.01)

    for ctr in pass_out:
        test_registration(ctr, 200, "Odev{}".format(ctr))
        time.sleep(.01)

    test_registration(8, 401, "Odev8", key="badkey", testname="Key for device name is wrong")
    test_registration(12, 403, "Odev12", testname="Output device not known to server")
    test_registration(12, 403, "Idev12", testname="Input device not known to server")


def test_helper(regdata, allexp=None):
    global passcount, failcount, rtime
    resp = get_reg_response(regdata)
    print (resp)
    if allexp :
        devid = regdata["Nid"]
        expires = regdata["Expires"]
        for exp in allexp :
            #print(exp)
            if (exp == "DBNOREGFOUND"):                        
                res = coln.find_one({"DevId" : devid})
                if res is None :
                    passcount = passcount + 1 
                else :
                    failcount = failcount + 1 
                    print("Expected that all registrations would "
                        "have been deleted, but found {}".format(res))
            elif (exp == "DBEXPIRES"): 
                res = coln.find_one({"DevId" : devid})
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
            elif (exp.startswith("TYPE")):
                resp_type = resp["Type"]
                req_type = int(exp[4:])
                if (resp_type == req_type):
                    passcount = passcount + 1
                else :
                    failcount = failcount + 1
                    print("Expected type={}, actual={}".format(req_type, resp_type))


def test_file(regfile):        
    
    with open(regfile) as json_file:  
        data = json.load(json_file)
        if (type(data) is list):
            for item in data:
                regdata = item["regdata"]
                exp = None
                if ("exp" in item):
                    exp = item["exp"]
                test_helper(regdata, exp)

        elif (type(data) is dict):
            regdata = data["regdata"]
            test_helper(regdata, data["exp"])      

        else :
            print("Unknown content in file")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--all",
      help="Run all tests", action="store_true")
    
    parser.add_argument("-s", "--server",
      help="Server",  default=DEFAULTSRV)

    parser.add_argument("-f", "--file", 
      help="Choose an individual test file to add registrtion", default="")
    
    args = parser.parse_args()
    print(args)
    if args.all:
        all_tests()
    elif args.file:
        test_file(args.file)
            #get_reg_response(data)
    print ("{{ \"Pass\":{}, \"Fail\":{}}}".format(passcount, failcount))
