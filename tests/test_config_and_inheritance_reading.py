import sys
sys.path.append("../scarecro")
import importlib 
import json 

### First, create the system object to see if we have active messages 

#Get the system config
import configs.system.system_config as system_config_file
import objects.system.system as system_class 
system_config = system_config_file.config
#Creta the system object 
system = system_class.return_object(system_config)

system.print_active_messages()



