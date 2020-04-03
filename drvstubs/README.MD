This folder contains various files which serve two purposes :
   - Create dummy entities and do operations like registrations, advertisements, etc., 
   - Run test scripts

###Creating Credentials###
The IONMP protocol mandates that only authorized devices are allowed to participate in the comminication. For this to happen, the server needs to know about such authorized participants. In the current version, we do not have a UI for adding these authorized entities. Instead these values have to be added directly to the database. 

The createcredentials.py python file takes care of this. Just execute:
  'python3 createcredentials.py`
This will create the credentials of a few dummy devices. 

#### Testing Utility ####
To test the server for protocol compliance, we have a simple set of test utilities. 
Please note that this test utility is evolving over time and we are adding test features to this without much planning. Therefore, please don't expect it to be robust or user-friendly. 

The entry point of the test utility is the test_utility.py

This can be run with different options. Run the command with -h option and you will see the usage help on the screen. 
'
usage: test_utility.py [-h] [-ra] [-s SERVER] [-f FILE] [-nd] [-d DIR]

optional arguments:
  -h, --help            show this help message and exit
  -ra, --regall         Register all and run tests
  -s SERVER, --server SERVER
                        Address of server
  -f FILE, --file FILE  Choose an individual test file
  -nd, --nodbdelete     Do not clean up the db before starting tests
  -d DIR, --dir DIR     Run all files with extension of .json in the specified
'

The -f and -d options takes in a test file as the argument and runs a test based on the content of this file. The format of the test file is described below:

The file is a json file whose content is an array of json elements. The test utlity runs all these json elements in a sequential fashion. 
Each json element has one or more of the following keys:
**iondata** : A json element which represents the ION message that has to be sent to the server. 
        <details>
           <summary>Sample data for registration</summary>
           <pre>
              "iondata" : {      
                    "Type": "Register", 
                    "Expires" : 3600,
                    "From" : "10.1.1.18", 
                    "Nid" : "Idev1", 
                    "Key" : "keyIdev1", 
                    "Mid" : "Idev1_001",
                    "Time" : "$time"
                    }
           </pre>
         </details>

**exp** : This is an optional key. It is an array of elements that could either be strings or other json elements.

If the element is not defined, then the utility does not check for any values, it simply sends the data in the "iondata" element. This is usually done, if you are running this data as a precondition. 

If the element is a string, then it could have one of the following values:
- DBNOREGFOUND : The test utility checks the underlying mongo db Registrations collection and confirms that no registration for the passed entity exists. The entity here is the one that was sent in the iondata key.
- DBEXPIRES : Check whether the expiry parameter in the mongo db is set to a value which is  offset from the current value by a value that was specified in the Expires parameter of the previous iondata message.
- RESPEXPIRES - In this case, it checks whether the Expires parameter of the server's response matches the Expires parameter specified in "iondata"
- TYPEXYZ - Here XYZ is a number that represents the status message sent back in the "Type" field of the response. For example, if the field is set to TYPE200, then the utility verifies whether the response has its Type field set to 200. 

The element could also be an array of JSON elements. The keys of the JSON is as follows:
- Verify - The value of the Verify key will be a JSON which in turn has a Key value pair. 
The test utility will check if the server's response has a key-value pair which matches the key-value specified in the **Verify** key. 

 <details>
           <summary>Sample Verify for advertisement</summary>
           <pre>
            {
                "iondata" : {
                    "Ver" : "0.8", "Mid" : "query0011", 
                    "Type" : "QUERY",  "From" : "localhost",
                    "Nid"  : "querylocalhost",
                    "TargetId" : "Idev1", 
                    "Time" : "$time"
                }, 
                "exp" : [
                    {
                        "Verify" : {"Data" : [{  
                            "Name" : "MotionSensor1", "NodeType" : "Sensor", "Location" : "Front door", "Capabilities" :["Detect Motion"], "Return" : { 
                            "MotionDetected" : "Boolean"}, "Contact":"10.1.1.18", 
                            "Expires" : 3600, "Nid" : "Idev1"}]
                        }
                    }, "TYPE200"
                ]
            }
           </pre>
           <p>
           In the above test set, the test utility first sends out the Query Message as per the **iondata** message. It then checks two things in the response:
           -  A) If the response has a key called *Data* and if the value matches the dictionary specified in the *Verify* key
           -  B) Checks if the server returns a response whose type is set to 200
           </p>
         </details>

- Exclude - The other possible element in the **exp** key is the **Exclude** key. This key contains an array of Strings. This array represents the key's from the response which has to be removed before checking whether the response matches the expected value or not. Typically this is done for those fields which we don't care about in the current test. For example, the incoming Expires key could be set to a value which is a second or so less than the original request. That is because, the server might have taken a second since the original request was made. Likewise, we don't care about the server's time and we may want to exclude this from the test comparisons. 

#####Example format for test json files#####
The directories adtest and regtests have test data files. Take a look at these to get a better understanding of the format. 