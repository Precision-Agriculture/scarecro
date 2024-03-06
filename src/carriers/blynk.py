import sys
import time 
import requests
import logging 
import json 
import paho.mqtt.client as paho
from paho import mqtt
sys.path.append("../scarecro")
import system_object
import util.util as util 
#Help from the documentation here: https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#multiple


class Blynk():
    def __init__(self, config, send_addresses, receive_addresses, message_configs):
        """
        Blynk needs:
            url
            auth
            debug T/F?  
        """
        #arguments passed in 
        self.config = config 
        self.send_addresses = send_addresses 
        self.receive_addresses = receive_addresses
        self.message_configs = message_configs
        

    def receive(self, address_names):
        """
        Receives a list of addresses (all with same duration). Depending 
        on the duration and the address, it sets itself
        up to 'receive' spoofed messages and post them
        to the system post office along with an address 
        """
        pass


    def send(self, address_names, entry_ids=[]):
        """
        Takes in an optional list of entry ids
        Grabs the messages and publishes them, optionally filtering by ID 
        """
        pass 
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return Blynk(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)

