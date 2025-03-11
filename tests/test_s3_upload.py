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
        "s3_upload",

    ],
}

message_type = "image_info"
enveloped_message = {
            "msg_id": "picamera",
            "msg_time": "now",
            "msg_type": "image_info",
            "msg_content": {
                    "id": "picamera",
                    "time": "now",
                    "file_name": "image_1.jpg",
                    "disk_path": "generated_data/images/image_1.jpg",
                    #"cloud_path": "camera_cloud/test_device/image_1.jpg"
                }
        }

#Init the 
system_object.system = system_class.return_object(system_config=system_config)
system_object.system.init_ecosystem()
system_object.system.start_scheduler()


print("#---------Before image info sent-------#")
time.sleep(2)
system_object.system.post_messages_by_type(enveloped_message, message_type)


while True:
    time.sleep(15)
    pass 

