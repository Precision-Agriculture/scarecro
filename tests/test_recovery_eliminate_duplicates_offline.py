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

#What are we testing here?
#We need to see if the middle agent receives
# the recovery data message 
#And then if it probably routes the recovery data to the database 

system_config = {
    "id": "test_device_middle_agent",
    "addresses": [
        "cloud_mqtt_receive",
        "mongo_cloud_immediate",
    ],
    "tasks":[
        "handle_recovery_data",
    ],
    #"updater": "updater"
}


#Init the 
system_object.system = system_class.return_object(system_config=system_config)
system_object.system.init_ecosystem()
system_object.system.start_scheduler()

address_name = "mongo_cloud_immediate_gateway_stats"

direct_messages = [
    {
        "topic": "gateway_stats",
        "id": 1,
        "value": 3,
        "time": "2024-10-01T00:05:00.0",
        "testing": True, 
        "source": "direct" 
    },
    {
        "topic": "gateway_stats",
        "id": 1,
        "value": 3,
        "time": "2024-10-01T00:10:00.0",
        "testing": True, 
        "source": "direct" 
    },
    {
        "topic": "gateway_stats",
        "id": 1,
        "value": 3,
        "time": "2024-10-01T00:15:00.0",
        "testing": True, 
        "source": "direct" 
    },
    {
        "topic": "gateway_stats",
        "id": 1,
        "value": 3,
        "time": "2024-10-01T00:20:00.0",
        "testing": True, 
        "source": "direct" 
    },
    {
        "topic": "gateway_stats",
        "id": 2,
        "value": 3,
        "time": "2024-10-01T00:05:00.0",
        "testing": True, 
        "source": "direct" 
    },
    {
        "topic": "gateway_stats",
        "id": 2,
        "value": 3,
        "time": "2024-10-01T00:10:00.0",
        "testing": True, 
        "source": "direct" 
    },
    
]

recovery_messages = [
    {
        "topic": "gateway_stats",
        "id": 1,
        "value": 3,
        "time": "2024-09-30T23:58:00.000000",
        "testing": True, 
        "recovered_message": True,
    },
    {
        "topic": "gateway_stats",
        "id": 1,
        "value": 3,
        "time": "2024-10-01T00:03:00.0",
        "testing": True, 
        "recovered_message": True,
    },
    {
        "topic": "gateway_stats",
        "id": 2,
        "value": 3,
        "time": "2024-10-01T00:12:00.0",
        "testing": True, 
        "recovered_message": True,
    },
    {
        "topic": "gateway_stats",
        "id": 1,
        "value": 3,
        "time": "2024-10-01T00:13:00.0",
        "testing": True, 
        "recovered_message": True,
    },
    {
        "topic": "gateway_stats",
        "id": 2,
        "value": 3,
        "time": "2024-10-01T00:17:00.0",
        "testing": True, 
        "recovered_message": True,
    },
    {
        "topic": "gateway_stats",
        "id": 1,
        "value": 3,
        "time": "2024-10-01T00:18:00.0",
        "testing": True, 
        "recovered_message": True,
    },
    {
        "topic": "gateway_stats",
        "id": 1,
        "value": 3,
        "time": "2024-10-01T00:23:00.0",
        "testing": True,
        "recovered_message": True, 
    },
    {
        "topic": "gateway_stats",
        "id": 1,
        "value": 3,
        "time": "2024-10-01T00:28:00.0",
        "testing": True,
        "recovered_message": True, 
    }
]

#Only message at 17 and 28 should make it back into the database

#Already did once - should not have to do again. 
#for message_body in direct_messages:
    #enveloped_message = system_object.system.envelope_message(message_body, address_name)
    #Already done - don't have to do again. 
    #system_object.system.post_messages(enveloped_message, address_name)




#Receive the recovery data message 
recovery_data_message = {
        "id": "gateway_2",
        "entity": "mongodb",
        "lost_connection_time": "2024-10-01T00:12:00.0",
        "restored_connection_time": "2024-10-01T00:30:00.0",
        "recovery_data": {
            "gateway_stats": recovery_messages, 
        }
}
recovery_address_name = "cloud_mqtt_receive_recovery_data"
enveloped_message = system_object.system.envelope_message(recovery_data_message, recovery_address_name)
system_object.system.post_messages(enveloped_message, recovery_address_name)
#See if it behaves
#Only 17 and 28 and one september one should make it to the database
#(Should remove 5 entries (8 if you ran this test without deleting already)) 
#Test passed on middle agent side - still need to figure out others 
while True:
    time.sleep(15)
    pass 

