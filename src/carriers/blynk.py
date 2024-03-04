import sys
import time 
import logging 
import json 
import paho.mqtt.client as paho
from paho import mqtt
sys.path.append("../scarecro")
import system_object
import util.util as util 
#Help from the documentation here: https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#multiple


class MQTT_Client():
    def __init__(self, config, send_addresses, receive_addresses, message_configs):
        """
        MQTT Clients need in the config: 
            mqtt_url: the url of the mqtt connection
            mqtt_port: the port of the mqtt connection. (Default 1883)
            mqtt_username: username for connection, defaults to None
            mqtt_password: password for connection, defaults to None
            client_id: client id of connection, very important to have 
            qos: qos of mqtt messages. Defaults to 1. 
        """
        #arguments passed in 
        self.config = config 
        self.send_addresses = send_addresses 
        self.receive_addresses = receive_addresses
        self.message_configs = message_configs
        


    def topic_address_mappings(self):
        """
        Takes no arguments 
        Use addresses to create a topic-address mapping dictionary
        And an address-topic mapping dictionary 
        """
        topic_address_mapping = {}
        address_topic_mapping = {} 

        for address_name, address_config in self.receive_addresses.items():
            additional_info = address_config.get("additional_info", {})
            topic = additional_info.get("topic", None)
            topic_address_mapping[topic] = address_name
            address_topic_mapping[address_name] = topic
        for address_name, address_config in self.send_addresses.items():
            additional_info = address_config.get("additional_info", {})
            topic = additional_info.get("topic", None)
            topic_address_mapping[topic] = address_name
            address_topic_mapping[address_name] = topic
        self.topic_address_mapping = topic_address_mapping
        self.address_topic_mapping = address_topic_mapping

    def envelope_message(self, message, address_name):
        """
        Takes in the message and address name and envelopes the 
        message
        Could really do this on the system object level. 
        """
        #Get message type from address 
        address_config = self.receive_addresses.get(address_name, {})
        message_type = address_config.get("message_type", "default")
        #Get message id from message definition
        message_config = self.message_configs.get(message_type, {})
        #Debug
        print("Message config", message_config)
        id_field = message_config.get("id_field", "id")
        message_id = message.get(id_field)
        time = util.get_today_date_time_utc()
        #Envelope it 
        enveloped_message = {
            "msg_id": message_id,
            "msg_time": time,
            "msg_type": message_type,
            "msg_content": message
        }
        return enveloped_message
        


    def receive(self, address_names):
        """
        Receives a list of addresses (all with same duration). Depending 
        on the duration and the address, it sets itself
        up to 'receive' spoofed messages and post them
        to the system post office along with an address 
        """
        #Add the current subscriptions to the userdata 
        try:
            current_user_data = self.client.user_data_get()
        except Exception as e:
            current_user_data = []
        if not isinstance(current_user_data, list):
            current_user_data = []
        subscriptions = self.get_subscriptions(address_names)
        for subscription in subscriptions:
            #Add the subscription topic to the userdata 
            if subscription not in current_user_data:
                current_user_data.append(subscription)
            #Add the callbacks for the subscriptions
            self.client.message_callback_add(subscription, self.receive_message)
        #Set the userdata 
        self.client.user_data_set(current_user_data)
        #Check the duration, then connect and run or connect and run forever
        first_address = self.receive_addresses.get(address_names[0], {})
        duration = first_address.get("duration", "as_needed")
        #Connect 
        if duration == "always":
            #Debug for now
            print("in a forever mqtt listener")
            self.connect_and_run_forever()
        else:
            self.connect_and_run()


    def send(self, address_names, entry_ids=[]):
        """
        Takes in an optional list of entry ids
        Grabs the messages and publishes them, optionally filtering by ID 
        """
        #Debug
        print("Going to send!")
        for address_name in address_names:
            print("Here!")
            try:
                #Look up the topic
                topic = self.address_topic_mapping.get(address_name, None)
                print("Topic", topic)
                if topic:
                    #Get the messages
                    messages = system_object.system.pickup_messages(address_name, entry_ids=entry_ids)
                    new_entry_ids = []
                    for message in messages:
                        entry_id = message.get("entry_id", None)
                        new_entry_ids.append(entry_id)
                        if entry_id not in self.sent_entries:
                            content = message.get("msg_content", {})
                            return_val = self.publish(topic, content)
                            #Debug. CHANGE
                            print(return_val)
                    self.sent_entries = new_entry_ids
                    print(self.sent_entries)
            except Exception as e:
                logging.error(f"Could not publish message on address {address_name}", exc_info=True)
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return MQTT_Client(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)

