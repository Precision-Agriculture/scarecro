import logging 
import sys 
sys.path.append("../scarecro")
import util.util as util 


class KKM_K6P:
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
        logging.info("Initing kkm_k6p handler")
        

    def bytes_to_fixed_point_88(self, bytes_object, endian):
        whole = int.from_bytes(bytes_object[0:1], endian)
        fraction = int.from_bytes(bytes_object[1:2], endian)
        number_string = f"{whole}.{fraction}"
        #number = whole + fraction/1<<8
        number = float(number_string)
        return number 


    def parse_message(self, message_packet):
        message = message_packet.get("packet", {})
        final_message = {}
        #message = bytearray(message)
        #message = list(message)
        frame_type = int.from_bytes(message[0:1], "little")
        #print("Frame Type", frame_type)
        version = int.from_bytes(message[1:2], "little")
        #print("Version", version)
        sensor_mask = int.from_bytes(message[2:3], "little")
        #print("Sensor Mask", sensor_mask)
        voltage = int.from_bytes(message[3:5], "little")
        #print("Voltage", voltage)
        temp = self.bytes_to_fixed_point_88(message[5:7], "big")
        #print("Temperature", temp)
        humidity = self.bytes_to_fixed_point_88(message[7:9], "little")
        #print("Humidity", humidity)
        accX = int.from_bytes(message[9:11], "big")
        #print("AccX", accX)
        accY = int.from_bytes(message[11:13], "big")
        #print("AccY", accY)
        accZ = int.from_bytes(message[13:15], "big")
        #print("AccZ", accZ)
        final_message["HUMIDITY"] = humidity
        final_message["TEMP"] = temp
        final_message["BATT_VOLTAGE"] = voltage
        final_message["SENSOR_NAME"] = message_packet.get("name", None)
        final_message["id"] = message_packet.get("mac_address", None)
        final_message["time"] = util.get_today_date_time_utc()
        return final_message


    def process(self, message_type, messages):
        """
        This function takes in a message_type and a list of messages
        It returns a list of messages 
        """
        for message in messages:
            sub_message = message.get("msg_content", {})
            new_message = self.parse_message(sub_message)
            logging.info(f"KKM Message {new_message}")
            message["msg_content"] = new_message
            #Envelope ovverride 
            #Once ID is parsed out, replace it in the envelope
            message["msg_id"] = new_message.get("id", "default")
        return messages 
        

def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return KKM_K6P(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)
