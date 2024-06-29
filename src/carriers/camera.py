import time 
import picamera
from datetime import datetime, timedelta, tzinfo
from datetime import timezone
from datetime import date
import pytz
from dateutil import tz 
import os
#from PIL import ImageFont, ImageDraw, Image
from PIL import Image
import logging

import sys 
sys.path.append("../scarecro")
import system_object
import util.util as util 

class Camera():
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
        self.id = self.config.get("id", "default")

        #Figure out file stuff 
        file_path = os.path.abspath(os.getcwd())
        self.base_path = f"{file_path}/generated_data/"
        #Create a mapping dictionary from the additional info 
        self.mapping_dict = util.forward_backward_map_additional_info([self.send_addresses, self.receive_addresses])
        self.create_folders()
        logging.info("Initialized camera carrier")

    def create_folders(self): 
        for address_name, folder in self.mapping_dict["folder"]["address_name"].items():
            #Create the folder
            make_path = f"{self.base_path}/{folder}/"
            if not os.path.exists(make_path):
                os.makedirs(make_path)

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

    def generate_picture_name_and_reading(self, save_path, camera_type):
        """
        Takes the name of the camera and the base save path 
        Returns the full filepath of the image name and a basic reading dictionary
        With the image name and timestamp. 
        """
        new_dict = {}
        utc_curr_time = datetime.now(tz=pytz.UTC)
        file_date = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
        file_day = datetime.datetime.now().strftime("%Y-%m-%d")
        picture_folder_save_path = f"{save_path}/{str(file_day)}/"
        os.makedirs(picture_folder_save_path, exist_ok=True)
        #Save filename as {datetime}_{id}_{camera_type}.jpg 
        picture_name = f"{picture_folder_save_path}{file_date}-{self.id}-{camera_type}.jpg"
        #Generate the reading 
        new_dict["image_name"] = picture_name
        new_dict["time"] = file_date   
        return picture_name, new_dict

    def take_picam_picture(self, address_name):
        """
        Takes a picamera picture and generates a reading
        with the image information 
        """
        new_dict = {}
        logging.info("Taking picamera picture(s)")
        #Get the save path 
        folder = self.mapping_dict["folder"]["address_name"][address_name]
        save_path = f"{self.base_path}/{folder}/"
        camera = picamera.PiCamera()
        camera.exposure_mode = "auto"
        try:
            #Take the picture 
            resolution = [1920, 1080]
            camera.resolution = (1920, 1080)
            # Camera warm-up time
            time.sleep(2)
            picture_name, new_dict = self.generate_picture_name_and_reading(save_path, "picamera")
            camera.capture(picture_name)
            #Generate the reading 
            new_dict["image_resolution"] = resolution
            new_dict["camera_type"] = "picamera"
        except Exception as e:
            logging.error("Could not take picamera image", exc_info=True)
        finally:
            try:
                camera.close()
            except Exception as e:
                logging.error("picamera Close Failed", exc_info=True)
        return new_dict

    def take_pi_hawk_eye_picture(self, address_name):
        new_dict = {}
        logging.info("Taking pi_hawk_eye picture(s)")
        #Get the save path 
        folder = self.mapping_dict["folder"]["address_name"][address_name]
        save_path = f"{self.base_path}/{folder}/"
        try:
            picture_name, new_dict = self.generate_picture_name_and_reading(save_path, "pi_hawk_eye")
            #Generate the reading 
            new_dict["image_resolution"] = [4626, 3472]
            new_dict["camera_type"] = "pi_hawk_eye"
            command = f"libcamera-still -t 5000 –autofocus –width 4626 –height 3472 -o {picture_name}"
            os.system(command)
        except Exception as e:
            logging.error("Could not take pi_hawk_eye image", exc_info=True)
        return new_dict

    #Need to add a cleaning picture task 

    def receive(self, address_names, duration):
        """
        Takes in the address names and the duration
        For this driver, duration should not be 'always'
        This function will NOT keep itself alive 
        """
        for address_name in address_names:
            try:
                camera_type = self.mapping_dict["camera_type"]["address_name"][address_name]
                reading = {}
                if camera_type == "picamera":
                    reading = self.take_picam_picture(address_name)
                elif camera_type == "pi_hawk_eye":
                    reading = self.take_pi_hawk_eye_picture(address_name)
                if reading:
                    reading = self.add_id_to_reading(reading, address_name)
                    logging.info(f"Took picture! Reading {reading}")
                    enveloped_message = system_object.system.envelope_message(reading, address_name)
                    system_object.system.post_messages(enveloped_message, address_name)
            except Exception as e: 
                logging.error(f"Could not take process image for address {address_name}", exc_info=True)

            
    def send(self, address_names, duration, entry_ids=[]):
        """
        Not really defined for this driver 
        Right now, driver only capable of listening on 433 radio,
        not sending
        """
        pass 
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return Camera(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)
