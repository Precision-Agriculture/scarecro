import time 
import os 
import json 
import logging  
from distutils.dir_util import copy_tree
from datetime import datetime, timedelta, tzinfo
from datetime import timezone
from datetime import date
import pytz
from dateutil import tz 

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
        logging.info("Initializing a System Update Class") 
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


    #Legacy - for python configs 
    # def write_to_file(self, config_folder, config_name, config_content):
    #     """
    #     Get config folder, name, and content
    #     And write the file to the configs director 
    #     """
    #     return_val = False
    #     try:
    #         #Might want to configure 
    #         full_name = f"{self.config_dir}/{config_folder}/{config_name}.py"
    #         content_to_write = f"config = {config_content}"
    #         file_handle = open(full_name, "w")
    #         file_handle.write(content_to_write)
    #         file_handle.close()
    #         logging.debug(f"Wrote {full_name}")
    #         return_val = True
    #     except Exception as e:
    #         logging.error(f"Could not write {config_name} {config_folder} to file; {e}", exc_info=True)
    #     return return_val
  

    def write_to_file(self, config_folder, config_name, config_content):
        """
        Get config folder, name, and content
        And write the file to the configs director 
        """
        return_val = False
        try:
            #Might want to configure 
            full_name = f"{self.config_dir}/{config_folder}/{config_name}.json"
            with open(full_name, "w") as file:
                json.dump(config_content, file, indent=4)
            logging.debug(f"Wrote {full_name}")
            return_val = True
        except Exception as e:
            logging.error(f"Could not write {config_name} {config_folder} to file; {e}", exc_info=True)
        return return_val

    def post_success_update_message(self, config_folder, config_name, config_id):
        try:
            time_utc = util.get_today_date_time_utc()
            msg = {
                "id": system_object.system.return_system_id(),
                "time": time_utc,
                "config_folder": config_folder,
                "config_name": config_name,
                "config_id": config_id
            }
            enveloped_message = system_object.system.envelope_message_by_type(msg, "local_config_updated")
            system_object.system.post_messages_by_type(enveloped_message, "local_config_updated")
        except Exception as e:
            logging.error(f"Could not post success message {config_folder} {config_name} {config_id}; e", exc_info=True)
    
    def check_back_up(self):
        """
        Back up the files if we don't already have a pending
        Update 
        """
        update_pending = system_object.system.return_system_updated()
        if update_pending == False:
            self.back_up_current_system()

    def update_files(self, message_type=None, entry_ids=[]):
        """
        Receives a 'fetched config' message from an on_message
        Trigger. Updates the configuration if it uses it. 
        """
        try:
            #First, back up if we don't have an update pending 
            self.check_back_up()
            #Then, see if we need to update 
            curr_updater = system_object.system.return_system_updater()
            messages = system_object.system.pickup_messages_by_message_type(message_type=message_type, entry_ids=entry_ids)
            for message in messages: 
                try:
                    #See if we need to update based on our updater file 
                    #Get the config id, config name, config folder
                    new_update_message = message.get("msg_content", {})
                    msg_config_folder = new_update_message.get("config_folder", None)
                    msg_config_id = new_update_message.get("config_id", None)
                    msg_config_name = new_update_message.get("config_name", None)
                    #If the keys match in the updater, make the update
                    updater_entry = curr_updater.get(msg_config_folder, {})
                    updater_match = updater_entry.get(msg_config_name, None)
                    if updater_match == msg_config_id:
                        msg_config_content = new_update_message.get("config_content", {})
                        if msg_config_content != {}: 
                            succ = self.write_to_file(msg_config_folder, msg_config_name, msg_config_content)
                            #If successful
                            if succ:
                                #Change the status to pending update  
                                system_object.system.set_system_updated(True)
                                #write a success message 
                                self.post_success_update_message(msg_config_folder, msg_config_name, msg_config_id)
                except Exception as e:
                    logging.error(f"Error running for {message}; {e}", exc_info=True)
        except Exception as e:
            logging.error(f"Error in update files task for {message_type}; {e}", exc_info=True)   
                 
   
        #Send an 'updated' succeed message
        #   -> Then reboot
        #If not, send an 'update failed' message
        # -> DON'T reboot 

    # def update_configs(self, message_type=None, entry_ids=[]): 
    #     """
    #     This function updates the configurations based on a 
    #     request to update. 
    #     """
    #     #First, pick up the request message 
    #     messages = system_object.system.pickup_messages_by_message_type(self, message_type=message_type, entry_ids=entry_ids)
    #     #In this case, only want most recent message, maybe? 
    #     #May want to change that in the future 
    #     recent_message = messages[-1]
    #     request_content = recent_message.get("msg_content", {})
    #     updates = request_content.get("updates", {})
    #     updater = updates.get("updater", [])
    #     #If we need to update everything, or update the updater file 
    #     update_succ = run_messages_through_handler
    #     if updates == {} or updater != []: 
    #         update_succ = self.update_updater_file()
    #     if update_succ: 
    #         #Go ahead and try to update everything
    #         if updates == {}:
    #             updates = system_object.system.return_system_updater()
    #         self.update_all_configs(updates)

        
#Main issue - how do we get new configs of any kind??? 
#Solve it by having the updater file pulled first and checking for any kinds of 
#New updates (if blank) - add to pulling updates. 


def return_object(config):
    return SystemUpdate(config)




# def get_configuration(self, config_folder, config_id): 
#         """
#         Get the stored configuration based on it's config_folder
#         And configuration ID 
#         """
#         #Might want to make this configured 
#         returned_config = {} 
#         collection_name = "configurations"
#         collection = self.get_collection(collection_name)
#         #Pull the bulk data 
#         query = {"config_id": config_id, "config_folder": config_folder}
#         try:
#             configuration = list(collection.find(query, {"_id": False}).limit(1))
#             if configuration == []:
#                 logging.debug(f"No configuration found")
#             else:
#                 returned_config = configuration[0]
#         except Exception as e:
#             self.reconnect()
#             logging.error(f'Issue with getting config {config_id} {config_folder}; {e}', exc_info=True)
#         return returned_config
            
#     def write_to_file(self, config_folder, config_name, config_content):
#         """
#         Get config folder, name, and content
#         And write to a file a the awaiting directory 
#         """
#         return_val = False
#         try:
#             #Might want to configure 
#             await_dir = "generated_data/awaiting_configs/"
#             full_name = f"{await_dir}{config_folder}{config_name}.py"
#             content_to_write = f"config = {config_content}"
#             file_handle = open(full_name, "w")
#             file_handle.write(content_to_write)
#             file_handle.close()
#             return_val = True
#         except Exception as e:
#             logging.error(f"Could not write {config_name} {config_folder} to file; {e}", exc_info=True)
            


#     def update_updater_file(self):
#         return_val = False
#         try:
#             curr_updater = system_object.system.return_system_updater()
#             updater_config = curr_updater.get("updater", {})
#             #This banks on the file being named "updater" - that is 
#             #A hard requirement 
#             updater_id = updater_config.get("updater", None)
#             new_updater_entry = self.get_configuration("updater", updater_id)
#             new_updater_config = new_updater_entry("config_content")
#             #Write it to file 
#             self.write_to_file("updater", "updater", new_updater_config)
#             system_object.system.set_system_updater(new_updater_config)
#         except Exception as e:
#             logging.error(f"Could not update updater file {e}", exc_info=True)

#     def update_all_configs(self, updates):
#         """
#         Updates all the configurations 
#         Need to change the control flow here
#         Since the gateways can't directly 
#         Interact with the database in mongo's case 
#         """
#         if updates != {}:
#             for folder, config_pairs in updates.items()
#                 for config_name, config_id in config_pairs.items():
#                     self.get_configuration(self, folder, config_id)
#                     self.write_to_file(folder, config_name, config_id)

    
#     def update_configs(self, message_type=None, entry_ids=[]): 
#         """
#         This function updates the configurations based on a 
#         request to update. 
#         """
#         #First, pick up the request message 
#         messages = system_object.system.pickup_messages_by_message_type(self, message_type=message_type, entry_ids=entry_ids)
#         #In this case, only want most recent message, maybe? 
#         #May want to change that in the future 
#         recent_message = messages[-1]
#         request_content = recent_message.get("msg_content", {})
#         updates = request_content.get("updates", {})
#         updater = updates.get("updater", [])
#         #If we need to update everything, or update the updater file 
#         update_succ = run_messages_through_handler
#         if updates == {} or updater != []: 
#             update_succ = self.update_updater_file()
#         if update_succ: 
#             #Go ahead and try to update everything
#             if updates == {}:
#                 updates = system_object.system.return_system_updater()
#             self.update_all_configs(updates)


        