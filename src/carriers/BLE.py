import sys
import time 
import logging 
import json 
import logging 
sys.path.append("../scarecro")
import system_object
import util.util as util 
import asyncio
from bleak import BleakScanner, BleakClient
import os 

if logging.root.level > logging.DEBUG:
    logging.getLogger('bleak.backends.bluezdbus.scanner').setLevel(logging.WARNING)
else:
    logging.getLogger('bleak.backends.bluezdbus.scanner').setLevel(logging.INFO)

#Help from the documentation here: https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#multiple
#We can probably make this a lot better! 

class BLE():
    def __init__(self, config, send_addresses, receive_addresses, message_configs):
        """
        Bluetooth needs to know on config level:
        1.The method of connection - beacon or write_read?
        2.listening_interval (default)

        On address level needs to know: 
        1. uuid of data to read 
        2. uuid of data to write AND data to write, if applicable 
        3. (optional) list of Mac address to filter by
        4. String match if connection not needed. 
        5. Connection (T/F) Needed to read the sensor 
        """
        #arguments passed in 
        self.config = config 
        self.send_addresses = send_addresses 
        self.receive_addresses = receive_addresses
        self.message_configs = message_configs
        #Necessary methods for the BLE program 
        self.read_method = self.config.get("read_method", None)
        self.listening_interval = self.config.get("listening_interval", 30)
        self.create_mappings()
        logging.info("Initialized BLE carrier")
        self.working_mac = None 
        self.working_address = None 

    def create_mappings(self):
        """
        Takes no arguments
        Uses send and receive addresses to create mappings
        """
        address_info_mapping = {} 
        match_address_mapping = {}
        mac_address_mapping = {}
        address_match_mapping = {}
        address_mac_mapping = {}
        all_addresses = {**self.send_addresses, **self.receive_addresses}
        for address_name, address_config in all_addresses.items():
            address_info = address_config.get("additional_info", {})
            info_dict = {}
            data_uuid = address_info.get("data_uuid", None)
            #string_match = address_info.get("string_match", None)
            connection = address_info.get("connection", False)
            write_uuid = address_info.get("write_uuid", None)
            data_to_write = address_info.get("data_to_write", None)
            mac_addresses = address_info.get("mac_addresses", [])
            info_dict = {
                "data_uuid": data_uuid,
                #"string_match": string_match,
                "connection": connection,
                "write_uuid": write_uuid,
                "data_to_write": data_to_write,
                "mac_addresses": mac_addresses
            }
            address_info_mapping[address_name] = info_dict.copy()
            if data_uuid:
                match_address_mapping[data_uuid] = address_name
                address_match_mapping[address_name] = data_uuid
            for individual_mac in mac_addresses:
                mac_address_mapping[individual_mac] = address_name
            address_mac_mapping[address_name] = mac_addresses
        self.address_info_mapping = address_info_mapping
        self.match_address_mapping = match_address_mapping
        self.mac_address_mapping = mac_address_mapping
        self.address_match_mapping = address_match_mapping
        self.address_mac_mapping = address_mac_mapping
        

    def receive(self, address_names, duration):
        """
        Receives a list of addresses and the duration. Depending 
        on the duration and the address, it sets itself
        up to 'receive' messages and post them
        to the system post office along with an address 
        """
        if self.read_method == "beacon":
            logging.debug("Beacon mode")
            self.run_scanner(address_names, duration)
        if self.read_method == "write_read": 
            logging.debug("Write Read Mode")
            self.run_write_read(address_names, duration)


    def beacon_callback(self, device, advertising_data):
        """
        Callback registered for a given scanner. 
        Takes in the device and the advertising data 
        Posts the message if applicable 
        """
        logging.debug("In Beacon Callback")
        name = device.name   
        address = device.address
        rssi = device.rssi 
        service_data_dict = advertising_data.service_data
        true_packet = False
        #If if it has a data_uuid we are looking for 
        #Might want to configure address-dynamic self matches? Kills reusability a bit
        for match in self.matches:
            if match not in list(service_data_dict.keys()):
                continue 
            packet = service_data_dict.get(match, None)
            if packet: 
                logging.debug(f"Found a matching packet!")
                #Get the address this refers to 
                address_name = self.match_address_mapping.get(match, None)
                mac_addresses = self.address_mac_mapping.get(address_name, None)
                #Optionally filter by mac address
                if address in mac_addresses or mac_addresses == [] or mac_addresses == None:
                    true_packet = True
                #If it meets the mac filter requirement, or if it has no mac filter requirements 
                if true_packet:
                    message = {
                        "name": name,
                        "mac_address": address,
                        "rssi": rssi,
                        "packet": packet
                    }
                    try:
                        enveloped_message = system_object.system.envelope_message(message, address_name)
                        system_object.system.post_messages(enveloped_message, address_name)
                    except Exception as e:
                        logging.debug(f"Could not post BLE Beacon message for reason {e}", exc_info=True)
                    break 
     

    def get_matches(self, address_names):
        matches = []
        #Put together a list of string matches
        for address_name in address_names:
            match = self.address_match_mapping.get(address_name, None)
            if match:
                matches.append(match)
        return matches

    async def scan_beacons(self, address_names, duration):
        """
        This function is called if the read_method property
        of the class is configured as "beacon"
        """
        #Data uuid matches to look up 
        self.matches = self.get_matches(address_names)
        logging.debug(f"MATCHES: {self.matches}")
        #Create the scanner 
        scanner = BleakScanner(detection_callback=self.beacon_callback, service_uuids=self.matches)
        #Start the scanner 
        await scanner.start()
        logging.debug("Started Scanner")
        await asyncio.sleep(self.listening_interval)
        if duration != "always":
            await asyncio.sleep(self.listening_interval)
            await scanner.stop()
        else:
            while True:
                #This part might need to change 
                await asyncio.sleep(60)

    def run_scanner(self, address_names, duration):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        #loop = asyncio.get_event_loop()
        logging.debug(f"In Run Scanner function, duration {duration}")
        loop.run_until_complete(self.scan_beacons(address_names, duration))
        #MARKED - may need to change later 
        # if duration != "always":
        #     print("Running this loop once")
        #     loop.run_until_complete(self.scan_beacons(address_names, duration))


    def write_read_callback(self, characteristic, data):
        logging.debug(f"Received data back: {data}")
        if data:
            message = {
                        "mac_address": self.working_mac,
                        "packet": data 
                    }
            try:
                enveloped_message = system_object.system.envelope_message(message, self.working_address)
                system_object.system.post_messages(enveloped_message, self.working_address)
            except Exception as e:
                logging.debug(f"Could not post BLE Write Read message for reason {e}", exc_info=True)
 

    async def query_function(self, mac_address, read_uuid, write_uuid, data_to_write):
        """
        Asynchronous function to run to write the appropriate 
        information and get the response in the callback 
        """
        try:
            async with BleakClient(mac_address) as client:
                logging.debug("Connected")
                await client.start_notify(read_uuid, self.write_read_callback)
                #Try this when next working on it 
                response_back = await client.write_gatt_char(write_uuid, data_to_write)
                #logging.debug(f"Response: {response_back}")
                await asyncio.sleep(5.0)
                await client.stop_notify(read_uuid)
        except Exception as e:
            logging.error(f"Issue with Bleak Write Read: {e}")
            try:
                logging.info("Attempting to restart bluetooth.")
                os.system("rfkill block bluetooth")
                os.system("rfkill unblock bluetooth")
            except Exception as e:
                logging.error(f"Could not bring BT up and down with rfkill: {e}")

    def get_readings_from_write_read(self, address_names):
        """
        This function gets the necessary info from the 
        addresses to run a write-read async loop from each
        """
         #For each identified address:
        for address_name in address_names:
            #Get the info dict 
            try:
                self.working_address = address_name 
                info_dict = self.address_info_mapping.get(address_name, {})
                #Get uuids and info 
                data_uuid = info_dict.get("data_uuid", None)
                if isinstance(data_uuid, list):
                    data_uuid = bytes(data_uuid)
                write_uuid = info_dict.get("write_uuid", None)
                if isinstance(write_uuid, list):
                    write_uuid = bytes(write_uuid)
                data_to_write = info_dict.get("data_to_write", None)
                if isinstance(data_to_write, list):
                    data_to_write = bytes(data_to_write)
                mac_list = self.address_mac_mapping.get(address_name, [])
                for mac_address in mac_list:
                    self.working_mac = mac_address
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(self.query_function(mac_address, data_uuid, write_uuid, data_to_write))
                    loop.close()
            except Exception as e:
                logging.error(f"Could not get BLE write read readings for address {address_name}")
        self.working_mac = None
        self.working_address = None 

    def disconnect(self):
        """
        In current implementation, function takes no arguments
        And only prints a message to the console. 
        """
        logging.info("Disconnect BLE: No actions needed for BLE disconnect in this driver.")


    def run_write_read(self, address_names, duration):
        """
        This function is called if the read_method property
        of the class is configured as "write_read". 

        """
        logging.debug("In write_read function")
        if duration != "always":
            self.get_readings_from_write_read(address_names)
        else:
            while True:
                pass 
                self.get_readings_from_write_read(address_names)
                time.sleep(300)
    
    def send(self, address_names, duration, entry_ids=[]):
        """
        Takes in an optional list of entry ids
        Grabs the messages and publishes them, optionally filtering by ID 
        """
        pass 
        #Currently not defined for this bluetooth driver. 
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return BLE(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)


