import sys
import time 
import logging 
import json 
sys.path.append("../scarecro")
import system_object
import util.util as util 


class TempestUDP():
    """
    Driver for Getting Underlying System Info .
    """
    def __init__(self, config, send_addresses, receive_addresses, message_configs):
        """
        This driver doesn't really need anything configuration-wise
        String matches and drivers are provided on an address level 
        """
        #For mongo, need to know if gateway or middle agent
        #Because gateways use slightly outdated version. 
        self.config = config.copy()
        self.send_addresses = send_addresses.copy()
        self.receive_addresses = receive_addresses.copy()
        self.message_configs = message_configs.copy()
        logging.info("Initialized Tempest UDP Carrier")


    def status_reading(self):
        message = {
            "dummy_message": 1
        }
        return message.copy() 
   
    def receive(self, address_names, duration):
        """
        Takes in the address names and the duration
        For this driver, the duration will pretty much always be 'always'
        You could potentally define other behavior, like listening 
        for a set amount of time.  
        """
        if duration == "always":
            while True:
                try:
                    for address_name in address_names:
                        reading = self.status_reading()
                        logging.info(f"Tempest UDP Reading, {reading}")
                        enveloped_message = system_object.system.envelope_message(reading, address_name)
                        system_object.system.post_messages(enveloped_message, address_name)
                    #Default time between tries 
                    time.sleep(300)
                except Exception as e:
                    logging.error(f"Issue processing readings ('always' duration) for underlying system {e}")
                    #Wait a bit before trying again 
                    time.sleep(300)    

    def send(self, address_names, duration, entry_ids=[]):
        """
        Not really defined for this driver 
        Right now, driver only capable of listening on 433 radio,
        not sending
        """
        pass 
            
 
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return TempestUDP(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)

         