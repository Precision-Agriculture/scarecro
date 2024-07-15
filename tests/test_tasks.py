
import sys
import time 
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
        "fake_receive_10_seconds",
        #"fake_receive_always",
        #"fake_receive_as_needed",
        "fake_send_on_message",
        #"fake_send_10_seconds",
        "fake_send_always",
    ],
    "tasks":[
        "fake_print_often"
    ]
}
system_object.system = system_class.return_object(system_config=system_config)
#Print the configurations 
system_object.system.init_ecosystem()
system_object.system.print_configs(["addresses", "messages", "carriers", "handlers", "tasks"])

# #Some other helpful prints
system_object.system.print_scheduler_dict()
system_object.system.start_scheduler()
# system_object.system.print_on_message_routing_dict()

prev = time.time()
curr = time.time()
while True:
    time.sleep(15)
    pass 

#system_object.print_routing_table()
