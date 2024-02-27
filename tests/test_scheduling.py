
import sys
sys.path.append("../scarecro")
import json 
import logging 

from apscheduler.schedulers.background import BackgroundScheduler
import apscheduler.events
import system_object


#Get the system config
import src.system.system as system_class 
#Need to come up with several message types and system classes 

system_config = {
    "id": "test_device",
    "addresses": [
        "fake_receive",
    ]
}
system_object.system = system_class.return_object(system_config=system_config)
#Print the configurations 


system_object.system.print_configs(["addresses", "messages", "carriers", "handlers"])

#See if the scheduler works with fake receiver address 
system_object.system.print_scheduler_dict()
system_object.system.print_on_message_routing_dict()

while True:
    pass 

