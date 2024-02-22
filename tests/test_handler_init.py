#Test initalizing the system to receive and send a very simple test message

#This test message:
    #Is read every 5 minutes
    #Is sent via MQTT to the middle agent on new message 
    #Is also sent to the local database on a new message 

#Help from here: https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth

import sys
sys.path.append("../scarecro")
import json 
import logging 

### First, create the system object to see if we have active messages 

#Get the system config
import src.system.system as system_class 


system = {
    "id": "test_device",
    "addresses": [
        #"fake_receive_level_2",
        "fake_receive",
        #"fake_receive_level_3",
        #"fake_send_middle_agent"
    ]
}


#Need to come up with several message types and system classes 
system_object = system_class.return_object(system_config=system)
system_object.print_configs(["addresses", "messages", "carriers", "handlers"])

#system_object.print_routing_table()
