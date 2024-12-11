# The `Temptest_UDP` class is designed to listen for UDP broadcasts from a WeatherFlow HUB and parse
# different types of observation data.

import sys
import socket
import select
import time
import logging
import json
import pytz
from datetime import datetime
from multiprocessing import Process

sys.path.append("../scarecro")
import system_object

# The `OBS_ST_MAP` is a mapping of observation data fields for the 'obs_st' type observations. Each
# entry in the list represents a tuple where the first element is the name of the observation field
# and the second element is the unit of measurement for that field. This mapping is used to parse and
# format the observation data received from the WeatherFlow HUB for the 'obs_st' type observations. It
# provides a structured way to interpret and display the different types of weather data such as wind
# speed, temperature, pressure, humidity, and other environmental parameters.
OBS_ST_MAP = [
    'Time_Seconds',                        # ('Time Epoch', 'Seconds'),
    'Wind Lull Speed',             # ('Wind Lull (minimum 3 second sample)', 'm/s'),
    'Average Wind Speed',          # ('Wind Avg (average over report interval)', 'm/s'),
    'Wind Gust Speed',             # ('Wind Gust (maximum 3 second sample)', 'm/s'),
    'Wind Direction',              # ('Wind Direction', 'Degrees'),
    'Wind Sample Interval',        # ('Wind Sample Interval', 'seconds'),
    'Station Pressure',            # ('Station Pressure', 'MB'),
    'Air Temperature',             # ('Air Temperature', 'C'),
    'Relative Humidity',           # ('Relative Humidity', '%'),
    'Illuminance',                 # ('Illuminance', 'Lux'),
    'UV Index',                    # ('UV', 'Index'),
    'Solar Radiation',             # ('Solar Radiation', 'W/m^2'),
    'Precipitation Accumulated',   # ('Precip Accumulated', 'mm'),
    'Precipitation Type',          # ('Precipitation Type', '0 = none, 1 = rain, 2 = hail'),
    'Lightning Strike Avg Distance', # ('Lightning Strike Avg Distance', 'km'),
    'Lightning Strike Count',      # ('Lightning Strike Count', ''),
    'Battery',                     # ('Battery', 'Volts'),
    'Report Interval'              # ('Report Interval', 'Minutes')
]

# The `RAPID_WIND_MAP` is a mapping that defines the structure of the data fields for the 'rapid_wind'
# type observations received from the WeatherFlow HUB. Each entry in the list represents a tuple where
# the first element is the name of the observation field and the second element is the unit of
# measurement for that field.
RAPID_WIND_MAP = [
    'Time',           # ('Time Epoch', 'Seconds'),
    'Wind Speed',     # ('Wind Speed', 'm/s'),
    'Wind Direction'  # ('Wind Direction', 'Degrees')
]

# The `EVT_STRIKE_MAP` is a mapping that defines the structure of the data fields for the 'evt_strike'
# type observations received from the WeatherFlow HUB. Each entry in the list represents a tuple where
# the first element is the name of the observation field and the second element is the unit of
# measurement for that field. In this case, the fields included in the mapping are 'Time Epoch'
# (measured in seconds), 'Distance' (measured in kilometers), and 'Energy' (unit unspecified). This
# mapping provides a structured way to interpret and handle the lightning strike observation data
# received from the WeatherFlow HUB.
EVT_STRIKE_MAP = [
    'Time',       # ('Time Epoch', 'Seconds'),
    'Distance',   # ('Distance', 'km'),
    'Energy'      # ('Energy', '')
]

class Tempest_UDP():
    def __init__(self, config, send_addresses, receive_addresses, message_configs):
        self.logger = logging.getLogger('Tempest_UDP')
        if logging.root.level <= logging.DEBUG:
            logging.getLogger('Tempest_UDP').setLevel(logging.DEBUG)
            #self.logger.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
        else:
            logging.getLogger('Tempest_UDP').setLevel(logging.INFO)
            #self.logger.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
        self.config = config.copy()
        self.send_addresses = send_addresses.copy()
        self.receive_addresses = receive_addresses.copy()
        self.message_configs = message_configs.copy()

        self.BROADCAST_PORT = 50222 #port that WeatherFlow HUB braodcasts on
        self.BROADCAST_IP = '' #IP is blank as only broadcast messages will be received 
        self.socket_list = [self.create_broadcast_listener_socket()]
        self.process = Process(target=self.receive)
        self.logger.info("Intialized TempestUDP Carrier")

    def create_broadcast_listener_socket(self):
        """
        The function creates a UDP socket for listening to broadcast messages on a specified IP address
        and port.
        """
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # create UDP Socket
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #set socket to be able to be reused
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #set socket to broadcast mode
        broadcast_socket.bind((self.BROADCAST_IP, self.BROADCAST_PORT)) #bind the socket to the IP and PORT
        
        return broadcast_socket
    
    def socket_error_handler(self):
        self.stop_listening()
        self.socket_list = [self.create_broadcast_listener_socket()]

    def read_data(self, s):
        """
        The function reads data from a socket, prints the message and address, decodes the data, and
        returns it.
        
        :param s: The parameter `s` in the `read_data` method is a socket object that is used for
        communication. It is typically created using the `socket` module in Python to establish a
        connection for sending and receiving data over a network
        :return: The `data` variable is being returned from the `receive` method.
        """
        data, addr = s.recvfrom(4096)
        self.logger.debug(f"Message from: {addr}")
        self.logger.debug(f'Received message: {data.decode("utf-8")}')
        return data

    def disconnect(self):
        """
        Takes no arguments, attempts to disconenct sockers
        """
        logging.info("Disconnected Tempest UDP")
        try:
            self.kill_process()
        except Exception as e:
            logging.error(f"Tempest UDP: Could not kill process: {e}", exc_info=True)

    def receive(self, address_names, duration):
        """
        The `receive` function continuously reads data from sockets, passes the data to the process data function, and
        envelopes and posts the processed message to the system.
        """
        if duration == 'always':
            while True:
                try:
                        #select function will wait until there is something to read from the socket
                        readable, writable, exceptional = select.select(self.socket_list, [], self.socket_list, 0)

                        #for each socket that is readable
                        for s in readable:
                            data = self.read_data(s)
                            
                            #convert to json
                            data_json = json.loads(data)

                            observations = self.process_data(data_json)
                            if observations != {}:
                                self.logger.info(f"Tempest message {observations}")
                                self.envelope_and_post_message(observations, address_names)
                except socket.error:
                    self.logger.error("Socket error occured! Reinitializing socket!")
                    self.socket_error_handler()

                #sleep keeps the loop from going too fast
                time.sleep(0.01) 
                            
    def process_data(self, data):
        """
        The function `process_data` processes different types of weather data messages and extracts
        relevant information based on the message type.
        
        :param data: The `data` parameter is a dictionary of data from the WeatherFlow hub that will be processed differently
        based on the value of the key `'type'`.
        :return: The `process_data` method returns the `observations` dictionary that is created based
        on the type of data received. The content of the `observations` dictionary varies depending on
        the type of data received (obs_st, rapid_wind, evt_strike). If the data type is 'evt_precip', a
        log message is generated instead of returning the observations dictionary. If the data type does
        not match any of the given types then it is a hub status message and it will be logged.
        """
        observations = {} 
        utc_curr_time = datetime.now(tz=pytz.UTC)
        time_string = utc_curr_time.strftime('%Y-%m-%dT%H:%M:%S.%f')

        if data['type'] == 'obs_st':
            #this will be temptest observation messages
            #adds values to OBS_ST_MAP
            observations = dict(zip(OBS_ST_MAP, data['obs'][0]))
            observations['time'] = time_string
            observations['id'] = data['serial_number']

        # if data['type'] == 'rapid_wind':
        #     #this will be rapid wind messages
        #     #adds values to RAPID_WIND_MAP
        #     observations = dict(zip(RAPID_WIND_MAP, data['ob']))
        #     observations['time'] = time_string
        #     observations['id'] = data['serial_number']

        # if data['type'] == 'evt_strike':
        #     #this will be lightning strike messages
        #     #adds values to EVT_STRIKE_MAP
        #     observations = dict(zip(EVT_STRIKE_MAP, data['evt']))
        #     observations['time'] = time_string
        #     observations['id'] = data['serial_number']

        # if data['type'] == 'evt_precip':
        #     #this will be precipitation messages
        #     time_stamp = time_string
        #     device_id = data['serial_number']
        #     self.logger.info(f'It started raining near device {device_id} at {time_stamp}!')
        else:
            #this will be the hub status messages
            self.logger.debug(data)
            
        return observations
                    
    def envelope_and_post_message(self, message, address_names):
        """
        The function `process_message` takes a message and envelopes it and then posts it to the system.
        
        :param message: The 'message' parameter will be the content of the message package.
        
        :param address_names: The 'address_names' parameter is the address of origin for the message(the list 
        will only contain one address in this case as the only source for messages will be the hub.)
        """
        try:
            for address_name in address_names:
                enveloped_message = system_object.system.envelope_message(message, address_name)
                system_object.system.post_messages(enveloped_message, address_name)
                
        except Exception as e:
                logging.error(f"Issue posting message {e}")
                #Wait a bit before trying again 
                time.sleep(300)   

    def start_process(self):
        """
        The function `start_process` starts a process using the `start` method of the `self.process`
        object.
        """
        self.process.start()
        self.logger.info('Temptest_UDP listener started!')

    def kill_process(self):
        """
        The `kill_process` function terminates a process if it is currently running and stops listening
        for any further events.
        """
        if self.process.is_alive():
            self.process.terminate()
            self.stop_listening()
            self.logger.info('Temptest_UDP listener stopped!')

    def restart_process(self):
        """
        The `restart_process` function kills the current process and then starts it again.
        """
        self.kill_process()
        self.start_process()
        self.logger.info('Restarted Temptest_UDP listener!')

    def stop_listening(self):
        """
        The function `stop_listening` shuts down and closes the broadcast listener socket.
        """
        self.shutdown_broadcast_listener_socket()
        self.close_broadcast_listener_socket()
        self.logger.info('Socket for Temptest_UDP listener shut down and closed!')

    def shutdown_broadcast_listener_socket(self):
        """
        The function `shutdown_broadcast_listener_socket` shuts down the broadcast listener socket.
        """
        for s in self.socket_list:
            s.shutdown(socket.SHUT_RDWR)

    def close_broadcast_listener_socket(self):
        """
        The function `close_broadcast_listener_socket` closes the broadcast listener socket.
        """
        for s in self.socket_list:
            s.close()

    def send(self):
        # This driver is for receiving UDP broadcasts from the WeatherFlow hub
        # there is no need for a send function as the hub will discard third
        # party communications
        pass

def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return Tempest_UDP(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)