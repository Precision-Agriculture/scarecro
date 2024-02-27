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
        "fake_receive",
    ]
}


#Need to come up with several message types and system classes 
system_object = system_class.return_object(system_config=system)
system_object.print_configs(["addresses", "messages", "carriers", "handlers"])

#system_object.print_routing_table()
