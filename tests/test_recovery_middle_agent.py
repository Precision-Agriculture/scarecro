import sys
import time 
sys.path.append("../scarecro")
import logging 
import system_object
#Get the system config
import src.system.system as system_class 
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(asctime)s - %(message)s')
#logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
#Need to come up with several message types and system classes 

#What are we testing here?
#We need to see if the middle agent receives
# the recovery data message 
#And then if it probably routes the recovery data to the database 
#Test passed if receives messages (minus duplicates) with no floods
#Note on behavior - will not self-asess for duplicates, 
#Assumes that filtering has already occurred on a gateway level. 

system_config = {
    "id": "test_device_middle_agent",
    "addresses": [
        "cloud_mqtt_receive",
        "mongo_cloud_immediate",
        "cloud_mqtt_send_immediate" 
    ],
    "tasks":[
        "handle_recovery_data",
    ],
    #"updater": "updater"
}


#Init the 
system_object.system = system_class.return_object(system_config=system_config)
system_object.system.init_ecosystem()
system_object.system.start_scheduler()

while True:
    time.sleep(15)
    pass 

