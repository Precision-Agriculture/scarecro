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
class DataGatorOTA:
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
                
    def get_new_gator_ota(self):
        pass 
        #Do what we need to do to get the new datagator
        #Image hosted 
        #Once it's in there
        #Send a received message 
        
#Main issue - how do we get new configs of any kind??? 
#Solve it by having the updater file pulled first and checking for any kinds of 
#New updates (if blank) - add to pulling updates. 

#Rest of update stuff going to have to deal with MongoDB 

def return_object(config):
    return DataGatorOTA(config)