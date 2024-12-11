
import sys
import time 
sys.path.append("../scarecro")
import json 
import logging 

from apscheduler.schedulers.background import BackgroundScheduler
import apscheduler.events
import system_object


#Get the system config
import logging
import src.system.system as system_class 

#Need to come up with several message types and system classes 
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(asctime)s - %(message)s')

system_config = {
    "id": "test_device",
    "addresses": [
        "gateway_stats_in",
        "mongo_local_immediate",
        "datagator_basic_sensors_in"
    ],
}
system_object.system = system_class.return_object(system_config=system_config)
#Print the configurations 
system_object.system.init_ecosystem()
system_object.system.print_configs(["addresses", "messages", "carriers", "handlers", "tasks"])

# #Some other helpful prints
system_object.system.print_scheduler_dict()
system_object.system.start_scheduler()
# system_object.system.print_on_message_routing_dict()

time.sleep(20)
print("Attempting to disconnect carriers")
system_object.system.disconnect_carriers()
time.sleep(15)


