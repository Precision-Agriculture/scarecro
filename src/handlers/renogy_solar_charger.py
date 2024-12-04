import logging 
import sys 
sys.path.append("../scarecro")
import util.util as util 




class RenogyBT:
    """
    This class uses code and functions from Cyril Sebastian's public
    "Renogy-BT" github repo located here: https://github.com/cyrils/renogy-bt/tree/main/renogybt
    to parse the information. The copyright belongs to Cyril Sebastian. 
    """
    def __init__(self, config={}, send_addresses={}, receive_addresses={}, message_configs={}):
        #These are optional - if your program needs them 
        """
        Takes in: a configuration dictionary for this handler,
        A dictionary of addresses for the handler for sending, (dictionary?)
        A dictionary of addresses for the handler for receiving (dictionary?), 
        A dictionary of message definitions indicated in the addresses 
        """
        self.config = config.copy()
        self.send_addresses = send_addresses.copy()
        self.receive_addresses = receive_addresses.copy()
        self.message_definitions = message_configs.copy()
        self.CHARGING_STATE = {
            0: 'deactivated',
            1: 'activated',
            2: 'mppt',
            3: 'equalizing',
            4: 'boost',
            5: 'floating',
            6: 'current limiting'
        }

        self.LOAD_STATE = {
            0: 'off',
            1: 'on'
        }

        self.FUNCTION = {
            3: "READ",
            6: "WRITE"
        }
        logging.info("Initialized renogy bt handler")

    def Bytes2Int(self, bs, offset, length):
        """
        Function from Cyril Sebastian's Renogy BT Repo 
        """
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


    def parse_temperature(self, raw_value):
        """
        Function from Cyril Sebastian's Renogy BT Repo 
        """
        sign = raw_value >> 7
        return -(raw_value - 128) if sign == 1 else raw_value


    def parse_charge_controller_info(self, message):
        """
        Function from Cyril Sebastian's Renogy BT Repo 
        """
        bs = message.get("packet", "")
        data = {}
        data['function'] = self.FUNCTION[self.Bytes2Int(bs, 1, 1)]
        data['battery_percentage'] = self.Bytes2Int(bs, 3, 2)
        data['battery_voltage'] = round(self.Bytes2Int(bs, 5, 2) * 0.1, 2)
        data['battery_current'] = self.Bytes2Int(bs, 7, 2) * 0.01
        data['battery_temperature'] = self.parse_temperature(self.Bytes2Int(bs, 10, 1))
        data['controller_temperature'] = self.parse_temperature(self.Bytes2Int(bs, 9, 1))
        data['load_status'] = self.LOAD_STATE[self.Bytes2Int(bs, 67, 1) >> 7]
        data['load_voltage'] = round(self.Bytes2Int(bs, 11, 2) * 0.1, 2)
        data['load_current'] = self.Bytes2Int(bs, 13, 2) * 0.01
        data['load_power'] = self.Bytes2Int(bs, 15, 2)
        data['pv_voltage'] = round(self.Bytes2Int(bs, 17, 2) * 0.1, 2)
        data['pv_current'] = self.Bytes2Int(bs, 19, 2) * 0.01
        data['pv_power'] = self.Bytes2Int(bs, 21, 2)
        data['max_charging_power_today'] = self.Bytes2Int(bs, 33, 2)
        data['max_discharging_power_today'] = self.Bytes2Int(bs, 35, 2)
        data['charging_amp_hours_today'] = self.Bytes2Int(bs, 37, 2)
        data['discharging_amp_hours_today'] = self.Bytes2Int(bs, 39, 2)
        data['power_generation_today'] = self.Bytes2Int(bs, 41, 2)
        data['power_consumption_today'] = self.Bytes2Int(bs, 43, 2)
        data['power_generation_total'] = self.Bytes2Int(bs, 59, 4)
        data['charging_status'] = self.CHARGING_STATE[self.Bytes2Int(bs, 68, 1)]
        data['deviceid'] = message.get("mac_address", "default")
        return data


    def process(self, message_type, messages):
        """
        This function takes in a message_type and a list of messages
        It returns a list of messages 
        """
        for message in messages:
            sub_message = message.get("msg_content", {})
            new_message = self.parse_charge_controller_info(sub_message)
            new_message["time"] = message.get("msg_time", None)
            message["msg_content"] = new_message
            #Envelope Override on the id here 
            message["msg_id"] = new_message.get("deviceid", "default")
        return messages 
        

def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return RenogyBT(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)
