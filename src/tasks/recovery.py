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
        if os.path.exists(self.connection_filename):
            connection_info = self.get_connection_file()
            if connection_info.get("status", None) == "disconnect":
                logging.debug(f"Starting in disconnected state")
                self.connected = False
                system_object.system.set_system_lost_connection(True)
        else:
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

    def get_connection_file(self): 
        """
        Function takes no arguments and attempts 
        To get information stored in connection file 
        """
        logging.debug(f"Attempting to open {self.connection_filename}")
        with open(self.connection_filename, 'r') as opened_file:
            connection_info = json.load(opened_file)
        return connection_info

    def write_to_connection_file(self, write_dict): 
        """
        Function takes the dictionary to write back into the 
        connection file, and writes it to the connection file 
        """
        logging.debug(f"Writing disconnect to {self.connection_filename}")
        with open(self.connection_filename, 'w') as opened_file:
            json.dump(write_dict, opened_file, indent=4)

    def generate_connection_file_dict(self, status, message):
        """
        Takes connect/disconnect status and the message 
        And uses info to generate what should be written
        to the persistent connection file 
        """
        curr_time = util.get_today_date_time_utc()
        connection_dict = {
            "status": status,
            "time": message.get("time", curr_time)
        }
        return connection_dict.copy()

    def handle_disconnect(self, message):
        """
        If the system is disconnected, write it 
        to a file if it's not already disconnected. 
        """
        system_object.system.set_system_lost_connection(True)
        connection_dict = self.generate_connection_file_dict("disconnect", message)
        if self.connected:
            self.connected = False
        try:
            connection_info = {}
            connection_info = self.get_connection_file()
            status = connection_info.get("status")
            
            if status != "disconnect":
                logging.debug(f"Writing disconnect to {self.connection_filename}")
                self.write_to_connection_file(connection_dict)
        except Exception as e:
            logging.error(f"Issue opening connection file on disconnect {e}", exc_info=True)


    def recovery_data_request(self, lost_connection_dict, restored_connection_dict):
        """
        Sends a request for system recovery data based on the 
        time of lost connection and time of restored connection 
        """
        system_object.system.set_system_lost_connection(False)
        try:
            lost_connection_time = lost_connection_dict.get("time", False)
            restored_connection_time = restored_connection_dict.get("time", False)
            message_type = "recovery_data_request"
            recovery_data_request_message = {
                "id": system_object.system.return_system_id(),
                "time": util.get_today_date_time_utc(),
                "lost_connection_time": lost_connection_time,
                "restored_connection_time": restored_connection_time
            }
            #If both the times are valid 
            if lost_connection_time and restored_connection_time:
                enveloped_message = system_object.system.envelope_message_by_type(recovery_data_request_message, message_type)
                system_object.system.post_messages_by_type(enveloped_message, message_type)
        except Exception as e:
            logging.error(f"Could not post request for recovery data; {e}", exc_info=True)


    def handle_reconnect(self, message): 
        """
        If the system is reconnected, write it 
        to a file if it's not already reconnected. 
        """
        system_object.system.set_system_lost_connection(False)
        connection_dict = self.generate_connection_file_dict("reconnect", message)
        if self.connected == False:
            self.connected = True
        try:
            connection_info = {}
            connection_info = self.get_connection_file()
            status = connection_info.get("status")
            if status != "reconnect":
                self.write_to_connection_file(connection_dict)
                self.recovery_data_request(connection_info, connection_dict)
        except Exception as e:
            logging.error(f"Issue opening connection file on reconnect {e}", exc_info=True)
 
        #Send recovery data message 


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