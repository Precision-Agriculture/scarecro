import sys
import time 
import logging 
import json 
sys.path.append("../scarecro")
import system_object
import util.util as util 

#Help from the documentation here: https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#multiple
class Printer():
    def __init__(self, config, send_addresses, receive_addresses, message_configs):
        """
        MQTT Clients need in the config: 
            mqtt_url: the url of the mqtt connection
            mqtt_port: the port of the mqtt connection. (Default 1883)
            mqtt_username: username for connection, defaults to None
            mqtt_password: password for connection, defaults to None
            client_id: client id of connection, very important to have 
            qos: qos of mqtt messages. Defaults to 1. 
        """
        #arguments passed in 
        self.config = config 
        self.send_addresses = send_addresses 
        self.receive_addresses = receive_addresses
        self.message_configs = message_configs 
        logging.info("Initialized printer carrier")


    def disconnect(self): 
        """
        In current implementation, function takes no arguments
        And only prints a message to the console. 
        """
        logging.info("Disconnect Printer: No actions needed for Printer disconnect in this driver.") 
        
    def send(self, address_names, duration, entry_ids=[]):
        """
        High level exposure function of the carrier
        Takes in an optional list of entry ids
        Grabs the messages and publishes them, optionally filtering by ID 
        No "always" duration is really defined for this driver, don't use with always 
        #Only on_message or duration 
        """
        for address_name in address_names:
            try:
                
                #Get the messages
                messages = system_object.system.pickup_messages(address_name, entry_ids=entry_ids)
                #Send each message individually 
                for message in messages:
                    content = message.get("msg_content", None)
                    message_type = message.get("msg_type", None)
                    print("**********************")
                    print("**********************")
                    print("**********************")
                    print("**********************")
                    print("CONTENT")
                    print(content)
            except Exception as e:
                logging.error(f"Could not publish message on address {address_name}", exc_info=True)
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return Printer(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)
