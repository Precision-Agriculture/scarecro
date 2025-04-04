import sys
import time 
sys.path.append("../scarecro")
import logging 
import system_object
#Get the system config
import src.system.system as system_class 
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(asctime)s - %(message)s')
#logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
#Need to come up with several message types and system classes 

system_config = {
    "id": "test_device",
    "addresses": [
        "cloud_mqtt_send_immediate",
    ],
    "tasks": [
        "download_new_firmware_image"
    ]
}

message_type = "firmware_image"
enveloped_message = {
            "msg_id": "site",
            "msg_time": "now",
            "msg_type": "firmware_image",
            "msg_content": {
                    "id": "site",
                    "time": "now",
                    "file_name": "image_1.jpg",
                    "disk_path": "generated_data/firmware_images/20220705_113630.jpg",
                    "cloud_path": "gateway_1/pics/20220705_113630.jpg",
                    "config_path": "generated_data/firmware_images/latest_firmware.txt"
                }
        }

#Init the 
system_object.system = system_class.return_object(system_config=system_config)
system_object.system.init_ecosystem()
system_object.system.start_scheduler()


print("#---------Before new firmware message sent-------#")
time.sleep(2)
system_object.system.post_messages_by_type(enveloped_message, message_type)


while True:
    time.sleep(15)
    pass 

