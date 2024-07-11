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

enveloped_message = {
            "msg_id": 3,
            "msg_time": "now",
            "msg_type": "remote_config_updated",
            "msg_content": {
                    "id": "system_middle_agent_test",
                    "time": "now",
                    "config_folder": "addresses",
                    "config_name": "bmp280_in",
                    "config_id": "bmp280_in_gateway",
                    #"config_id": "bmp280_in_gateway_wrong" 
                }
        }


system_config = {
    "id": "test_device",
    "addresses": [
        #"mongo_cloud_immediate",
        #"cloud_mqtt_receive"
    ],
    "tasks":[
        "fetch_updates",
        "update_config"
    ],
}

#Init the 
system_object.system = system_class.return_object(system_config=system_config)
system_object.system.start_scheduler()
time.sleep(2)
system_object.system.post_messages_by_type(enveloped_message, "remote_config_updated")
#Post a request update message and
#See if the system fetches the right config 
while True:
    time.sleep(15)
    pass 

