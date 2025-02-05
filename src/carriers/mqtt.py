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
        self.config = config.copy() 
        self.monitor_connection = self.config.get("monitor_connection", False)
        self.send_addresses = send_addresses.copy()
        self.receive_addresses = receive_addresses.copy()
        self.message_configs = message_configs.copy()
        #See if we need to be passing in mqtt topic in our message
        self.include_topic = self.config.get("include_topic", False)
        self.flood_seconds_tolerance = self.config.get("flood_seconds_tolerance", 2)

        #Set up connection info 
        self.mqtt_url = self.config.get("mqtt_url", '127.0.0.1')
        self.mqtt_port = self.config.get("mqtt_port", '1883')
        self.mqtt_username = self.config.get("mqtt_username", None)
        self.mqtt_password = self.config.get("mqtt_password", None)
        self.qos = self.config.get("qos", 1)
        self.client_id = self.config.get("client_id", "default")
        self.system_id = self.config.get("system_id", "default")
        self.client_id = f"{self.client_id}_{self.system_id}"
        self.protocol_num = self.config.get("version", 5)
        #if self.protocol_num == 5:
        self.protocol = paho.MQTTv5
        self.num_missed_connections = 0
        self.alerted_lost_connection = False 
        self.address_time_dict = {}
        #else:
        #    self.protocol = paho.MQTTv3
        if self.protocol_num == 5:
            self.client = paho.Client(client_id=self.client_id, protocol=self.protocol)
        else:
            self.client = paho.Client(client_id=self.client_id)
        #Set up security info 
        if self.mqtt_username and self.mqtt_password:
            self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
            self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        #Set up client
        self.client.on_connect = self.on_connect
        #self.topic_address_mappings()
        self.sent_entries = {}
        self.loop_forever = False
        self.loop_start=False
        #self.startup_connection_dealt = False

        self.mapping_dict = util.forward_backward_map_additional_info([self.send_addresses, self.receive_addresses])
        #Set up message definitions for looking up messages 
        logging.info("Initialized mqtt carrier")


    def fake_print(self):
        print("Fake print - inside MQTT task")
        

    def check_topic_map(self, topic_name):
        """
        String matches topic names 
        NEED TO CHECK - MARKED 
        """
        #address_map = self.topic_address_mapping.get(topic_name, None)
        address_map = self.mapping_dict["topic"]["value"].get(topic_name, None)
        if address_map == None:
            #for key, value in self.topic_address_mapping.items():
            for key, value in self.mapping_dict["topic"]["value"].items():
                if key in topic_name:
                    address_map = value
        return address_map 


    def receive_message(self, client, userdata, message):
        """
        Takes in client, userdata, and message
        Follows the paho function footprint for receiving a message
        Each subscription gets it's own instance of this callback. 
        """
        #Need to change so it can handle nested topics!!
        #MARKED 
        #Get the topic
        try:
            topic_name = message.topic
            #Debug for now
            logging.debug(f"Got message {json.loads(message.payload)} on topic {message.topic}")
            #Map it to an address
            address_name = self.check_topic_map(topic_name)
            message_body = json.loads(message.payload)
            logging.debug(f"Received Message {topic_name} {message_body} {address_name}")
            if self.include_topic:
                message_body["topic"] = topic_name
            if address_name:
                #This is where we want to check for flooding
                #If the last send time was too soon - don't post it 
                curr_time = util.get_today_date_time_utc()
                last_time = self.address_time_dict.get(address_name, None)
                #Flood seconds tolerance is in configuration to prevent flooding 
                if last_time == None or util.compare_seconds(last_time, curr_time) > self.flood_seconds_tolerance:
                    #Envelope and post it
                    enveloped_message = system_object.system.envelope_message(message_body, address_name)
                    system_object.system.post_messages(enveloped_message, address_name)
                self.address_time_dict[address_name] = curr_time
        except Exception as e:
            logging.error(f"Could not receive message {message}; {e}", exc_info=True)

    def get_subscriptions(self, addresses):
        """
        Takes in addresses
        Get the list of all relevant subscriptions topics
        based on the addresses, topic/mapping dict 
        """
        subscriptions = []
        for address_name in addresses:
            topic = self.mapping_dict["topic"]["address_name"].get(address_name, None)
            subscriptions.append(f"{topic}/#")
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
                    if self.protocol_num == 5:
                        self.client.connect(self.mqtt_url, port=self.mqtt_port, clean_start=False)
                    else:
                        self.client.connect(self.mqtt_url, port=self.mqtt_port)
            else:
                if self.protocol_num == 5:
                    self.client.connect(self.mqtt_url, port=self.mqtt_port, clean_start=False)
                else:
                    self.client.connect(self.mqtt_url, port=self.mqtt_port)
        except Exception as e:
            logging.error(f'Could not connect client {self.client_id}', exc_info=True)

    def on_connect(self, client, userdata, flags, reasonCode, properties=None):
        """
        On the connection, subscribe to all relevant subscriptions already identified 
        for the client 
        """
        if reasonCode==0:
            if userdata == None:
                userdata = []
            if isinstance(userdata, list):
                for topic in userdata:
                    logging.info(f'{topic} connected, return code: {reasonCode}')
                    #Need to revisit qos?
                    self.client.subscribe(topic, qos=self.qos)
        else:
            logging.error(f'{self.client_id} bad Connection, return code: {reasonCode}') 


    #MARKED - may want to make this one function 
    #Disconnects the client from the broker 
    def disconnect(self):
        """
        Takes no arguments
        Disconnect the client from the broker 
        """
        try:
            self.client.loop_stop()
            self.loop_start = False
            self.loop_forever = False
        except Exception as e:
            logging.error(f'{self.client_id} loop stop did not terminate', exc_info=True)
        #Add try/except here?
        try:
            self.client.disconnect()
        except Exception as e:
            logging.error(f"{self.client_id} could not disconnect", exc_info=True)
        logging.info("MQTT disconnected")



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

    
    
    def post_lost_connection_message(self):
        """
        Posts a lost connection message from mqtt
        driver to the system 
        """
        try:
            message_type = "connection_status"
            lost_connection_message = {
                "id": "mqtt",
                "time": util.get_today_date_time_utc(),
                "connection_status": "disconnect"
            }

            enveloped_message = system_object.system.envelope_message_by_type(lost_connection_message, message_type)
            system_object.system.post_messages_by_type(enveloped_message, message_type)
        except Exception as e:
            logging.debug(f"Could not post lost connection message from mqtt; {e}", exc_info=True)


    def post_restored_connection_message(self): 
        """
        Posts a restored connection message from mqtt
        driver to the system 
        """
        try:
            message_type = "connection_status"
            restored_connection_message = {
                "id": "mqtt",
                "time": util.get_today_date_time_utc(),
                "connection_status": "reconnect"
            }
            enveloped_message = system_object.system.envelope_message_by_type(restored_connection_message, message_type)
            system_object.system.post_messages_by_type(enveloped_message, message_type)
        except Exception as e:
            logging.debug(f"Could not post restored connection message from mqtt; {e}", exc_info=True)

    
    def check_connection_status(self, rc): 
        """
        This function checks that status of the MQTT
        message send to determine if a connection was 
        lost. This might be something to enable on the 
        configuration. 
        If the connection is lost, it posts a connection 
        lost message
        If a previously lost connection was restored, it 
        posts a connection restorted message 
        """
        try:
            #If the message didn't send 
            if rc != 0:
                self.num_missed_connections += 1
                if self.num_missed_connections > 2 and self.alerted_lost_connection == False:
                    logging.debug(f"Generating lost connection from mqtt")
                    self.alerted_lost_connection = True 
                    self.post_lost_connection_message()
            #If it did send, only send a restored connection message 
            #If we noticed a disconnect earlier, or if the system
            #itself is disconnected 
            else:
                system_connection_lost = system_object.system.return_system_lost_connection()
                logging.debug(f"Lost System Connection in MQTT {system_connection_lost}")
                self.num_missed_connections = 0 
                #If we noticed that we have alerted a lost connection, or 
                #The system knows it had a lost connection 
                if self.alerted_lost_connection or system_connection_lost:
                    logging.debug(f"Generating restored connection from mqtt")
                    if self.alerted_lost_connection == True:
                        self.alerted_lost_connection = False
                    self.post_restored_connection_message()
                    
        except Exception as e:
            logging.error("Could not check system mqtt connection status")
            

    
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
            #If we are monitoring the connection, go ahead and 
            #check for it. 
            if self.monitor_connection:
                self.check_connection_status(msgpub.rc)
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
                #topic = self.address_topic_mapping.get(address_name, None)
                topic = self.mapping_dict["topic"]["address_name"].get(address_name, None)
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
                            #Add the gateway id it came from 
                            content["gateway_id"] = self.system_id
                            #Since it's coming directly from mqtt,
                            #We'll say the source is direct 
                            content["source"] = "direct"
                            return_val = self.publish(topic, content)
                    self.sent_entries[topic] = new_entry_ids
            except Exception as e:
                logging.error(f"Could not publish message on address {address_name}", exc_info=True)
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return MQTT_Client(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)
