import sys
sys.path.append("../scarecro")
import importlib 
import json 
import logging 
import threading 

class System: 
    def __init__(self, system_config=None):
        """
        Initializes the system object 
        Takes in: an optional system configuration. If not provided, 
        it will default to the one labeled "system" in the
        configs/system folder 
        """
        #Initialize the system object - addresses, messages, handlers,
        #carriers, ... 
        self.init_system_object(system_config)

    ####### Configs ########################
    def init_system_object(self, system_config=None):
        """
        Take in an optional system config (for testing)
        And initializes the system 

        """
        #Get the system config 
        if system_config:
            self.system_config = system_config.copy()
        else:
            self.system_config = self.import_config("system", "system", "system")
        #Get the post office info - addresses, carriers, 
        #handlers, and messages 
        self.init_post_office_configs() 
        #Create the system message table 
        self.create_message_table()
        #Create the routing table
        self.build_routing_table()
        #Init the handlers 
        for handler_name in self.handlers:
            self.init_handler(handler_name)
        

        
    def init_post_office_configs(self):
        """
        Takes no arguments but uses the system config class variable
        to initialize post office object 
        """
        #Puts active messages in system class variable, or an empty list if
        #that keyword isn't present 
        #Systen storage objects 
        self.addresses = {}
        self.messages = {}
        self.handlers = {}
        self.carriers = {}
        #Get addresses
        active_addresses = self.system_config.get("addresses", [])
        for address in active_addresses:
            address_content = self.import_config("addresses", address, "address")
            self.addresses[address] = address_content
        #Get message configs
        self.messages = self.map_addresses(self.messages, self.addresses, "message_type")
        for message in self.messages.keys():
            self.messages[message]["content"] = self.import_config("messages", message, "message")
        #Get handler configs
        self.handlers = self.map_addresses(self.handlers, self.addresses, "handler")
        for handler in self.handlers.keys():
            self.handlers[handler]["content"] = self.import_config("handlers", handler, "handler")
        #Get carrier configs 
        self.carriers = self.map_addresses(self.carriers, self.addresses, "carrier")
        for carrier in self.carriers.keys():
            self.carriers[carrier]["content"] = self.import_config("carriers", carrier, "carrier")


    #Substitution dictionary for init'ing configs 
    def make_sub_dict(self, content, name):
        """
        Make the substitution dictionary for a configuration
        Based on the configuration's name and content
        Returns: dictionary of substitution mappings 
        """
        sub_dict = {
            "$name": name,
            "$msg_type": content.get("message_type", None)
        }
        return sub_dict

    #Also going to recursively call this 
    def substitution_content(self, name, content, sub_dict=None):
        """
        Take in the configuration name and content (and optionally)
        a higher level substitution dict and perform the substitution
        on the configuration content. 
        Returns: content wirh substition performed
        """
        subs = ["$name", "$msg_type"]
        if sub_dict == None:
            sub_dict = self.make_sub_dict(content, name)
        for key, val in content.items():
            if val in subs:
                content[key] = sub_dict[val]
            if isinstance(val, dict):
                content[key] = self.substitution_content(name, content[key], sub_dict=sub_dict)
        for key, val in content.items():
            if key in subs:
                sub = sub_dict[key]
                content[sub] = content[key]
                content.pop(key)
        return content  


    #Put in util function, possibly 
    def deep_update(self, base_dict, new_dict):
        """
        Takes in a base dictionary and a new dictionary to update it 
        with This is recursive for dictionary values, different 
        to the the python built-in update method 
        Returns: updated dictionary 
        """
        #Got help from a linked stack overflow site 
        for key_name, val in new_dict.items():
            #if isinstance(val, collections.abc.Mapping):
            if isinstance(val, dict):
                base_dict[key_name] = self.deep_update(base_dict.get(key_name, {}), val)
            else:
                base_dict[key_name] = val 
        return base_dict


    def inheritance(self, path_name, module_name, attribute, content):
        """
        This takes in content as well as the configuration path informatino
        (module, attribute, and path) and looks for and applies any inherited
        properties, in left to right order, with the main content overriding
        Returns: config content with the inheritance applied
        """
        inherited_content = content.get("inheritance", [])
        if inherited_content != []:
            sub_content_config = {}
            for sub_content_name in inherited_content:
                #Recursive call - get the inherited value
                sub_content = self.get_import_content(path_name, sub_content_name, attribute)
                #Also run inheritance recursively on the subcontent: 
                sub_content = self.inheritance(path_name, sub_content_name, attribute, sub_content)
                #Read in the inheritance first 
                sub_content_config = self.deep_update(sub_content_config, sub_content)
            content = self.deep_update(sub_content_config, content)
            content = sub_content_config
        return content 


    def get_import_content(self, path_name, module_name, attribute):
        """
        This takes in the path to the the imported, the module name 
        inside the folder path, and the attribute name to import
        Returns: the content tied to the attribute name in the imported file
        """
        content = {}
        try:
            import_string = f"{path_name}.{module_name}"
            content = getattr(importlib.import_module(import_string, package=None), attribute).copy()
        except Exception as e:
            logging.error(f"Could not import module {module_name}", exc_info=True) 
        return content 


    #Here, perform inheritance and sensor name substitution  
    def import_config(self, config_folder, module_name, attribute):
        """
        Specific import function for configs. Takes in the sub-config
        folder, the module name within the folder, and the attribute, 
        and applies the inheritance and substitution operators to the config

        Returns: The config content 
        """
        path_name = f"configs.{config_folder}"
        #Get the content
        content = self.get_import_content(path_name, module_name, attribute)
        #Run inheritance on the content 
        content = self.inheritance(path_name, module_name, attribute, content)
        content = self.substitution_content(module_name, content)
        return content

    def return_default_mapping_dict(self):
        """
        Returns the base system address and content mapping dictionary
        For system items like messages, carriers, and handlers
        """
        default_dict = {
            "addresses": [],
            "content": None,
        }
        return default_dict.copy()

    def map_addresses(self, content_dict, addresses, address_key):
        """
        This function takes in a blank dictionary, and maps the addresses
        it takes in that are associated with a specific content type
        (address key provided) 
        Returns: the inputed dictionary, now mapped to addresses in
        it's "addresses" field  
        """
        for address_name, address_val in addresses.items():
            content_key = address_val.get(address_key)
            #If that doesn't exist in the content dict, add it
            if content_dict.get(content_key, None) == None:
                content_dict[content_key] = self.return_default_mapping_dict()
            #Append this address to this content's address fields
            content_dict[content_key]["addresses"].append(address_name)
        return content_dict

    def print_configs(self, config_types):
        """
        Takes in a singular or list of config names 
        prints the configuation in the system dictionary 
        """
        if isinstance(config_types, list):
            for config_type in config_types:
                print(f"Configuration for {config_type}")
                print(json.dumps(getattr(self, config_type), indent=4, default=str))
        else:
            print(f"Configuration for {config_types}")
            print(json.dumps(getattr(self, config_types), indent=4, default=str))

    def get_config_object_from_config_type(self, config_type):
        """
        Returns the object storing configuration details based on 
        the configuration type provided 
        """
        return_object = {}
        if config_type == "address":
            return_object = self.addresses
        elif config_type == "handler":
            return_object = self.handlers
        elif config_type == "carrier":
            return_object = self.carriers
        elif config_type == "message":
            return_object = self.messages
        return return_object 

    def get_collapsed_to_content_config_dict(self, full_dict):
        return_dict = {}
        for key, value in full_dict.items():
            return_dict[key] = value.get("content", {}) 
        return return_dict 

    #Come back to this. 
    def return_configs(self, config_type, config_names):
        """
        Takes in a config type and a config name 
        config name can be a name, a list of names, or "all" 
        Return a dictionary where the keys are configuration names
        And the values are corresponding configurations 
        """
        return_val = {}
        #Get the object we need the config from 
        config_object = self.get_config_object_from_config_type(config_type)
        if config_names == "all":
            return_val = config_object.copy()
        elif isinstance(config_names, list):
            for sub_name in config_names: 
                return_val[sub_name] = config_object[sub_name].copy()
        else:
            return_val[sub_name] = config_object[sub_name].copy()
        #Collapse any configs that match content
        if config_type in ["handler", "carrier", "message"]:
            return_val = self.get_collapsed_to_content_config_dict(return_val)
        return return_val

    def get_address_mappings_from_config(self, full_dict):
        """
        Takes a dictionary of key: full config pairs
        And returns a dictionary of key: address_list pairs,
        where key is the name of the config 
        """
        return_dict = {}
        for key, value in full_dict.items():
            return_dict[key] = value.get("addresses", {}) 
        return return_dict 

    #Come back to this. 
    def return_address_mapping(self, config_type, config_names):
        """
        Takes in a config type and a config name 
        config name can be a name, a list of names, or "all" 
        Return a dictionary where the keys are configuration names
        And the values are corresponding configurations 
        """
        return_val = {}
        #Get the object we need the config from 
        config_object = self.get_config_object_from_config_type(config_type)
        if config_names == "all":
            return_val = config_object.copy()
        elif isinstance(config_names, list):
            for sub_name in config_names: 
                return_val[sub_name] = config_object[sub_name].copy()
        else:
            return_val[sub_name] = config_object[sub_name].copy()
        #Collapse any configs that match content
        return_val = self.get_address_mappings_from_config(return_val)
        return return_val

    ################# System Object for Routing ###################
    def build_routing_table(self):
        """
        Build the routing table for messages
        {
            message_type: {
                "address_1": {address_1_config_dict},
                "address_2": {address_2_config_dict},
                ...
            }
        }
        And set it to the routing_table class atrribute 
        """
        routing_dict = {}
        for message, message_dict in self.messages.items():
            message_addresses = message_dict.get("addresses", [])
            message_address_sub_dict = {} 
            for address in message_addresses:
                address_config = self.addresses.get(address, {})
                message_address_sub_dict[address] = address_config.copy()
            routing_dict[message] = message_address_sub_dict
        self.routing_table = routing_dict 

    def print_routing_table(self):
        """
        json dumps prints the routing table 
        """
        print(json.dumps(self.routing_table, indent=4))

    def run_messages_through_handler(self, message_type, messages, address):
        """
        Takes in the message type, list of messages, and the address dictionary
        It runs the handler function on the message
        It then returns the list of processed messages 
        """
        handler_name = address.get("handler", None)
        handler_function = address.get("handler_function", None)
        if handler_name and handler_function:
            #Get handler init 
            handler_dict = self.handlers.get(handler_name, {})
            handler_object = handler_dict.get("object", None)
            if handler_object:
                try:
                    #Run the function on it
                    handler_function = getattr(handler_object, handler_function)
                    messages = handler_function(message_type, messages)
                except Exception as e:
                    logging.error(f"Could not process with handler message of type {message_type}", exc_info=True)
        #Return the messages 
        return messages

    def send_messages_through_carrier(self, message_type, messages, address):
        """
        This function takes in the message type, list of messages, and the address
        dictionary
        It sends the messages to the carrier 
        It returns the result - True or False - based on the response
        of the carrier send 
        """
        result = False
        carrier_name = address.get("carrier", None)
        if carrier_name:
            #Get handler init 
            carrier_dict = self.carrier.get(handler_name, {})
            carrier_object = handler_dict.get("object", None)
            if carrier_object:
                try:
                    #Run the function on it
                    carrier_function = getattr(carrier_object, "send")
                    result = messages = carrier_function(message_type, messages, address_names)
                except Exception as e:
                    logging.error(f"Could not send with carrier message of type {message_type}", exc_info=True)
        #Return the result 
        return result

    def check_send_on_message(self, message_type, msg_ids):
        pass 

    def route_messages(self, message_type, messages, address_name):
        """
        Takes in the message type, single message or list of messages,
        And the name of the address

        Return True or False with result of adding the message
        or sending it. 
        """
        result = False
        #Get the handler and function
        if not isinstance(messages, list):
            messages = [messages]
        message_addresses = self.routing_table.get(message_type, {})
        address = message_addresses.get(address_name, {})
        messages = self.run_messages_through_handler(message_type, messages, address)
        address_action = address.get("send_or_receive", None)
        #If it's a receive action -- send the messages, and then
        #Somehow check if you need to send immediately 
        if address_action == "receive":
            for message in messages:
                msg_ids = []
                sub_result = self.add_message(message_type, message)
                if sub_result != False:
                    msg_ids.append(sub_result)
            if len(msg_ids) >= 1:
                #We were able to add at least one message 
                result = True
                #Then - we need to check any immediate addresses 
                #Of this message type 
                self.check_send_on_message(message_type, msg_ids)
        elif address_action == "send":
            result = self.send_messages_through_carrier(self, message_type, messages, address)
        return result
    

    ################# System Table Object for messages ################
    def create_message_table(self):
        """
        Creates the table entries for all the messages in use by the system
        Including the latest entry setter, the semaphore, and the contents
        """
        main_dict = {}
        for message_type in self.messages.keys():
            main_dict[message_type] = self.create_message_dict_entry()
        #Create the message entry dictionary 
        self.message_entries = main_dict

    def print_message_entries_dict(self, message_types="all"):
        """
        Prints all messages entries. Passing in one or a list
        of message types restrics the entries to just those types 
        """
        if message_types == "all":
            print_dict = self.message_entries
        elif isinstances(message_types, list):
            print_dict = {} 
            for sub_type in message_types:
                print_dict[sub_type] = self.message_entries.get(sub_type, {})
        else:
            print_dict = {
                sub_type: self.message_entries[sub_type]
            }
        print("Message Table Entries")
        for message_type in print_dict.keys():
            print(message_type)
            print(json.dumps(print_dict[message_type].get("messages", {})))

    def create_message_dict_entry(self):
        """
        Creates and returns a default dictionary for system
        messages, with a key for the message_type latest entry id,
        the message semaphore, and the actual messages dictionary
        """
        message_dict_entry = {
            "latest_entry_id": 0,
            "semaphore": threading.Semaphore(),
            "messages": {}
        }
        return message_dict_entry.copy() 
    
    def get_all_messages_of_type(self, message_type, list_form=True):
        """
        Takes in a message type and returns all message envelopes 
        of that type currently in the table 
        It list form is set to False, it will return this in the form
        of id: contents instead of a list of messages 
        This semaphore protects the messages and returns copies 
        of them only. 
        """
        send = {}
        #Get the semaphpore
        message_holder = self.message_entries.get(message_type, {})
        if message_holder != {}:
            self.get_message_semaphore(message_type)
            send = message_holder.get(messages, {}).copy()
            self.release_message_semaphore(message_type)   
        else:
            logging.debug(f"{message_type} not recognized by the system on get message") 
        if list_form: 
            send_list = []
            for key, item_val in send.items():
                send_list.append(item_val)
            send = send_list
        return send

    def get_message_semaphore(self, message_type):
        """
        Takes in a message type. Acquires the message semaphore, if 
        it exists
        """
        message_holder = self.message_entries.get(message_type, {})
        if message_holder != {}:
            message_semaphore = message_holder.get("semaphore", None)
            if message_semaphore != None:
                message_semaphore.acquire()

    def release_message_semaphore(self, message_type):
        """
        Takes in a message type. Releases the message semaphore,
        if it exists 
        """
        message_holder = self.message_entries.get(message_type, {})
        if message_holder != {}:
            message_semaphore = message_holder.get("semaphore", None)
            if message_semaphore != None:
                message_semaphore.release()

    def get_latest_message_entry(self, message_type):
        """Get the latest message entry for a given
        message type 
        """
        latest = None
        self.get_message_semaphore(message_type)
        message_handler = self.message_entries.get(message_type, {})
        latest = message_handler.get("latest_entry_id", None)
        self.release_message_semaphore(message_type)

        return latest 
                    
    #TODO: Probably need a try/except clause here 
    def add_message(self, message_type, message):
        """
        Takes in a message (after being enveloped) and 
        message type and adds a message to the message table in state. 
        Triggers a function if that handler is set 
        TODO: (Need to figure impact performance time of this)
        """
        result = False
        #Get the semaphore based on the message type
        message_holder = self.message_entries.get(message_type, {})
        if message_holder != {}:
            #Give the message an entry id
            self.get_message_semaphore(message_type)
            latest_entry = message_holder.get("latest_entry_id", 0)
            latest_entry += 1
            #Don't necessarily have to do this - in interest
            #of keeping numbers small and readable 
            if latest_entry > 9999:
                latest_entry = 0
            message["entry_id"] = latest_entry
            msg_id = message.get("msg_id", None)
            #Insert the new message at the message id, or the 
            #'default' message id 
            if msg_id:
                message_holder["messages"][msg_id] = message
            else:
                message_holder["messages"]["default"] = message
            #Update the latest entry id 
            message_holder["latest_entry_id"] = latest_entry
            #Release the semaphore
            #Might also send before release here. 
            self.release_message_semaphore(message_type)
            result = msg_id
        else:
            logging.debug(f"{message_type} not recognized by system on add message")
        
        #This is where we'll need to trigger any mapped functionality?!
        #(i.e. message sending!)
        #TODO: CHANGE ??? 
        return result
    
    ######## Objects #############
    def get_message_configs_from_addresses(self, addresses):
        """
        Take in a list of address names,
        {"name_of_address": address_config}
        Return a dictionary of message configurations
        {"name of message": message_config}
        """
        return_dict = {}
        for address in addresses:
            address_dict = self.addresses.get(address, {})
            address_message = address_dict.get("message_type", None)
            if address_message:
                message_dict = self.messages.get(address_message, {})
                message_config = message_dict.get("content", {})
            else:
                message_config = {}
            return_dict[address_message] = message_config
        return return_dict 

    def get_send_and_receive_addresses(self, addresses):
        """
        Take in a list of addresses 
        Return two dictionaries - send addresses and receive addresses
        """
        send_addresses = {}
        receive_addresses = {}
        for address_name in addresses: 
            sub_address = self.addresses.get(address_name, {})
            address_type = sub_address.get("send_or_receive", None)
            if address_type == "send":
                send_addresses[address_name] = sub_address.copy()
            elif address_type == "receive":
                receive_addresses[address_name] = sub_address.copy()
        return send_addresses, receive_addresses 

    def get_object(self, path_name, module_name, return_function="return_object"):
        item = None          
        import_string = f"{path_name}.{module_name}"
        item = getattr(importlib.import_module(import_string, package=None), return_function)
        #item = getattr(item, return_function)
        return item 

    def init_handler(self, handler_name):
        """
        Takes in the name of the handler.
        Intializes the handler and starts it...? 
        Actually not sure about that  
        TODO: COME BACK TO THIS
        """
        #Get the config for the handler
        handler_dict = self.handlers.get(handler_name, {})
        handler_config = handler_dict.get("content", {})
        print("Config")
        print(handler_config)
        handler_addresses = handler_dict.get("addresses", [])
        #Get the send and recieve addresses for the handler: 
        send_addresses, receive_addresses = self.get_send_and_receive_addresses(handler_addresses)
        print("Send and Receive Addresses")
        print(json.dumps(send_addresses))
        print(json.dumps(receive_addresses))
        #Get the message configurations 
        message_configs = self.get_message_configs_from_addresses(handler_addresses)
        print("Message configs")
        print(json.dumps(message_configs))
        #This is where we need to get the init info for the actual driver 
        handler_path = "src.handlers"
        handler_wrapper = self.get_object(handler_path, handler_name, return_function="return_object")
        handler_item = handler_wrapper(config=handler_config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)
        handler_dict["object"] = handler_item
        print(handler_dict)


    # def create_object_dict(self):
    #     #carriers, handlers, and (eventually) tasks 
    #     # {
    #     #     "carriers": 
    #     #         {
    #     #             "object_handle"
    #     #             "addresses":
    #     #             "messages?"
    #     #         }
    #     # }
    #     pass 




def return_object(system_config=None):
    """
    Returns an instance of the system object 
    """
    return System(system_config)


if __name__=="__main__":
    system = return_object()
    system.print_configs(["addresses", "messages", "carriers", "handlers"])
    system.print_message_entries_dict()
    