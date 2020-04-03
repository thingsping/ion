import importlib, glob

importlib.import_module("iontest_helper")
from iontest_helper import *

def all_tests():
    pass_in = [1, 2, 3, 4, 5, 6, 7, 8 ]
    pass_out = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    reg_tpl_dict= { 
        "Type": "Register", "Expires" : 3600,
        "From" : "10.1.1.1$ctr", 
        "Nid" : "$devname", 
        "Key" : "key$devname", 
        "Mid" : "$devname_1",
        "Time" : "$time"
    }
    for ctr in pass_in:
        test_from_template(args.server, reg_tpl_dict, ctr, 200, "Idev{}".format(ctr))
        time.sleep(.01)

    for ctr in pass_out:
        test_from_template(args.server, reg_tpl_dict, ctr, 200, "Odev{}".format(ctr))
        time.sleep(.01)

    test_from_template(args.server, reg_tpl_dict, 8, 401, "Odev8", key="badkey", testname="Key for device name is wrong")
    test_from_template(args.server, reg_tpl_dict, 12, 403, "Odev12", testname="Output device not known to server")
    test_from_template(args.server, reg_tpl_dict, 12, 403, "Idev12", testname="Input device not known to server")

if __name__ == '__main__':
    args = get_args()
    print(args)
    failures = {}

    if not args.nodbdelete:
        print("Cleaning up database before tests")
        cleanup_db()

    try :        
        if args.regall:
            all_tests()
        elif args.file:
            print("Executing - {}".format(args.file))
            cur_failures=test_file(args.server, args.file)            
            if len(cur_failures) != 0 :
                failures[args.file] =  cur_failures
        elif args.dir:
            td = "{}/*.json".format(args.dir)
            reqd_files = glob.glob(td)
            for f in reqd_files :
                print("Executing - {}".format(f))
                cur_failures = test_file(args.server, f)
                if len(cur_failures) != 0 :
                    failures[f] = cur_failures
    except Exception as e:
        print(e)

    summary = get_results()
    print ("\n========================\n{{ \"Pass\":{}, \"Fail\":{}}}".format(summary[0], summary[1]))
    if len(failures) != 0 :
        print("\nDetails of failures:")
    for k,v in failures.items():
        # Value of each item will itself be a tuple of all failures of this test
        for failure in v :
            failstring = "For test - {} | Expected={}; Actual={}".format(k, failure[0], failure[1])
            print (failstring)
            
        
    print("========================")

    

    
