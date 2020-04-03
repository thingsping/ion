import importlib

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
    cleanup_db()
    if args.regall:
        all_tests()
    elif args.file:
        test_file(args.server, args.file)
    summary = get_results()
    print ("\n========================\n{{ \"Pass\":{}, \"Fail\":{}}}\n========================".format(summary[0], summary[1]))

    
