import sys
import time 
import logging 
import paho.mqtt.client as paho
from paho import mqtt
import paho.mqtt.publish as pub

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
            spin_seconds: # of spin seconds to send/or receive something. Defaults to 10 
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
        self.client = paho.Client(client_id=self.client_id, protocol=paho.MQTTv5)
        #Set up security info 
        if self.mqtt_username and mqtt_password:
            self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
            self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        #Set up client
        self.client.on_connect = self.on_connect
        #Set up 

    def get_subscriptions(self):
        """
        Get the list of all relevant subscriptions 
        """
        subscriptions = []
        for address_name, address_config in self.receive_addresses.items():
            mqtt_config = address_config.get("additional_info", {})
            topic = mqtt_config.get("topic", None)
            subscriptions.append(topic)
        self.subscriptions = subscriptions

    def on_connect(self, client, userdata, flags, reasonCode, properties=None):
        """
        On the connection, subscribe to all relevant subscriptions 
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
        except Exception as e:
            logging.error(f'{self.client_id} loop stop did not terminate', exc_info=True)
        #Add try/except here?
        self.client.disconnect()

    def run(self):
        try:
            self.client.loop_start()
        except Exception as e:
            logging.error(f'Could not loop start client {self.client_id}', exc_info=True)


    def run_forever(self):
        try:
            self.client.loop_forever()
        except Exception as e:
            logging.error(f'Could not loop forever client {self.client_id}', exc_info=True)

    def run_stop(self):
        try:
            self.client.loop_stop()
        except Exception as e:
            logging.error(f'Could not loop stop client {self.client_id}', exc_info=True)

    #Just a convenience wrapper for starting a client (does not block)
    def connect_and_run(self):
        self.connect()
        self.run()

    #Just a convenience wrapper for starting a client that blocks 
    def connect_and_run_forever(self):
        self.connect()
        self.run_forever()


    def receive(self, address_names):
        """
        Receives a list of addresses (all with same duration). Depending 
        on the duration and the address, it sets itself
        up to 'receive' spoofed messages and post them
        to the system post office along with an address 
        """


    def send(self, address_names, entry_ids=[]):
        #Going to get the message type from the system message table. 
        
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return MQTT_Client(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)

