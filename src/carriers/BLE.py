import sys
import time 
import logging 
import json 
sys.path.append("../scarecro")
import system_object
import util.util as util 
import asyncio
from bleak import BleakScanner, BleakClient

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
        

        self.read_method = self.config.get("read_method", None)
        self.listening_interval = self.config.get("listening_interval", 60)
        self.create_mappings()

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
        print("In receive function")
        if self.read_method == "beacon":
            print("Right before the run scanner function")
            self.run_scanner(address_names, duration)


    def beacon_callback(self, device, advertising_data):
        """
        Callback registered for a given scanner. 
        Takes in the device and the advertising data 
        Posts the message if applicable 
        """
        print("In Beacon Callback")
        name = device.name   
        address = device.address
        rssi = device.rssi 
        service_data_dict = advertising_data.service_data
        true_packet = False
        #If if it has a data_uuid we are looking for 
        #Might want to configure address-dynamic self matches? Kills reusability a bit
        print(self.matches)
        print(service_data_dict.keys())
        for match in self.matches:
            if match not in list(service_data_dict.keys()):
                continue 
            packet = service_data_dict.get(match, None)
            if packet: 
                print("Found a matching packet!")
                print(match)
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
                    print("SEND MESSAGE")
                    print(message)
                    enveloped_message = system_object.system.envelope_message(message, address_name)
                    system_object.system.post_messages(enveloped_message, address_name)
                    #JUST FOR DEBUG - CHANGE
                    system_object.system.print_message_entries_dict()
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
        print("MATCHES")
        print(self.matches)
        #Create the scanner 
        scanner = BleakScanner(detection_callback=self.beacon_callback, service_uuids=self.matches)
        #Start the scanner 
        await scanner.start()
        print("Started Scanner")
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
        print("IN Run Scanner function")
        print(duration)
        loop.run_until_complete(self.scan_beacons(address_names, duration))
        # if duration != "always":
        #     print("Running this loop once")
        #     loop.run_until_complete(self.scan_beacons(address_names, duration))


    # def notification_callback(characteristic, data):
#     print("DATA")
#     print(data)
#     new_data = parse_charge_controller_info(data)
#     print(new_data)


    def run_write_read(self, address_names, duration):
        """
        This function is called if the read_method property
        of the class is configured as "write_read". 
        """
        pass 
        #For write and then read, assume we need to connect first
        #This may make the connection variable obsolute? Or else,
        #we need to run a scan session first. 
        #Try to get it up without a scan session first, then keep going. 


    def send(self, address_names, duration, entry_ids=[]):
        """
        Takes in an optional list of entry ids
        Grabs the messages and publishes them, optionally filtering by ID 
        """
        pass 
        #Currently not defined for this bluetooth driver. 
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return BLE(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)



#if __name__=="__main__":

#     import asyncio
#     from bleak import BleakScanner

#     async def main():
#         devices = await BleakScanner.discover()
#         # for d in devices:
#         #     print(d)

#         device_dict = BleakScanner.discovered_devices_and_advertisement_data
#         print(json.dumps(device_dict, default=str))
#         # BleakScanner.start()
#         # device_tuple = BleakScanner()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())


# async with BleakClient("60:98:66:EA:40:A9") as client:
#         print(client.address)
#         print(client.services)
#         print("Connected")

#         await client.start_notify(read_uuid, notification_callback)
#         #Try this when next working on it 
#         response_back = await client.write_gatt_char(try_write_uuid, data_in_bytes)
#         print(response_back)
#         await asyncio.sleep(5.0)
#         await client.stop_notify(read_uuid)

    
# read_uuid = "0000fff1-0000-1000-8000-00805f9b34fb"
# try_write_uuid = "0000ffd1-0000-1000-8000-00805f9b34fb"
# data = [255, 3, 1, 0, 0, 34, 209, 241]
# data_in_bytes = bytes(data)


# def notification_callback(characteristic, data):
#     print("DATA")
#     print(data)
#     new_data = parse_charge_controller_info(data)
#     print(new_data)


