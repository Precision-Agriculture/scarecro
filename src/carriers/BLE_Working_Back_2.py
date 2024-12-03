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
from bleak import BleakScanner, BleakClient


CHARGING_STATE = {
    0: 'deactivated',
    1: 'activated',
    2: 'mppt',
    3: 'equalizing',
    4: 'boost',
    5: 'floating',
    6: 'current limiting'
}

LOAD_STATE = {
  0: 'off',
  1: 'on'
}

FUNCTION = {
    3: "READ",
    6: "WRITE"
}

def Bytes2Int(bs, offset, length):
        # Reads data from a list of bytes, and converts to an int
        # Bytes2Int(bs, 3, 2)
        ret = 0
        if len(bs) < (offset + length):
            return ret
        if length > 0:
            # offset = 11, length = 2 => 11 - 12
            byteorder='big'
            start = offset
            end = offset + length
        else:
            # offset = 11, length = -2 => 10 - 11
            byteorder='little'
            start = offset + length + 1
            end = offset + 1
        # Easier to read than the bitshifting below
        return int.from_bytes(bs[start:end], byteorder=byteorder)


def Int2Bytes(i, pos = 0):
    # Converts an integer into 2 bytes (16 bits)
    # Returns either the first or second byte as an int
    if pos == 0:
        return int(format(i, '016b')[:8], 2)
    if pos == 1:
        return int(format(i, '016b')[8:], 2)
    return 0


def parse_set_load_response(bs):
    data = {}
    data['function'] = FUNCTION[Bytes2Int(bs, 1, 1)]
    data['load_status'] = Bytes2Int(bs, 5, 1)
    return data

def parse_temperature(raw_value):
    sign = raw_value >> 7
    return -(raw_value - 128) if sign == 1 else raw_value


def parse_charge_controller_info(bs):
    data = {}
    data['function'] = FUNCTION[Bytes2Int(bs, 1, 1)]
    data['battery_percentage'] = Bytes2Int(bs, 3, 2)
    data['battery_voltage'] = Bytes2Int(bs, 5, 2) * 0.1
    data['battery_current'] = Bytes2Int(bs, 7, 2) * 0.01
    data['battery_temperature'] = parse_temperature(Bytes2Int(bs, 10, 1))
    data['controller_temperature'] = parse_temperature(Bytes2Int(bs, 9, 1))
    data['load_status'] = LOAD_STATE[Bytes2Int(bs, 67, 1) >> 7]
    data['load_voltage'] = Bytes2Int(bs, 11, 2) * 0.1
    data['load_current'] = Bytes2Int(bs, 13, 2) * 0.01
    data['load_power'] = Bytes2Int(bs, 15, 2)
    data['pv_voltage'] = Bytes2Int(bs, 17, 2) * 0.1
    data['pv_current'] = Bytes2Int(bs, 19, 2) * 0.01
    data['pv_power'] = Bytes2Int(bs, 21, 2)
    data['max_charging_power_today'] = Bytes2Int(bs, 33, 2)
    data['max_discharging_power_today'] = Bytes2Int(bs, 35, 2)
    data['charging_amp_hours_today'] = Bytes2Int(bs, 37, 2)
    data['discharging_amp_hours_today'] = Bytes2Int(bs, 39, 2)
    data['power_generation_today'] = Bytes2Int(bs, 41, 2)
    data['power_consumption_today'] = Bytes2Int(bs, 43, 2)
    data['power_generation_total'] = Bytes2Int(bs, 59, 4)
    data['charging_status'] = CHARGING_STATE[Bytes2Int(bs, 68, 1)]
    return data


read_uuid = "0000fff1-0000-1000-8000-00805f9b34fb"
try_write_uuid = "0000ffd1-0000-1000-8000-00805f9b34fb"
data = [255, 3, 1, 0, 0, 34, 209, 241]
data_in_bytes = bytes(data)


def notification_callback(characteristic, data):
    print("DATA")
    print(data)
    new_data = parse_charge_controller_info(data)
    print(new_data)

async def main():
    async with BleakClient("60:98:66:EA:40:A9") as client:
        print(client.address)
        print(client.services)
        print("Connected")

        # char_dict = client.services.characteristics
        # for key, value in char_dict.items():
        #     print(key)
        #     print(value.description)
        #     print(value.properties)
        #     print(value.uuid)
        #     print("---------------")
        #response_back = await client.write_gatt_char(char_specifier=WRITE_CHAR_UUID, data=data_in_bytes, response=True)
        # response_back = await client.read_gatt_char(read_uuid)
        # print(response_back)
        
        await client.start_notify(read_uuid, notification_callback)
        #Try this when next working on it 
        response_back = await client.write_gatt_char(try_write_uuid, data_in_bytes)
        print("Response")
        print(response_back)
        await asyncio.sleep(5.0)
        await client.stop_notify(read_uuid)

        # await client.start_notify(args.characteristic, notification_handler)
        # await asyncio.sleep(5.0)
        # await client.stop_notify(args.characteristic)


#def run_the_program():
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

#Convert each one of these into a byte. Write the array of bytes to
#the write characteristic 
#data = [255, 3, 1, 0, 0, 34, 209, 241]

#data to modbus?: [255, 3, 1, 0, 0, 34] -> wrapped in bytes 

#run_the_program()

#Look into: https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/ 

#Found write characteristic: 0000fff1-0000-1000-8000-00805f9b34fb

#WRITE_CHAR_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"