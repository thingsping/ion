import pymongo

'''
Script to add credentials for sample entities. 
These entities are 'driver' entities which ar eonly used
for testing. There are two categories of entities:
    a) IdevX
    b) OdevX

Idev devices are input drivers , that is , to simulate sensors. 
Odev devices are output drivers, that is, to simulate actuators. 

'''

print("Establishing DB Connection...")
dbclient = pymongo.MongoClient("mongodb://localhost:27017/") 
db = dbclient["thingspingion"]
coln = db["credentials"]
coln.drop()
credsdata = [{
        "DevId" : "Idev1",
        "Key" : "keyIdev1", 
        "Name" : "PIR1", 
        "Type" : "PIR Motion Sensor", 
        "Owner" : None
    },
    {
        "DevId" : "Idev2",
        "Key" : "keyIdev2", 
        "Name" : "TemperatureSensor1", 
        "Type" : "DHT11", 
        "Owner" : None
    },
    {
        "DevId" : "Idev3",
        "Key" : "keyIdev3", 
        "Name" : "LightSensor1", 
        "Type" : "LightSensor", 
        "Owner" : None
    },
    {
        "DevId" : "Idev4",
        "Key" : "keyIdev4", 
        "Name" : "WaterLevel1", 
        "Type" : "Water Level", 
        "Owner" : None
    },
    {
        "DevId" : "Idev5",
        "Key" : "keyIdev5", 
        "Name" : "TiltSensor1", 
        "Type" : "Tilt Sensor", 
        "Owner" : None
    },
    {
        "DevId" : "Idev6",
        "Key" : "keyIdev6", 
        "Name" : "SoilSensor1", 
        "Type" : "Soil Sensor", 
        "Owner" : None
    }, 
    {
        "DevId" : "Idev7",
        "Key" : "keyIdev7", 
        "Name" : "GasSensor1", 
        "Type" : "Gas Sensor", 
        "Owner" : None
    },
    {
        "DevId" : "Idev8",
        "Key" : "keyIdev8", 
        "Name" : "SmokeSensor1", 
        "Type" : "Smoke Sensor", 
        "Owner" : None
    },
    {
        "DevId" : "Odev1",
        "Key" : "keyOdev1", 
        "Name" : "Exhaust Fan#1", 
        "Type" : "Exhaust Fan", 
        "Owner" : None
    },
    {
        "DevId" : "Odev2", 
        "Key" : "keyOdev2", 
        "Name" : "Fan1", 
        "Type" : "Fan", 
        "Owner" : None
    },
    {
        "DevId" : "Odev3",
        "Key" : "keyOdev3", 
        "Name" : "Buzzer1", 
        "Type" : "Buzzer", 
        "Owner" : None
    },
    {
        "DevId" : "Odev4", 
        "Key" : "keyOdev4", 
        "Name" : "Light1", 
        "Type" : "Light", 
        "Owner" : None
    },
    {
        "DevId" : "Odev5",
        "Key" : "keyOdev5", 
        "Name" : "Light2", 
        "Type" : "Light", 
        "Owner" : None
    },
    {
        "DevId" : "Odev6",
        "Key" : "keyOdev6", 
        "Name" : "LCD1", 
        "Type" : "2 Line LCD", 
        "Owner" : None
    },
    {
        "DevId" : "Odev7",
        "Key" : "keyOdev7", 
        "Name" : "Sms1", 
        "Type" : "SMS Gateway", 
        "Owner" : None
    },
    {
        "DevId" : "Odev8", 
        "Key" : "keyOdev8", 
        "Name" : "Left Music Player",
        "Type" : "Music Player",
        "Owner" : None
    },
    {
        "DevId" : "Odev9", 
        "Key" : "keyOdev9", 
        "Name:" : "Right Music Player", 
        "Type" : "Music Player",
        "Owner" : None
    },
    {
        "DevId" : "Odev10",
        "Key" : "keyOdev10", 
        "Name" : "Pump1", 
        "Type" : "Pump", 
        "Owner" : None
    },
    {
        "DevId" : "PiPlayer_1", 
        "Key" : "keyPiPlayer_1", 
        "Name" : "PiPlayer_1", 
        "Type" : "MediaPlayer", 
        "Owner" : None
    }
    
]

coln.insert_many(credsdata)
print("Number of Credential Items = {}".format(coln.count()))
