from datetime import datetime
import pytz
import psutil
import re
import subprocess
import time 
#Help from here: https://stackoverflow.com/questions/276052/how-to-get-current-cpu-and-ram-usage-in-python
#https://stackoverflow.com/questions/42471475/fastest-way-to-get-system-uptime-in-python-in-linux
import logging
import sys 
sys.path.append("../scarecro")
import system_object
import util.util as util 
import socket 


class UnderlyingSystem():
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
        #Create a mapping dictionary from the additional info 
        self.mapping_dict = util.forward_backward_map_additional_info([self.send_addresses, self.receive_addresses])

    def add_id_to_reading(self, reading, address_name):
        """
        Adds the id from the configured carrier to the readings
        """
        #Get the id from the message 
        address_config = self.receive_addresses.get(address_name, {})
        msg_type = address_config.get("message_type", None)
        msg_config = self.message_configs.get(msg_type, {})
        msg_id = msg_config.get("id_field", "id")
        reading[msg_id] = self.config.get("id", "default")
        return reading 
        

    def status_reading(self):
        #Need to replace this with a system call - or else configured in the addresses?
        #Make new system keyword substitution - system_id 
        new_dict = {}
        try:
            utc_curr_time = datetime.now(tz=pytz.UTC)
            time_string = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            new_dict["time"] = time_string
            new_dict["cpu_usage"] = psutil.cpu_percent()
            new_dict["memory_free"] = round(psutil.virtual_memory().available*100/psutil.virtual_memory().total, 2)
            try:
                err, pitemp = subprocess.getstatusoutput("vcgencmd measure_temp")
                temp = re.search(r'-?\d.?\d*', pitemp)
                tempformatted = float(temp.group())
                #Internal Pi Temperature 
                new_dict["internal_temp"] = round(tempformatted, 1)
            except Exception as e:
                logging.error("Could not get internal temp", exc_info=True)
            #Get active ip addresses assigned to the system
            new_dict["ip_addresses"] = []
            try:
                host_address_dict = psutil.net_if_addrs()
                for hostname, host_dict in host_address_dict.items():
                    #Get address (entry index 1) of first snic tuple
                    broadcast_address = host_dict[0][1]
                    if ("docker" not in hostname) and (not broadcast_address == None) and (not any(character.isalpha() for character in broadcast_address)) and (broadcast_address != "127.0.0.1"):
                        #print(hostname)
                        #print(broadcast_address)
                        new_dict["ip_addresses"].append(broadcast_address)    
            except Exception as e:
                logging.error("Could not get ip addresses", exc_info=True)
            #uptime
            uptime = time.time() - psutil.boot_time()
            new_dict["uptime"] = round(uptime, 2)
            logging.info(f"Gateway Stats Reading: {new_dict}")
        except Exception as e:
            logging.error("Could not process gateway stats reading", exc_info=True)
            new_dict = {}
        return new_dict 


    def process_readings(self, address_names):
        try:
            #For each address
            for address_name in address_names:
                    #Find the function 
                    #function_name = self.address_key_mapping.get(address_name, None)
                    function_name = self.mapping_dict["function"]["address_name"][address_name]
                    if function_name == "status_reading": 
                        reading = self.status_reading()
                        #Add the id 
                        reading = self.add_id_to_reading(reading, address_name)
                        logging.info(f"Underlying System Reading {reading}")
                        enveloped_message = system_object.system.envelope_message(reading, address_name)
                        system_object.system.post_messages(enveloped_message, address_name)
        except Exception as e:
            logging.error(f"Issue processing readings for underlying system {e}")

    def disconnect(self): 
        """
        In current implementation, function takes no arguments
        And only prints a message to the console. 
        """
        logging.info("Disconnect Underlying System: No actions needed for Underlying System disconnect in this driver.") 

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
                    self.process_readings(address_names)
                    #Default time between tries 
                    time.sleep(300)
                except Exception as e:
                    logging.error(f"Issue processing readings ('always' duration) for underlying system {e}")
                    #Wait a bit before trying again 
                    time.sleep(300)    
        else:
            self.process_readings(address_names)
            
    def send(self, address_names, duration, entry_ids=[]):
        """
        Not really defined for this driver 
        Right now, driver only capable of listening on 433 radio,
        not sending
        """
        pass 
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return UnderlyingSystem(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)

         