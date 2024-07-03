import time 
import os 
import logging  
#import shutil
from distutils.dir_util import copy_tree

import sys 
sys.path.append("../scarecro")
import system_object
import util.util as util 

class SystemUpdate:
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
        self.duration = self.config.get("duration", "always")
        print("Initializing a System Update Class") 
        self.config_dir = "configs"
        self.backup_dir = "generated_data/backup_configs/"
        self.await_dir = "generated_data/awaiting_configs/"
                
    def back_up_current_system(self):
        """
        This backs up the current system to a folder 
        generated_files/backup_configs/
        """
        #This works SUPER well.
        #Will override with each backup I believe. 
        copy_tree(self.config_dir, self.backup_dir)

    def restore_system_from_backup(self):
        """
        This copies the current backup 
        to the configs folders, restoring an original image 
        """
        #TODO: Make sure this directory exists first,
        #And is filled before doing! 
        copy_tree(self.backup_dir, self.config_dir)

    def request_updates(self, config_ids=[]):
        #If config ids is an empty list, write EVERYTHING 
        #In the update list. 
        #Otherwise - check if the config
        #Check configs on wake up?  
        #Send a message requesting the new updates 
        pass 
        
    def update_files(self):
        pass 
        #Wait, with a timeout, for the updated configs to populate a given folder 
        #If the updates populate in the folder, copy them over
        #copy_tree(self.await_dir, self.config_dir)
        #Send an 'updated' succeed message
        #   -> Then reboot
        #If not, send an 'update failed' message
        # -> DON'T reboot 
        
#Main issue - how do we get new configs of any kind??? 
#Solve it by having the updater file pulled first and checking for any kinds of 
#New updates (if blank) - add to pulling updates. 

#Rest of update stuff going to have to deal with MongoDB 

def return_object(config):
    return SystemUpdate(config)