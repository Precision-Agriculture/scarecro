
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

def run_test_configuration(system_config):
    #Init the 
    system_object.system = system_class.return_object(system_config=system_config)
    system_object.system.init_ecosystem()
    system_object.system.start_scheduler()
    while True:
        time.sleep(15)
        pass 

