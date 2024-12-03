import sys
import time 
import requests
import logging 
import json 
import gatt 
sys.path.append("../scarecro")
import system_object
import util.util as util 
#Help from the documentation here: https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#multiple


class BLE():
    def __init__(self, config, send_addresses, receive_addresses, message_configs):
        """
        Bluetooth needs
        1. A mac address
        2. optionally an alias  
        """
        #arguments passed in 
        self.config = config 
        self.send_addresses = send_addresses 
        self.receive_addresses = receive_addresses
        self.message_configs = message_configs

    def receive(self, address_names, duration):
        """
        Receives a list of addresses (all with same duration). Depending 
        on the duration and the address, it sets itself
        up to 'receive' spoofed messages and post them
        to the system post office along with an address 
        """
        pass


    def send(self, address_names, duration, entry_ids=[]):
        """
        Takes in an optional list of entry ids
        Grabs the messages and publishes them, optionally filtering by ID 
        """
        pass 
    
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

import asyncio
from bleak import BleakScanner

async def main():
    stop_event = asyncio.Event()

    # TODO: add something that calls stop_event.set()

    def bytes_to_fixed_point_88(bytes_object, endian):
        whole = int.from_bytes(bytes_object[0:1], endian)
        fraction = int.from_bytes(bytes_object[1:2], endian)
        number_string = f"{whole}.{fraction}"
        #number = whole + fraction/1<<8
        number = float(number_string)
        return number 





    def callback(device, advertising_data):
        # TODO: do something with incoming data        
        service_data_dict = advertising_data.service_data
        TLM_packet = service_data_dict.get("0000feaa-0000-1000-8000-00805f9b34fb", None)
        address = device.address
        
        if TLM_packet and (device.address == "BC:57:29:00:F6:C4"):
            print("DEVICE")
            print(device)
            print("Advertising Service Data")
            print("Length", len(TLM_packet))
            #TLM_packet = bytearray(TLM_packet)
            #TLM_packet = list(TLM_packet)
            frame_type = int.from_bytes(TLM_packet[0:1], "little")
            print("Frame Type", frame_type)
            version = int.from_bytes(TLM_packet[1:2], "little")
            print("Version", version)
            sensor_mask = int.from_bytes(TLM_packet[2:3], "little")
            print("Sensor Mask", sensor_mask)
            voltage = int.from_bytes(TLM_packet[3:5], "little")
            print("Voltage", voltage)
            temp = bytes_to_fixed_point_88(TLM_packet[5:7], "big")
            print("Temperature", temp)
            humidity = bytes_to_fixed_point_88(TLM_packet[7:9], "little")
            print("Humidity", humidity)
            accX = int.from_bytes(TLM_packet[9:11], "big")
            print("AccX", accX)
            accY = int.from_bytes(TLM_packet[11:13], "big")
            print("AccY", accY)
            accZ = int.from_bytes(TLM_packet[13:15], "big")
            print("AccZ", accZ)
            print("--------------------------")
        #print(advertising_data.service_data)

    
    scanner = BleakScanner(detection_callback=callback)
    await scanner.start()

    await asyncio.sleep(15*60)

    #OR --- Need to think about the best way to go about this 
    # async with BleakScanner(detection_callback=callback) as scanner:
    #     ...
    #     # Important! Wait for an event to trigger stop, otherwise scanner
    #     # will stop immediately.
    #     await stop_event.wait()


def run_the_program():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

run_the_program()

#Look into: https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/ 