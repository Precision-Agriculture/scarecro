import sys
import time 
import logging 
import json 
import paho.mqtt.client as paho
from paho import mqtt
sys.path.append("../scarecro")
import system_object
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
        #Set up connection info 
        self.mqtt_url = self.config.get("mqtt_url", '127.0.0.1')
        self.mqtt_port = self.config.get("mqtt_port", '1883')
        self.mqtt_username = self.config.get("mqtt_username", None)
        self.mqtt_password = self.config.get("mqtt_password", None)
        self.qos = self.config.get("qos", 1)
        self.client_id = self.config.get("client_id", "default")
        #self.protocol_num = self.config.get("version", 5)
        #if self.protocol_num == 5:
        self.protocol = paho.MQTTv5
        #else:
        #    self.protocol = paho.MQTTv3
        self.client = paho.Client(client_id=self.client_id, protocol=self.protocol)
        #Set up security info 
        if self.mqtt_username and self.mqtt_password:
            self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
            self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        #Set up client
        self.client.on_connect = self.on_connect
        self.topic_address_mappings()
        self.sent_entries = {}
        self.loop_forever = False
        self.loop_start=False
        #Set up message definitions for looking up messages 


    def topic_address_mappings(self):
        """
        Takes no arguments 
        Use addresses to create a topic-address mapping dictionary
        And an address-topic mapping dictionary 
        """
        topic_address_mapping = {}
        address_topic_mapping = {} 
        all_addresses = {**self.send_addresses, **self.receive_addresses}
        #For every address, map it to a topic and vice versa 
        for address_name, address_config in all_addresses.items():
            additional_info = address_config.get("additional_info", {})
            topic = additional_info.get("topic", None)
            topic_address_mapping[topic] = address_name
            address_topic_mapping[address_name] = topic
        self.topic_address_mapping = topic_address_mapping
        self.address_topic_mapping = address_topic_mapping

    def receive_message(self, client, userdata, message):
        """
        Takes in client, userdata, and message
        Follows the paho function footprint for receiving a message
        Each subscription gets it's own instance of this callback. 
        """
        #Get the topic
        topic_name = message.topic
        #Debug for now
        logging.debug(f"Got message {json.loads(message.payload)} on topic {message.topic}")
        #Map it to an address
        address_name = self.topic_address_mapping.get(topic_name, None)
        if address_name:
            #Post it
            enveloped_message = system_object.system.envelope_message(json.loads(message.payload), address_name)
            system_object.system.post_messages(enveloped_message, address_name)
            #logging.debug(system_object.system.print_message_entries_dict())


    def get_subscriptions(self, addresses):
        """
        Takes in addresses
        Get the list of all relevant subscriptions topics
        based on the addresses, topic/mapping dict 
        """
        subscriptions = []
        for address_name in addresses:
            subscriptions.append(self.address_topic_mapping.get(address_name, None))
        return subscriptions

     #Connects to the broker. 
    def connect(self, reconnect=False):
        """
        Takes an optional reconnect argument, defaults to False 
        If already connected and we , it disconnects and reconnects to the broker. 
        """
        try:
            if self.client.is_connected():
                #If we want to reconnect 
                if reconnect:
                    self.disconnect_from_broker()
                    self.client.connect(self.mqtt_url, port=self.mqtt_port, clean_start=False)
            else:
                self.client.connect(self.mqtt_url, port=self.mqtt_port, clean_start=False)
        except Exception as e:
            logging.error(f'Could not connect client {self.client_id}', exc_info=True)

    def on_connect(self, client, userdata, flags, reasonCode, properties=None):
        """
        On the connection, subscribe to all relevant subscriptions already identified 
        for the client 
        """
        if reasonCode==0:
            if userdata != []:
                for topic in userdata:
                    logging.info(f'{topic} connected, return code: {reasonCode}')
                    #Need to revisit qos?
                    self.client.subscribe(topic, qos=self.qos)
        else:
            logging.error(f'{self.client_id} bad Connection, return code: {reasonCode}') 


    #Disconnects the client from the broker 
    def disconnect_from_broker(self):
        """
        Disconnect the client from the broker 
        """
        try:
            self.client.loop_stop()
            self.loop_start = False
            self.loop_forever = False
        except Exception as e:
            logging.error(f'{self.client_id} loop stop did not terminate', exc_info=True)
        #Add try/except here?
        self.client.disconnect()


    def run(self, duration="as_needed"):
        """
        Takes an optional duration argument (defaults to 'as_needed')
        If duration is always, runs loop_forever is that is not already the case 
        For others, runs loop_start if that or loop_forever not already in play 
        """
        #Loop forever if not already
        if duration == "always" and self.loop_forever == False:
            try:
                self.loop_forever = True
                self.client.loop_forever()
            except Exception as e:
                logging.error(f'Could not loop forever client {self.client_id}', exc_info=True)
        #Loop start if not already 
        else:
            if self.loop_forever == False and self.loop_start == False:
                try:
                    self.loop_start = True
                    self.client.loop_start()
                except Exception as e:
                    logging.error(f'Could not loop start client {self.client_id}', exc_info=True)

    def publish(self, topic, message):
        """
        publish the message on the topic 
        """
        return_val = False
        try:
            msgpub = self.client.publish(topic, json.dumps(message), qos=self.qos)
            logging.info(f'MSGPUB RC: {msgpub.rc} on topic {topic}')
            if msgpub.rc != paho.MQTT_ERR_SUCCESS:
                logging.error(f'Could not publish message {message} on topic {topic}')
                return_val = False
            else:
                return_val = True
        except Exception as e:
            logging.error(f'Could not publish message {self.client_id}', exc_info=True)
            return_val = False
        return return_val


    def receive(self, address_names, duration):
        """
        High level exposure function of the carrier 
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
        #Connect 
        self.connect(reconnect=True)
        self.run(duration=duration)

    def send(self, address_names, duration, entry_ids=[]):
        """
        High level exposure function of the carrier
        Takes in an optional list of entry ids
        Grabs the messages and publishes them, optionally filtering by ID 
        No "always" duration is really defined for this driver, don't use with always 
        """
        for address_name in address_names:
            try:
                #Look up the topic
                topic = self.address_topic_mapping.get(address_name, None)
                if topic:
                    #Get the messages
                    messages = system_object.system.pickup_messages(address_name, entry_ids=entry_ids)
                    new_entry_ids = []
                    sent_entries = self.sent_entries.get(topic, [])
                    #Send each message individually 
                    if messages != []:
                        self.connect(reconnect=False)
                        self.run(duration=duration)
                    for message in messages:
                        entry_id = message.get("entry_id", None)
                        new_entry_ids.append(entry_id)
                        
                        #Send only if we haven't already sent it
                        if entry_id not in sent_entries:
                            content = message.get("msg_content", {})
                            return_val = self.publish(topic, content)
                    self.sent_entries[topic] = new_entry_ids
            except Exception as e:
                logging.error(f"Could not publish message on address {address_name}", exc_info=True)
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return MQTT_Client(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)

         