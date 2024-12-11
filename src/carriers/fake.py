import sys
import time 
sys.path.append("../scarecro")
import system_object
import util.util as util 
import logging 


class Fake():
    def __init__(self, config, send_addresses, receive_addresses, message_configs):
        self.name = config.get("name", None)
        self.send_addresses = send_addresses 
        self.receive_addresses = receive_addresses
        self.message_configs = message_configs
        print("I'm init'ing")
        #Make a table mapping messages to addresses?  


    def return_message_type_matching_address(self):
        pass 

    def get_address_matching_message(self):
        pass 

    #Splitting of message types will actually be up to 
    #The system logic  - might need to make that a param,
    #actually, when it comes to dealing with shared objects. 


    def envelope_spoofed_message(self, id_val, time, content):
        spoofed_message = {
            "msg_type": "test_message",
            "msg_id": id_val,
            "msg_time": time,
            "msg_content": content 
        } 
        return spoofed_message.copy()


    def get_spoofed_message(self, id_val=1, duration="interval"):
        spoofed_message_content = {
            "id": duration,
            "time": util.get_today_date_time_local(),
            "place": "here",
            "person": "you!",
            "duration": duration 
        }
        message = self.envelope_spoofed_message(spoofed_message_content["id"], spoofed_message_content["time"], spoofed_message_content)
        return message

    def receive(self, address_names, duration):
        """
        Receives a list of addresses (all with same duration). Depending 
        on the duration and the address, it sets itself
        up to 'receive' spoofed messages and post them
        to the system post office along with an address 
        """
        #first_address = address_names[0]
        #address_def = self.receive_addresses.get(first_address, {})
        #duration = address_def.get("duration", "as_needed")
        if str(duration).isnumeric():
            spoofed_message = self.get_spoofed_message(duration=duration)
            print("Receiving a message on an interval")
            system_object.system.post_messages(spoofed_message, address_names[0])
            system_object.system.print_message_entries_dict()

        elif duration == "as_needed":
            spoofed_message = self.get_spoofed_message(duration=duration)
            print("Receiving a message as needed")
            system_object.system.post_messages(spoofed_message, address_names[0])
            system_object.system.print_message_entries_dict()

        elif duration == "on_message":
            spoofed_message = self.get_spoofed_message(duration=duration)
            print("Receiving a message, because we received another message ")
            system_object.system.post_messages(spoofed_message, address_names[0])
            system_object.system.print_message_entries_dict()

        elif duration == "always":
            print("Creating a forever listener")
            spoofed_message = self.get_spoofed_message(duration=duration)
            #Have us wait forever, but receive a message every 20 seconds
            prev = time.time()
            curr = time.time()
            while True:
                if curr - prev > 20:
                    prev = curr
                    print("Receiving a message, from a forever listener")
                    system_object.system.post_messages(spoofed_message, address_names[0])
                    system_object.system.print_message_entries_dict()
                curr = time.time()


    def spoof_message_send(self,messages):
        print("SPOOF SENDING")
        print(f"Sending {len(messages)} messages")
        for message in messages:
            print(message)

    def disconnect(self):
        """
        In current implementation, function takes no arguments
        And only prints a message to the console. 
        """
        logging.info("Disconnect Fake Carrier: No actions needed for Fake Carrier disconnect in this driver.") 


    def send(self, address_names, duration, entry_ids=[]):
        #Going to get the message type from the system message table. 
        #first_address = address_names[0]
        #address_def = self.send_addresses.get(first_address, {})
        #duration = address_def.get("duration", "as_needed")
        if str(duration).isnumeric():
            print("Sending a message on an interval")
            messages = system_object.system.pickup_messages(address_names[0], entry_ids=entry_ids)
            self.spoof_message_send(messages)

        elif duration == "as_needed":
            print("Sending a message as needed")
            messages = system_object.system.pickup_messages(address_names[0], entry_ids=entry_ids)
            self.spoof_message_send(messages)

        elif duration == "on_message":
            print("Sending a message, because we received a message ")
            messages =system_object.system.pickup_messages(address_names[0], entry_ids=entry_ids)
            self.spoof_message_send(messages)

        elif duration == "always":
            print("Sending on a forever sender")
            #Have us wait forever, but receive a message every 20 seconds
            prev = time.time()
            curr = time.time()
            while True:
                if curr - prev > 20:
                    prev = curr
                    print("Send a message, from a forever sender")
                    messages = system_object.system.pickup_messages(address_names[0], entry_ids=entry_ids)
                    self.spoof_message_send(messages)
                curr = time.time()


    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return Fake(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)




    
