This folder contains various files which serve two purposes :
   - Create dummy entities and do operations like registrations, advertisements, etc., 
   - Run test scripts

### Creating Credentials ###
The IONMP protocol mandates that only authorized devices are allowed to participate in the comminication. For this to happen, the server needs to know about such authorized participants. In the current version, we do not have a UI for adding these authorized entities. Instead these values have to be added directly to the database. 

The createcredentials.py python file takes care of this. Just execute:
  'python3 createcredentials.py`
This will create the credentials of a few dummy devices. 

### Testing Utility ###
To test the server for protocol compliance, we have a simple set of test utilities. 
Please note that this test utility is evolving over time and we are adding test features to this without much planning. Therefore, please don't expect it to be robust or user-friendly. 

The entry point of the test utility is the test_utility.py

This can be run with different options. Run the command with -h option and you will see the usage help on the screen. 

```
usage: test_utility.py [-h] [-ra] [-s SERVER] [-f FILE] [-nd] [-do] [-d DIR]

optional arguments:
  -h, --help            show this help message and exit
  -ra, --regall         Register all and run tests
  -s SERVER, --server SERVER
                        Address of server
  -f FILE, --file FILE  Choose an individual test file
  -nd, --nodbdelete     Do not clean up the db before starting tests
  -do, --deleteonce     Cleanup the DB only once before running all tests.
                        Without this the db will get deleted before each test
  -d DIR, --dir DIR     Run all files with extension of .json in the specified
                        directory

 
```

The -f and -d options takes in a test file as the argument and runs a test based on the content of this file. The format of the test file is described below:

The file is a json file whose content is an array of json elements. The test utlity runs all these json elements in a sequential fashion. 
Each json element has one or more of the following keys:

- **iondata** : A json element which represents the ION message that has to be sent to the server. 
    - <details>
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

- **exp** : This is an optional key. It is an array of elements that could either be strings or other json elements.

    If the element is not defined, then the utility does not check for any values, it simply sends the data in the "iondata" element. This is usually done, if you are running this data as a precondition. 

    If the element is a string, then it could have one of the following values:
    - DBNOREGFOUND : The test utility checks the underlying mongo db Registrations collection and confirms that no registration for the passed entity exists. The entity here is the one that was sent in the iondata key.
    - DBEXPIRES : Check whether the expiry parameter in the mongo db is set to a value which is  offset from the current value by a value that was specified in the Expires parameter of the previous iondata message.
    - RESPEXPIRES - In this case, it checks whether the Expires parameter of the server's response matches the Expires parameter specified in "iondata"
    - TYPEXYZ - Here XYZ is a number that represents the status message sent back in the "Type" field of the response. For example, if the field is set to TYPE200, then the utility verifies whether the response has its Type field set to 200. 

    The element could also be an array of JSON elements. The keys of the JSON is as follows:
    - Verify - The value of the Verify key will be a JSON which in turn has a Key value pair. 
    The test utility will check if the server's response has a key-value pair which matches the key-value specified in the **Verify** key. 

        - <details>
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

- **meta** : Optional but recommended key. A json element that describes about this test. As on the current date of writing, this key is just discarded. We intend to use it in future when the number of tests grows quite a bit and we have a more robust testing mechanism. The JSON Element has two keys:
    - **Name** : A short name for the test
    - **Desc** : A detailed description about the test 
    
##### Example format for test json files #####
The directories adtest and regtests have test data files. Take a look at these to get a better understanding of the format. 

### Running Tests ###
The scripts and test files in the drvstubs directory are used to run various tests. 

First cd to drvstubs directory 
Then create the required credentials as mentioned in the section about credentials. That is, 
   ```python3 createcredentials.py```
and run the tests as mentioned below:

#### Registration Tests ####

Registrations tests are executed to simulate the condition where entities try to register with the ION server. To run registration tests, you have to run the test utility script twice with different options:

- Create registrations for all entities
```
    python3 test_utility.py -ra 
```
    If all goes well you should see all tests passed (21 as of current writing)
    
```
    ========================
    { "Pass":21, "Fail":0}
    ========================
```
- Run other registration tests
```
    python3 test_utility.py -d regtests
```
This should again show that all tests have passed and zero failed 
```
   ========================
   { "Pass":17, "Fail":0}
   ========================
```
If you are wondering why there are two sets of testts, that is because we started writing the test utility as a bunch of scripts to quickly vefify the communication. Later we started adding more features and made it more robust. Overtime, we will make -ra go away and have test templates for these too. 

#### Advertisements Tests ####

Advertisement tests are used to simulate both registered and unregistered endpoints trying to advartise their capabilities to the server. Run advertisement tests by calling the python script:

```
    python3 test_utility.py -d adtests
```
All tests should pass with zero failures
```
    ========================
    { "Pass":35, "Fail":0}
    ========================

```
#### PUBLISH tests ####

Run the utility:
```
    python3 test_utility.py -d pubtests
```
This will simulate the ability of sensor nodes to publish data to the server and the server's ability to process these messages. After you run the tests, if you see that all **but one** tests have passed, then you are all good!
```
   ========================
   { "Pass":40, "Fail":1}

   Details of failures:
   For test - pubtests/pub_multithing_samenames.json | Expected={'State': False}; Actual={'State': True}
   ========================
```
The lone failure is due to the protocol issue : https://github.com/thingsping/IONMP/issues/3

#### Tests for confirming the event-action relationships ####
In our IONSERVER, we have not yet implemented the SUBSCRIBE-NOTIFY technique of the IONMP protocol for managing events and their associated approach. Instead we directly define the event-action relationship in the database. The server has an Event Coordinator component which continously checks if there is an event that would trigger an action. If yes, then it does the needful. 
In the tests, we have to do a few steps to verify this:

    - create the subscription database
    
    ``` 
    Run the script
    python3 createcredentials.py
    ```
    
    You should see the message 
    ```
    Establishing DB Connection...
    Number of Subscription Items = 10
    ```
    - Now create a the registrations and advertisements required for running all scripts
     ```
      python3 test_utility.py -f subscribes/subscribe_entities
     ```
      All tests should pass. Please note that these are not tests as such, but they are preconditions. These steps are required to ensure that all entities have been setup as required. At the end of these preconditions, we also have a bunch of POLLCONTROL messages, to ensure that there are no 'residual unconsumed` actions before the start of the tests. 
     
     ```
      ========================
      { "Pass":10, "Fail":0}
      ========================
      ```
     - The first step after this is to run the set of tests which rely on the entities having been setup as mentioned in the previous step.  To do so run the the tests      
     
     ```
      python3 test_utility.py -nd -d subscribes_nodeldb
     ```
      Observe here that we are passing the parameter ```-nd``` to the script. This ensures that the database is not cleaned up before the tests are run. Without this option, the database is cleaned up before the start of each test. 
      The above set of tests verify all possible scenaris of event-action relationship . Once you run the tests you should see that all tests have passed as seen below:
     ```
     ========================
     { "Pass":38, "Fail":0}
     ========================
     ```
     - Finally run those event-action relationship tests that need the database to be be cleaned before running the tests 
     
     ```
     python3 test_utility.py -d subscribes/
     ```
     
     After you run these tests, you should confirm that all tests have passed and none of the tests have failed. 
     ```
     ========================
      { "Pass":5, "Fail":0}
     ========================
     ```


     


