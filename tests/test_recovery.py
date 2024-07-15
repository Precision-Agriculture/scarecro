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
            "msg_id": "mqtt",
            "msg_time": "now",
            "msg_type": "connection_status",
            "msg_content": {
                    "id": "mqtt",
                    "time": "now",
                    "connection_status": "disconnect",
                }
        }


system_config = {
    "id": "test_device",
    # "addresses": [
    #     #"mongo_cloud_immediate",
    #     #"cloud_mqtt_receive"
    #     "cloud_mqtt_send_immediate"
    # ],
    "tasks":[
        "handle_connection_change",
    ],
    #"updater": "updater"
}

#Init the 
system_object.system = system_class.return_object(system_config=system_config)
system_object.system.init_ecosystem()
system_object.system.start_scheduler()
#Print system update variable 
print("Before disconnect message sent")
time.sleep(2)
system_object.system.post_messages_by_type(enveloped_message, "connection_status")


while True:
    time.sleep(15)
    pass 

