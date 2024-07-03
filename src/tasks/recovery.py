import time 
import os 
import logging  
#import shutil
from distutils.dir_util import copy_tree

import sys 
sys.path.append("../scarecro")
import system_object
import util.util as util 

#This might be better placed in the handler??? 
class DataRecovery:
    """
    This is the task super class. 
    Tasks may import most other modules (as well as other tasks)
    to run period system functionality. Sub classes may
    add functionality.
    """
    def __init__(self, config={}):
        """
        Initializes the task with configuration provided 
        """
        self.config = config.copy()
        self.duration = self.config.get("duration", )
        print("Initializing a System Update Class") 
        self.config_dir = "configs"
        self.backup_dir = "generated_data/backup_configs/"
        self.await_dir = "generated_data/awaiting_configs/"
                
    def send_recovery_data(self):
        #Pickup the recovery message
        #Not sure we even implement this function -- 
        # - this might be purely on the driver side? 
        #Get start and end dates 
        #Place into nice package 
        #Send as a message 
        #MQTT picks up - might not need a recovery task after all? 
        
        pass 

        

def return_object(config):
    return DataRecovery(config)