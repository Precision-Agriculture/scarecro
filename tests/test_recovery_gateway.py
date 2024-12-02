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
#We have some readings coming in regularly.
#We disconnect power in the middle and/or restart the program
#We see if the system sends itself a disconnect message
#We see if the system sends itself a reconnect message
#We see if the system sends a request for recovery data
#We see if the system sends up the recovery data for what
#It collected while it was out of connection 

#It needs to have all these things happen to pass its test 
#Situations
#Start with power - lose power - regain power
#Start without power - regain power
#Start without power - reboot - start without power - regain power - PASS
#Start without power - reboot - start with power
#Start with power - reboot - start without power - regain power 
#Tests with multiple message types
#Test with multiple gateways 


system_config = {
    "id": "test_device",
    "addresses": [
        #To gather some data 
        "gateway_stats_in",
        #"bmp280_in",
        #To send the data immediately - so can track
        "cloud_mqtt_send_immediate",
        #So we can locally store the data 
        "mongo_local_immediate"

    ],
    "tasks":[
        #For detecting the connection change
        "handle_connection_change",
        #For recovering the data 
        "handle_request_for_recovery_data"
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

