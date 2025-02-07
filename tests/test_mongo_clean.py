
import sys
import time 
sys.path.append("../scarecro")
import json 
import logging 
import system_object
import pymongo
#Get the system config
import src.system.system as system_class 
#Need to come up with several message types and system classes 
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(asctime)s - %(message)s')



gateway_message_old =  {
            "time": "2025-01-04T21:41:02.369307",
            "cpu_usage": 6.7,
            "memory_free": 78.58,
            "ip_addresses": [
                "129.101.98.208"
            ],
            "uptime": 18736.38,
            "id": "test_device"
        }

gateway_message_new =  {
            "time": "2025-02-06T21:41:02.369307",
            "cpu_usage": 6.7,
            "memory_free": 78.58,
            "ip_addresses": [
                "129.101.98.208"
            ],
            "uptime": 18736.38,
            "id": "test_device"
        }

enveloped_message_old = {
            "msg_id": "underlying_system",
            "msg_time": "2025-01-04T21:41:02.369307",
            "msg_type": "gateway_stats",
            "msg_content": gateway_message_old
        }

enveloped_message_new = {
            "msg_id": "underlying_system",
            "msg_time": "2025-02-06T21:41:02.369307",
            "msg_type": "gateway_stats",
            "msg_content": gateway_message_new
        }


system_config = {
    "id": "test_device",
    "addresses": [
        "gateway_stats_in",
        "mongo_local_immediate",
    ],
    "tasks": [
        "clean_database",
    ]
}


system_object.system = system_class.return_object(system_config=system_config)
#Print the configurations 
system_object.system.init_ecosystem()
system_object.system.print_configs(["tasks", "carriers"])
system_object.system.start_scheduler()


print("Before messages posted")
time.sleep(2)
system_object.system.post_messages_by_type(enveloped_message_old, "gateway_stats")
print("After old messages posted")
time.sleep(4)
#system_object.system.post_messages_by_type(enveloped_message_new, "gateway_stats")
#time.sleep(2)

client = pymongo.MongoClient("127.0.0.1:27017")
collection = client.SCARECRO.gateway_stats

search_query_1 = {
    "time": {
        "$gte": "2025-01-03T21:41:02.369307",
        "$lte": "2025-01-05T21:41:02.369307",
    }
}
search_query_2 = {
    "time": {
        "$gte": "2025-02-05T21:41:02.369307",
        "$lte": "2025-02-07T21:41:02.369307",
    }
}


print("Old Messages")
results = list(collection.find(search_query_1))
print(len(results))
print(results)
# print("New Messages")
# results = list(collection.find(search_query_2))
# print(len(results))
# print(results)

print("Wait for task to run .... ")
time.sleep(90)

print("Old Messages -- should be empty")
results = list(collection.find(search_query_1))
print(len(results))
print(results)
print("New Messages")
results = list(collection.find(search_query_2))
print(len(results))
#print(results)

time.sleep(2)
client.close()
 
#PASSED!
#This test is MAD Annoying. 