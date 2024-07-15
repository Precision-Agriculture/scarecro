
import sys
import time 
sys.path.append("../scarecro")
import json 
import logging 
import system_object


#Get the system config
import src.system.system as system_class 
#Need to come up with several message types and system classes 

system_config = {
    "id": "test_device",
    "addresses": [
        "datagator_mqtt_in",
        "datagator_mqtt_out",
    ]
}
system_object.system = system_class.return_object(system_config=system_config)
#Print the configurations 
system_object.system.init_ecosystem()

system_object.system.print_configs(["addresses", "messages", "carriers", "handlers"])

#Get carrier schedulers 
system_object.system.print_scheduler_dict()
system_object.system.print_on_message_routing_dict()
system_object.system.start_scheduler()

prev = time.time()
curr = time.time()
while True:
    time.sleep(15)
    pass 

#system_object.print_routing_table()
