#Test initalizing the system to receive and send a very simple test message

#This test message:
    #Is read every 5 minutes
    #Is sent via MQTT to the middle agent on new message 
    #Is also sent to the local database on a new message 

#Help from here: https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth

import sys
sys.path.append("../scarecro")
import json 
import logging 

### First, create the system object to see if we have active messages 

#Get the system config
import src.system.system as system_class 



system = {
    "id": "test_device",
    "addresses": [
        "fake_receive_level_2",
        "fake_receive",
        "fake_receive_level_3",
        "fake_send_middle_agent"
    ]
}



test_message = {
    "id": "1",
    "time": "now",
    "place": "here",
    "who": "me"
}

test_message_2 = {
    "id": "2",
    "time": "now",
    "place": "here",
    "who": "me"
}

test_message_level_2 = {
    "id": "10",
    "time": "now",
    "place": "here",
    "who": "me"
}


def envelope_message(msg_id, time, message_type, message):
    envelope_dict = {
        "msg_id": msg_id,
        "msg_time": time,
        "msg_type": message_type,
        "msg_content": message
    }
    return envelope_dict.copy()




#Need to come up with several message types and system classes 
system_object = system_class.return_object(system_config=system)
system_object.print_configs(["addresses", "messages", "carriers", "handlers"])

#Test adding
new_message = envelope_message(test_message["id"], test_message["time"], "test_message", test_message)
new_message_2 = envelope_message(test_message_2["id"], test_message_2["time"], "test_message", test_message_2)
new_message_3 = envelope_message(test_message_level_2["id"], test_message_level_2["time"], "test_message_level_2", test_message_level_2)
#Initial Add
system_object.add_message("test_message", new_message)
print("#################")
system_object.print_message_entries_dict()
print("Test Message Latest: ", system_object.get_latest_message_entry("test_message"))
print("Test Message Level 2 latest: ", system_object.get_latest_message_entry("test_message_level_2"))


#Increment
print("###################")
system_object.add_message("test_message", new_message)
system_object.print_message_entries_dict()
print("Test Message Latest: ", system_object.get_latest_message_entry("test_message"))
print("Test Message Level 2 latest: ", system_object.get_latest_message_entry("test_message_level_2"))

#New add
print("###################")
system_object.add_message("test_message", new_message_2)
system_object.print_message_entries_dict()
print("Test Message Latest: ", system_object.get_latest_message_entry("test_message"))
print("Test Message Level 2 latest: ", system_object.get_latest_message_entry("test_message_level_2"))


#New add
print("###################")
system_object.add_message("test_message_level_2", new_message_3)
system_object.print_message_entries_dict()
print("Test Message Latest: ", system_object.get_latest_message_entry("test_message"))
print("Test Message Level 2 latest: ", system_object.get_latest_message_entry("test_message_level_2"))
