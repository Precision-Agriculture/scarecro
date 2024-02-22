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



    


addresses_answers = {
    "fake_receive_level_2": 
    {
        "inheritance":["fake_receive"],
        "message_type": "test_message_level_1",
        "fake_receive_level_2": "test_message_level_1",
        "carrier": "fake_message_listener_level_2",
        "handler": "fake_message_handler",
        "handler_function": "process",
        "send_or_receive": "receive",
        "duration": 30,
        "additional_info": {
            "topic": "ice_cream" 
        } 
    },
    "fake_receive": 
    {
        "inheritance":[],
        "message_type": "test_message",
        "handler": "fake_message_handler",
        "handler_function": "process",
        "send_or_receive": "receive",
        "carrier": "fake_message_listener",
        "duration": 30,
    },
    "fake_receive_level_3": 
    {
        "inheritance":["fake_receive_level_2"],
        "message_type": "test_message_level_2",
        "fake_receive_level_3": "test_message_level_2",
        "carrier": "fake_message_listener_level_2",
        "handler": "fake_message_handler_level_2",
        "handler_function": "process",
        "send_or_receive": "receive",
        "duration": 30,
        "additional_info": {
            "topic": "fake_receive_level_3"
        } 
    },
    "fake_send_middle_agent": 
    {
        "inheritance": ["fake_five_minute_send_MQTT"],
        "handler": "My_own",
        "message_type": "test_message",
        "handler_function": "process",
        "fake_send_middle_agent": "One",
        "send_or_receive": "send",
        "carrier": "fake_message_listener",
        "Hurrah": "test_message",
        "duration": 300,
        "additional_info":{
            "topic": "test_message",
            "fake_send_middle_agent": "test_message",
            "connection": "HERE" 
            }
    },
}


carrier_answers = {
    "fake_message_listener_level_2": 
    {
        "inheritance": ["fake_message_listener"],
        "fake_message_listener_level_2": "Hello",
        "connection_url": "fake_url@nobody_there.com"
    },
    "fake_message_listener":
    {
        "connection_url": "fake_url@nobody_there.com"
    }
} 

handler_answers = {
    "fake_message_handler": 
    {
        "handler_source": "test"
    },
    "fake_message_handler_level_2":
    {
        "inheritance": ["fake_message_handler"],
        "handler_function": "fake_message_handler_level_2",
        "handler_source": "test"
    },
    "My_own": {}
}


message_answers = {
    "test_message": 
    {
        "inheritance": [],
        "id_field": "id",
        "time_field": "time",
        "doesn't_matter": "not_important"
    },
    "test_message_level_1": 
    {
        "inheritance": ["test_message"],
        "id_field": "id_1",
        "time_field": "time_1",
        "thresher_sharks": "have_long_tails",
        "test_message_level_1": "test_message_level_1",
        "doesn't_matter": "not_important"
    },
    "test_message_level_2": 
    {
        "inheritance": ["test_message_level_1", "test_message"],
        "id_field": "id_2",
        "understandable": "comprehensible",
        "time_field": "time",
        "thresher_sharks": "have_long_tails",
        "test_message_level_2": "filler",
        "doesn't_matter": "not_important"
    }
}

carrier_mapping_answers = {
    "fake_message_listener_level_2": ["fake_receive_level_2", "fake_receive_level_3" ],
    "fake_message_listener": ["fake_receive", "fake_send_middle_agent"]
}

handler_mapping_answers = {
    "fake_message_handler": ["fake_receive_level_2", "fake_receive"],
    "fake_message_handler_level_2": ["fake_receive_level_3"],
    "My_own": ["fake_send_middle_agent"]
}

message_mapping_answers = {
    "test_message": ["fake_receive", "fake_send_middle_agent"],
    "test_message_level_1": ["fake_receive_level_2"],
    "test_message_level_2": ["fake_receive_level_3"] 
}


def compare_dicts(dict1, dict2):
    return_val = False
    return_reason = ""
    for key, val_1 in dict1.items():
        val_2 = dict2.get(key, "$no_value_here$")
        if val_1 == "no_value_here": 
            reason = f"Dictionary_2 has no value at key {key}"
            return return_val, reason
        elif val_2 != val_1:
            reason = f"Dictionary_2 has value {val_2} at key {key} instead of {val_1}"
            return return_val, reason 
    if len(list(dict2.keys())) > len(list(dict1.keys())):
        reason = f"Dictionary 2 has more entries than Dictionary 1"
        return return_val, reason 
    else:
        return_val = True
        reason = "No difference"
        return return_val, reason 


#Need to come up with several message types and system classes 
system_object = system_class.return_object(system_config=system)
system_object.print_configs(["addresses", "messages", "carriers", "handlers"])


address_configs = system_object.return_configs("address", "all")
result, reason = compare_dicts(addresses_answers, address_configs)
print("Testing Address Equivalence")
print(f"Result: {result} Reason: {reason}")

carrier_configs = system_object.return_configs("carrier", "all")
result, reason = compare_dicts(carrier_answers, carrier_configs)
print("Testing Carrier Config Equivalence")
print(f"Result: {result} Reason: {reason}")


handler_configs = system_object.return_configs("handler", "all")
result, reason = compare_dicts(handler_answers, handler_configs)
print("Testing Handler Config Equivalence")
print(f"Result: {result} Reason: {reason}")


message_configs = system_object.return_configs("message", "all")
result, reason = compare_dicts(message_answers, message_configs)
print("Testing Message Config Equivalence")
print(f"Result: {result} Reason: {reason}")

## Now test address mapping
print()
print("Test Address Mapping")

carrier_mapped_addresses = system_object.return_address_mapping("carrier", "all")
result, reason = compare_dicts(carrier_mapping_answers, carrier_mapped_addresses)
print("Testing Carrier Address Mapping Equivalence")
print(f"Result: {result} Reason: {reason}")


handler_mapped_addresses = system_object.return_address_mapping("handler", "all")
result, reason = compare_dicts(handler_mapping_answers, handler_mapped_addresses)
print("Testing Handler Address Mapping Equivalence")
print(f"Result: {result} Reason: {reason}")


message_mapped_addresses = system_object.return_address_mapping("message", "all")
result, reason = compare_dicts(message_mapping_answers, message_mapped_addresses)
print("Testing Handler Message Mapping Equivalence")
print(f"Result: {result} Reason: {reason}")


#system_object = return_address_mapping(self, config_type, config_names)