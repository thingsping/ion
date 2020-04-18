import pymongo

print("Establishing DB Connection...")
dbclient = pymongo.MongoClient("mongodb://localhost:27017/") 
db = dbclient["mysiteion"]
coln = db["subscriptions"]
coln.drop()
subscriptions = [
    {
        "Creator" : "evt-cfgator", 
        "Event" : { 
                    "Location" : "Bedroom", "Name" : "LightSensor1", "Parameter" : "LightLevel", 
                    "Condition" : "<", "CondValue" : 3
                  },
        "Action" : [{ 
                     "Location" : "Bedroom", "Name" : "Light#2", "Parameters" : {"State": True}
                   }]    
    },
    {
        "Creator" : "evt-cfgator", 
        "Event" : { 
                    "Location" : "Tank", "Name" : "WaterLevel1", "Parameter" : "WaterLevel", "Condition" : "<", "CondValue" : 300
                  },
        "Action" : [
                   { 
                     "Location" : "Server", "Name" : "SMS Gateway", "Parameters" : {"Message" : "Water level too low", "Recipient" : "Raghu"}
                   },
                   {
                     "Location" : "Pump room", "Name" : "Main Pump", "Parameters" : {"State": True}
                   }
                   
                   ]         
    },
    {
        "Creator" : "evt-cfgator", 
        "Event" : { 
                    "Location" : "Kitchen", "Name" : "TemperatureSensor", 
                    "Parameter" : "Temperature", "Condition" : ">", "CondValue" : 28
                  },
        "Action" : [{ 
                     "Location" : "Kitchen", "Name" : "Exhaust Fan#1", 
                     "Parameters" : {"State" : True}
                   }]       
    },
    {
        "Creator" : "evt-cfgator", 
        "Event" : { 
                    "Location" : "Kitchen", "Name" : "TemperatureSensor", 
                    "Parameter" : "Temperature", "Condition" : "<", "CondValue" : 26
                  },
        "Action" : [{ 
                     "Location" : "Kitchen", "Name" : "Exhaust Fan#1", 
                     "Parameters" : {"State" : False}
                   }]       
    },
    {
        "Creator" : "evt-cfgator", 
        "Event" : { 
                    "Location" : "Bedroom", "Name" : "TiltSensor1", "Parameter" : "Tilt", 
                    "Condition" : ">", "CondValue" : 30
                  },
        "Action" : [{ 
                     "Location" : "Bedroom", "Name" : "Music Player", 
                     "Parameters" : {"Sound Track" : "lullaby.mp3"}
                   } ]       
    },
    {
        "Creator" : "evt-cfgator", 
        "Event" : { 
                    "Location" : "Kitchen", "Name" : "GasDetector1", "Parameter" : "Gas Detected", 
                    "Condition" : "==", "CondValue" : True
                  },
        "Action" : [{ 
                     "Location" : "Hall", "Name" : "Display#1", 
                     "Parameters" : {"Line1" : "*** CAUTION ***", "Line2" : "Gas Leakage Detected!"}
                   } ]       
    },
    {
        "Creator" : "evt-cfgator", 
        "Event" : { 
                    "Location" : "Kitchen", "Name" : "TemperatureSensor", 
                    "Parameter" : "Temperature", "Condition" : ">", "CondValue" : 28
                  },
        "Action" : [{ 
                     "Location" : "Kitchen", "Name" : "Exhaust Fan#1", 
                     "Parameters" : {"State" : True}
                   }]       
    },
    {
        "Creator" : "evt-cfgator", 
        "Event" : { 
                    "Location" : "Front door", "Name" : "RFReader", 
                    "Parameter" : "Card data", "Condition" : "==", "CondValue" : "VIPCARD"
                  },
        "Action" : [{ 
                     "Location" : "Front door", "Name" : "DoorLock", 
                     "Parameters" : {"State" : True}
                   }]       
    },
    {
        "Creator" : "evt-cfgator", 
        "Event" : { 
                    "Location" : "Bedroom", "Name" : "TiltSensor1", "Parameter" : "Tilt", 
                    "Condition" : ">", "CondValue" : 45
                  },
        "Action" : [{ 
                     "Location" : "Hall", "Name" : "Buzzer#1", 
                     "Parameters" : {
                         "Beep Time" : {"Name":"TiltSensor1","Location":"Bedroom","Parameter":"Tilt"},                      
                       "Interval" : 1}
                   } ]        
    },
    {
        "Creator" : "evt-cfgator", 
        "Event" : { 
                    "Location" : "Front door", "Name" : "MotionSensor1", "Parameter" : "MotionDetected", 
                    "Condition" : "==", "CondValue" : True
                  },
        "Action" : [{ 
                     "Location" : "Hall", "Name" : "Buzzer#1", 
                     "Parameters" : {"Beep Time" : 20, "Interval" : 1}
                   } ]      
    }
]
coln.insert_many(subscriptions)

print("Number of Subscription Items = {}".format(coln.count()))
