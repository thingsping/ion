import requests,json,time, copy


srv_addr="http://172.21.20.106:5000"

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

def get_reg_response(ctr, exp_code, devname, testname="", key=None):
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
    print(strsend)
    r = requests.post(srv_addr,json=strsend)
    respjson = r.json()
    resptype = respjson["Type"]
    if resptype == exp_code : 
        passcount = passcount + 1
    else :
        failcount = failcount + 1
        print("For {}, expected = {}. Actual = {}".format(testname, exp_code, resptype))




pass_in = [1, 2, 3, 4, 5, 6, 7, 8 ]
pass_out = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


for ctr in pass_in:
    get_reg_response(ctr, 200, "Idev{}".format(ctr))
    time.sleep(.01)

for ctr in pass_out:
    get_reg_response(ctr, 200, "Odev{}".format(ctr))
    time.sleep(.01)

get_reg_response(8, 401, "Odev8", key="badkey", testname="Key for device name is wrong")
get_reg_response(12, 403, "Odev12", testname="Output device not known to server")
get_reg_response(12, 403, "Idev12", testname="Input device not known to server")

print ("Summary. Pass={}, Fail={}".format(passcount, failcount))

#

#print(r)