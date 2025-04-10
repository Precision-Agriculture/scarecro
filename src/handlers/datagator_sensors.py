from datetime import datetime, timedelta, tzinfo
from datetime import timezone
from datetime import date
import pytz
from dateutil import tz 
import logging 


class DataGatorSensors:
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
        #Debug Step 
        logging.info("Initing Data Gator sensors handler")
    

    def envelope_id_override(self, message_envelope, message_content): 
        message_def = self.message_definitions.get(message_envelope.get("msg_type", None), {})
        message_envelope["msg_content"] = message_content
        message_envelope["msg_id"] = message_content.get(message_def.get("id_field", "id"), "default")
        message_envelope["msg_time"] = message_content.get(message_def.get("time_field", "time"), "default")
        return message_envelope

    def parse_datagator(self, message):
        """
        Takes in message of form {"topic_list": [topic_list], "message": {message}}
        Returns parsed datagator message 
        """
        new_dict = {}
        try:
            topic_list = message["topic_list"]
            #Marked - Necessary? 
            new_dict["datagator_id"] = message["MAC"]
            #It's ID is the ID of the aggregator plus it's depth. 
            new_dict["id"] = str(message["MAC"])
            #Then the time:
            utc_curr_time = datetime.now(tz=pytz.UTC)
            time_string = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            new_dict["time"] = time_string
            #Rest of message came through normally
            new_dict["FIRMWARE_VERSION"] = message["FIRMWARE_VERSION"]
            new_dict["BATT_VOLTAGE"] = message["BATT_VOLTAGE"]
            new_dict["BATT_PERCENTAGE"] = message["BATT_PERCENTAGE"]
            if "RSSI" in list(message.keys()):
                new_dict["RSSI"] = message["RSSI"]
            if "BSSID" in list(message.keys()):
                new_dict["BSSID"] = message["BSSID"]
        except Exception as e:
            logging.error("Could not process datagator message: ", exc_info=True)
        #MARKED
        logging.debug(f"Datagator Reading {new_dict}")
        return new_dict

    def parse_datagator_ota(self, message):
        new_dict = {}
        try:
            #Change here 
            topic_list = message["topic_list"]
            new_dict["datagator_id"] = topic_list[2]
            new_dict["id"] = topic_list[2]
            #Then the time:
            utc_curr_time = datetime.now(tz=pytz.UTC)
            time_string = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            new_dict["time"] = time_string
            if "STATUS_MSG" in list(message.keys()):
                new_dict["STATUS_MSG"] = message["STATUS_MSG"]
            if "SERVER_FW_VERSION" in list(message.keys()):
                new_dict["SERVER_FW_VERSION"] = message["SERVER_FW_VERSION"]
            if "DEVICE_FW_VERSION" in list(message.keys()):
                new_dict["DEVICE_FW_VERSION"] = message["DEVICE_FW_VERSION"]
        except Exception as e:
            logging.error("Could not process datagator_ota message: ", exc_info=True)
        #MARKED
        logging.debug(f"Datagator OTA Reading {new_dict}")
        return new_dict


    def parse_atlas_ezo_ph(self, message):
        new_dict = {}
        try:
            topic_list = message["topic_list"]
            new_dict["datagator_id"] = message["MAC"]
            #It's ID is the ID of the aggregator plus it's depth. 
            new_dict["id"] = str(message["MAC"])
            if len(topic_list) > 3:
                new_dict["id"] = str(message["MAC"])+"_"+str(topic_list[2])
                new_dict["depth"] = topic_list[2]
            #Then the time:
            utc_curr_time = datetime.now(tz=pytz.UTC)
            time_string = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            new_dict["time"] = time_string
            #Rest of message came through normally
            new_dict["PH"] = message["PH"]
            if "PH_RAW" in list(message.keys()):
                new_dict["PH_RAW"] = message["PH_RAW"]
        except Exception as e:
            logging.error(f"Could not process atlas gravity message: {message}", exc_info=True)
        logging.debug(f"Atlas ezo pH reading: {new_dict}")
        return new_dict

    def parse_atlas_gravity_ph(self, message):
        new_dict = {}
        try:
            topic_list = message["topic_list"]
            new_dict["datagator_id"] = message["MAC"]
            #It's ID is the ID of the aggregator plus it's depth. 
            new_dict["id"] = str(message["MAC"])
            #Then the time:
            utc_curr_time = datetime.now(tz=pytz.UTC)
            time_string = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            new_dict["time"] = time_string
            #Rest of message came through normally
            new_dict["PH"] = message["PH"]
            new_dict["PH_RAW"] = message["PH_RAW"]
        except Exception as e:
            logging.error(f"Could not process atlas gravity message: {message}", exc_info=True)
        logging.debug(f"Atlas Gravity pH reading: {new_dict}")
        return new_dict

    def parse_generic_pH(self, message):
        new_dict = {}
        try:
            topic_list = message["topic_list"]
            new_dict["datagator_id"] = message["MAC"]
            #It's ID is the ID of the aggregator plus it's depth. 
            new_dict["id"] = str(message["MAC"])
            #Then the time:
            utc_curr_time = datetime.now(tz=pytz.UTC)
            time_string = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            new_dict["time"] = time_string
            #Rest of message came through normally
            new_dict["PH"] = message["PH"]
            new_dict["PH_RAW"] = message["PH_RAW"]
        except Exception as e:
            logging.error("Could not process generic_pH message: ", exc_info=True)
        logging.debug(f"generic pH reading: {new_dict}")
        return new_dict

    def parse_kkm_k6p(self, message):
        new_dict = {}
        try:
            topic_list = message["topic_list"]
            new_dict["datagator_id"] = message["GATOR_MAC"]
            #It's ID is the ID of the aggregator plus it's depth. 
            new_dict["id"] = str(message["MAC"])
            #Then the time:
            utc_curr_time = datetime.now(tz=pytz.UTC)
            time_string = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            new_dict["time"] = time_string
            #Rest of message came through normally
            new_dict["HUMIDITY"] = message["HUMIDITY"]
            new_dict["TEMP"] = message["TEMP"]
            if "BATT_VOLTAGE" in list(message.keys()):
                new_dict["BATT_VOLTAGE"] = message["BATT_VOLTAGE"]
            if "SENSOR_NAME" in list(message.keys()):
                new_dict["SENSOR_NAME"] = message["SENSOR_NAME"]
        except Exception as e:
            logging.error("Could not process kkm_k6p message:", exc_info=True)
        logging.debug(f"kkm_k6p reading: {new_dict}")
        return new_dict

    def parse_meter_teros10(self, message):
        new_dict = {}
        try:
            topic_list = message["topic_list"]
            new_dict["datagator_id"] = message["MAC"]
            #It's ID is the ID of the aggregator plus it's depth. 
            new_dict["id"] = str(message["MAC"])+"_"+str(topic_list[1])
            #Then the time:
            utc_curr_time = datetime.now(tz=pytz.UTC)
            time_string = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            new_dict["time"] = time_string
            #Rest of message came through normally
            new_dict["VWC"] = message["VWC"]
            new_dict["VWC_RAW"] = message["VWC_RAW"]
            new_dict["DEPTH"] = message["DEPTH"]
        except Exception as e:
            logging.error("Could not process meter_teros10 message: ", exc_info=True)
        logging.debug(f"meter_teros10 reading: {new_dict}")
        return new_dict

    def parse_mij_02_lms(self, message):
        new_dict = {}
        try:
            topic_list = message["topic_list"]
            new_dict["datagator_id"] = message["MAC"]
            #It's ID is the ID of the aggregator plus it's depth. 
            new_dict["id"] = str(message["MAC"])+"_"+str(topic_list[1])
            #Then the time:
            utc_curr_time = datetime.now(tz=pytz.UTC)
            time_string = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            new_dict["time"] = time_string
            #Rest of message came through normally
            new_dict["VOLTAGE"] = message["VOLTAGE"]
            new_dict["RADIUS"] = message["RADIUS"]
            new_dict["DEPTH"] = message["DEPTH"]
        except Exception as e:
            logging.error("Could not process mij_02_lms message: ", exc_info=True)
        logging.debug(f"mij_02_lms dendrometer reading: {new_dict}")
        return new_dict

    def parse_minew_s1(self, message):
        new_dict = {}
        try:
            topic_list = message["topic_list"]
            new_dict["datagator_id"] = message["GATOR_MAC"]
            #It's ID is the ID of the aggregator plus it's depth. 
            new_dict["id"] = message["MAC"]
            #Then the time:
            utc_curr_time = datetime.now(tz=pytz.UTC)
            time_string = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            new_dict["time"] = time_string
            #Rest of message came through normally
            if "HUMIDITY" in list(message.keys()):
                new_dict["humidity"] = message["HUMIDITY"]
            if "TEMP" in list(message.keys()):
                new_dict["temperature"] = message["TEMP"]
        except Exception as e:
            logging.error("Could not process minew_s1 message: ", exc_info=True)
        logging.debug(f"Minew s1 reading: {new_dict}")
        return new_dict


    def process_datagator_sensor_message(self, message_type, messages):
        """
        This function takes in a message_type and a list of messages
        It returns a list of messages, processed in some way 
        """
        try:
            for message in messages:
                sub_message = message.get("msg_content", {})
                sub_message["topic_list"] = topic_list = sub_message["topic"].split('/')
                if message_type == "datagator":
                    new_message = self.parse_datagator(sub_message)
                elif message_type == "datagator_ota": 
                    new_message = self.parse_datagator_ota(sub_message) 
                elif message_type == "atlas_ezo_ph": 
                    new_message = self.parse_atlas_ezo_ph(sub_message)
                elif message_type == "atlas_gravity_ph": 
                    new_message = self.parse_atlas_gravity_ph(sub_message)
                elif message_type == "generic_pH": 
                    new_message = self.parse_generic_pH(sub_message)
                elif message_type == "kkm_k6p": 
                    new_message = self.parse_kkm_k6p(sub_message)
                elif message_type == "minew_s1": 
                    new_message = self.parse_minew_s1(sub_message)
                elif message_type == "meter_teros10": 
                    new_message = self.parse_meter_teros10(sub_message)
                elif message_type == "mij_02_lms":
                    new_message = self.parse_mij_02_lms(sub_message)
                if new_message == {}:
                    #logging.debug(f"Error processing weather rack message")
                    return [] 
                message = self.envelope_id_override(message, new_message)
                logging.info(f"{message_type} Reading from Datagator: {message}")
            return messages
        except Exception as e:
            logging.error(f"Could not process switchdoc sensor messages: {e}")
            return [] 
        

def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return DataGatorSensors(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)

