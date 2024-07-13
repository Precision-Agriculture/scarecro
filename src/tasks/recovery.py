import time 
import os 
import logging  
import json 

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
        self.connected = True 
        self.current_directory = os.getcwd()
        self.connection_filename = config.get("connection_filename", "generated_data/connection_info.json")
        self.connection_filepath = f"{self.current_directory}/{self.connection_filename}"
        #Create the connection file if it doesn't exist already 
        curr_time = util.get_today_date_time_utc()
        connection_dict = {
            "status": "reconnect",
            "time": curr_time
        }
        if not os.path.exists(self.connection_filename):
            with open(self.connection_filepath, 'a+') as opened_file:
                json.dump(connection_dict, opened_file, indent=4)

    def send_recovery_data(self):
        #Pickup the recovery message
        #Not sure we even implement this function -- 
        # - this might be purely on the driver side? 
        #Get start and end dates 
        #Place into nice package 
        #Send as a message 
        #MQTT picks up - might not need a recovery task after all? 
        pass 

    def handle_disconnect(self, message):
        """
        If the system is disconnected, write it 
        to a file if it's not already disconnected. 
        """
        curr_time = util.get_today_date_time_utc()
        connection_dict = {
            "status": "disconnect",
            "time": message.get("time", curr_time)
        }
        if self.connected:
            self.connected = False
        try:
            connection_info = {}
            logging.debug(f"Attempting to open {self.connection_filename}")
            with open(self.connection_filename, 'r') as opened_file:
                connection_info = json.load(opened_file)
            status = connection_info.get("status")
            
            if status != "disconnect":
                logging.debug(f"Writing disconnect to {self.connection_filename}")
                with open(self.connection_filename, 'w') as opened_file:
                    json.dump(connection_dict, opened_file, indent=4)
        except Exception as e:
            logging.error(f"Issue opening connection file {e}", exc_info=True)

    def handle_reconnect(self, message): 
        pass 

    def handle_connection_message(self, message_type=None, entry_ids=[]): 
        """
        Get a connection message passed in by the 
        on_message trigger, and take action based on it. 
        """ 
        messages = system_object.system.pickup_messages_by_message_type(message_type=message_type, entry_ids=entry_ids)
        for message in messages: 
            #Get the content 
            msg = message.get("msg_content", {})
            connection_status = msg.get("connection_status", None)
            #See what kind of connection status and take 
            #The appropriate action 
            if connection_status == "disconnect":
                logging.debug("Disconnect message received")
                self.handle_disconnect(msg) 

            elif connection_status == "reconnect":
                logging.debug("Reconnect message received")
                self.handle_reconnect(msg) 

def return_object(config):
    return DataRecovery(config)