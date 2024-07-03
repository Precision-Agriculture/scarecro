import sys 
import logging 
import json
from threading  import Thread
import time

sys.path.append("../scarecro")
import system_object
from subprocess import PIPE, Popen, STDOUT

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty 
ON_POSIX = 'posix' in sys.builtin_module_names


class Radio_433():
    """
    Driver for 433 MHz Radio Communication with T820T2 SDR
    """
    def __init__(self, config, send_addresses, receive_addresses, message_configs):
        """
        This driver doesn't really need anything configuration-wise
        String matches and drivers are provided on an address level 
        """
        #For mongo, need to know if gateway or middle agent
        #Because gateways use slightly outdated version. 
        self.config = config.copy()
        self.send_addresses = send_addresses.copy()
        self.receive_addresses = receive_addresses.copy()
        self.message_configs = message_configs.copy()
        self.create_mappings()
        self.cmd = ['/usr/local/bin/rtl_433', '-q', '-M', 'level', '-F', 'json']
        logging.info("Initialized 433_radio carrier")


    def create_mappings(self):
        """
        Mappings here instead of using system function
        Due to the possibility of mutliple string matches 
        """
        matches_address_mapping = {}
        address_matches_mapping = {}
        driver_address_mapping = {}
        address_driver_mapping = {}

        all_addresses = {**self.send_addresses, **self.receive_addresses}
        for address_name, address_config in all_addresses.items():
            add_info = address_config.get("additional_info", {})
            string_matches = add_info.get("string_matches", [])
            driver = add_info.get("driver", None)
            driver_address_mapping[driver] = address_name
            address_driver_mapping[address_name] = driver
            for match in string_matches:
                matches_address_mapping[match] = address_name
            address_matches_mapping[address_name] = string_matches
        self.matches_address_mapping = matches_address_mapping
        self.address_matches_mapping = address_matches_mapping
        self.driver_address_mapping = driver_address_mapping
        self.address_driver_mapping = address_driver_mapping


    def make_command(self, address_names):
        """
        Creates the command to run the 433 driver 
        """
        new_cmd = self.cmd.copy()
        for address_name in address_names:
            driver = self.address_driver_mapping.get(address_name, None)
            if driver:
                new_cmd.append('-R')
                new_cmd.append(str(driver))
        #Debug for now
        logging.debug(f"433 Command {new_cmd}")
        return new_cmd


    def enqueue_output(self, src, out, queue):
        try:
            for line in iter(out.readline, b''):
                queue.put(( src, line))
            out.close()
        except:
            pass 

    def connect(self, cmd):
        """
        Takes no arguments 
        starts the 433 connection thread
        """
        return_val = False
        try:
            self.p = Popen(cmd, stdout=PIPE, stderr=STDOUT, bufsize=1, close_fds=ON_POSIX)
            self.q = Queue()
            self.t = Thread(target=self.enqueue_output, args=('stdout', self.p.stdout, self.q))
            self.t.daemon = True # thread dies with the program
            self.t.start()
            self.pulse = 0
            self.last_sample_received = time.time() 
            return_val = True
            logging.info("starting 433MHz scanning")
            logging.info("######") 
        except Exception as e:
            logging.error(f"Could not start 433 thread {e}", exc_info=True)
        return return_val


    def disconnect(self):
        """
        Takes no arguments 
        Disconnects from 433  
        """
        logging.info( "Killing SDR Thread")
        self.p.kill()
        self.t.join()
        pass 

    def reconnect(self, cmd):
        """
        Reconnects to the database, if operation
        different from connect/disconnect
        """
        logging.info(">>>>>>>>>>>>>>restarting SDR thread.....")
        self.last_sample_received = time.time()
        #if (config.SWDEBUG):
        self.disconnect()
        self.connect(cmd) 

  
    def process_sample(self, sLine):
        reading = {}
        try:
            for potential_match in list(self.matches_address_mapping.keys()):
                if sLine.find(potential_match) != -1:
                    #debug
                    logging.debug(f"Processing sample {sLine}")
                    address_name = self.matches_address_mapping.get(potential_match, None)
                    if address_name:
                        reading_dict = sLine
                        enveloped_message = system_object.system.envelope_message(json.loads(sLine), address_name)
                        system_object.system.post_messages(enveloped_message, address_name)
                    break 
        except Exception as e:
            logging.error(f'Could not process sLine in radio_433 protocol', exc_info=True)

    def listen(self, cmd):
        """
        Takes in address names. 
        Listen for a sensor reading
        """
        if self.time_since_last_sample > 720.0:
                #Reconnect if it's been 12 min since last reading 
                self.reconnect(cmd)
        try:
            src, line = self.q.get(timeout = 1)
        except Empty:
            self.pulse += 1
        else: # got line
            self.pulse -= 1
            sLine = line.decode()
            self.last_sample_received = time.time()
            self.process_sample(sLine)
            sys.stdout.flush()


    def receive(self, address_names, duration):
        """
        Takes in the address names and the duration
        For this driver, the duration will pretty much always be 'always'
        You could potentally define other behavior, like listening 
        for a set amount of time.  
        """
        cmd = self.make_command(address_names)
        self.connect(cmd)
        self.time_since_last_sample = time.time() - self.last_sample_received
        if duration == "always":
            while True:
                self.time_since_last_sample = time.time() - self.last_sample_received
                self.listen(cmd)
        else:
            try:
                prev_time = time.time()
                curr_time = time.time()
                time_out = curr_time-prev_time
                #Heuristic listening time - could have this configured 
                while time_out < 50.0:
                    self.listen(cmd)
                    curr_time = time.time()
                    time_out = curr_time-prev_time
                self.disconnect()
            except Exception as e:
                logging.error(f"Could not listen on for period of time on 433 {e}")
            
    def send(self, address_names, duration, entry_ids=[]):
        """
        Not really defined for this driver 
        Right now, driver only capable of listening on 433 radio,
        not sending
        """
        pass 
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return Radio_433(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)

         