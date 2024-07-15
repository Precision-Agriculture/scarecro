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
        #"gateway_stats_in",
        "cloud_mqtt_send_immediate",
        "mongo_local_immediate"
    ],
    "tasks":[
        "handle_request_for_recovery_data",
    ],
    #"updater": "updater"
}

message_type = "recovery_data_request"
enveloped_message = {
            "msg_id": "test_device",
            "msg_time": "now",
            "msg_type": "recovery_data_request",
            "msg_content": {
                    "id": "test_device",
                    "time": "now",
                    "lost_connection_time": "2024-07-15T21:40:22.045685",
                    "restored_connection_time": "2024-07-15T21:42:22.045685"
                }
        }

#Init the 
system_object.system = system_class.return_object(system_config=system_config)
system_object.system.init_ecosystem()
system_object.system.start_scheduler()


print("#---------Before recovery message sent-------#")
time.sleep(2)
system_object.system.post_messages_by_type(enveloped_message, message_type)


while True:
    time.sleep(15)
    pass 

