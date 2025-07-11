import time 
import logging 

#Get the system object and system config 
import system_object
import src.system.system as system_class 
#It's possible that logging is something you'll want to set on a system level
#This should do for now - marked for change 
logging.basicConfig(level=logging.INFO)
system_object.system = system_class.return_object()
system_object.system.init_ecosystem()
system_object.system.start_scheduler()
while True:
    time.sleep(15)
    pass 
