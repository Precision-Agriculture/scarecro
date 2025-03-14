import sys
import importlib 
import json 
import logging 
import threading 
import copy 
from apscheduler.schedulers.background import BackgroundScheduler
import apscheduler.events
sys.path.append("../scarecro")
import util.util as util 

if logging.root.level > logging.DEBUG:
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
else:
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)

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
        #Variables 
        self.system_updated = False
        #Need to check this on permanent store? 
        self.system_lost_connection = False
        self.system_config = {}
        #Get the system config 
        if system_config:
            logging.debug(f"Using system configuration passed in")
            self.system_config = system_config.copy()
        else:
            logging.debug(f"Using the system configuration in the configurations folder")
            self.system_config = self.import_config("system", "system")
        #Get the post office info - addresses, carriers, 
        #handlers, and messages 
        self.system_id = self.system_config.get("id", "default")


    def init_ecosystem(self):
        self.init_post_office_configs() 
        #Create the system message table 
        self.create_message_table()
        #Init the handlers 
        for handler_name in self.handlers:
            self.init_handler(handler_name)
        #Init the carriers
        for carrier_name in self.carriers:
            self.init_carrier(carrier_name)
        #Init the tasks - tasks are last because they may use
        #handlers or carriers that already exist 
        for task_name in self.tasks:
            self.init_task(task_name)
        #Handle the updater 
        updater = self.system_config.get("updater", None)
        if updater:
            updater_config = self.import_config("updater", updater)
            self.updater = updater_config
        else:
            self.updater = {}
        #Init the scheduler 
        self.init_scheduler()
        #If debug, do some prints
        if logging.root.level <= logging.DEBUG: 
            logging.debug("System Configurations")
            self.print_configs(["addresses", "messages", "carriers", "handlers", "tasks"])
            self.print_scheduler_dict()
            self.print_on_message_routing_dict()

        
    def return_system_updated(self):
        return self.system_updated

    def return_system_lost_connection(self):
        return self.system_lost_connection
    
    def set_system_updated(self, value):
        """
        Pass in True or False to set the system
        updated value 
        """
        self.system_updated = value 

    def set_system_lost_connection(self, value):
        """
        Pass in True or False to set the system 
        lost connection value 
        """
        self.system_lost_connection = value 


    def return_system_id(self):
        return self.system_id

    def return_system_updater(self):
        return self.updater.copy()

    def set_system_updater(self, new_updater):
        self.updater = new_updater.copy()

    def start_system(self):
        """
        This function begins the scheduler
        This is a separate function to allow all initializations
        to execute in the proper order
        """
        logging.debug("Beginning scheduler")
        self.start_scheduler()
        if logging.root.level <= logging.DEBUG: 
            self.print_scheduled_jobs()
        
    def init_post_office_configs(self):
        """
        Takes no arguments but uses the system config class variable
        to initialize post office objects - addresses, carriers, and 
        handler configs. It does not create the objects from the configs. 
        """
        #Puts active messages in system class variable, or an empty list if
        #that keyword isn't present 
        #Systen storage objects 
        self.addresses = {}
        self.messages = {}
        self.handlers = {}
        self.carriers = {}
        self.tasks = {}
        #Get addresses
        active_addresses = self.system_config.get("addresses", [])
        #Get tasks
        active_tasks = self.system_config.get("tasks", [])
        #import addresses - configs, message breakup, inheritance and substitution 
        self.import_addresses(active_addresses)
        #Import tasks as well 
        #Get task configs 
        for task in active_tasks:
            task_content = self.import_config("tasks", task)
            self.tasks[task] = task_content


        #Get message configs
        self.messages = self.map_addresses(self.messages, self.addresses, "message_type")
        self.messages = self.map_tasks(self.messages, self.tasks, "message_type")
        for message in self.messages.keys():
            self.messages[message]["content"] = self.import_config("messages", message)
        #Get handler configs
        self.handlers = self.map_addresses(self.handlers, self.addresses, "handler")
        self.handlers = self.map_tasks(self.handlers, self.tasks, "handler")
        for handler in self.handlers.keys():
            self.handlers[handler]["content"] = self.import_config("handlers", handler)
        #Get carrier configs 
        self.carriers = self.map_addresses(self.carriers, self.addresses, "carrier")
        self.carriers = self.map_tasks(self.carriers, self.tasks, "carrier")
        for carrier in self.carriers.keys():
            self.carriers[carrier]["content"] = self.import_config("carriers", carrier)
        
        #Change is here!!! 
        # #Get task configs 
        # for task in active_tasks:
        #     task_content = self.import_config("tasks", task)
        #     self.tasks[task] = task_content

    #Scheduler exception listener - SDL originally 
    def ap_my_listener(self, event):
        """
        Event exception listener 
        """
        if event.exception:
            print(event.exception)
            print(event.traceback)
            print(event.job_id)
            print(event)
            sys.stdout.flush()

    def create_scheduler(self):
        """
        Creates the scheduler to be used for the system 
        """
        #Create a scheduler 
        thread_config = {'apscheduler.executors.default': {'class': 'apscheduler.executors.pool:ThreadPoolExecutor', 'max_workers': '50'}}
        self.scheduler = BackgroundScheduler(thread_config)
        #for debugging
        self.scheduler.add_listener(self.ap_my_listener, apscheduler.events.EVENT_JOB_ERROR)
        logging.debug("Scheduler created")

    #Substitution dictionary for init'ing configs 
    def make_sub_dict(self, content, name):
        """
        Make the substitution dictionary for a configuration
        Based on the configuration's name and content
        Returns: dictionary of substitution mappings 
        """
        sub_dict = {
            "$name": name,
            "$msg_type": content.get("message_type", None),
            "$system_id": self.system_config.get("id", "default")
        }
        return sub_dict

    def return_sub_keywords(self):
        """
        Returns a list of authorized substitution 
        keywords for the system 
        """
        sub_keywords = ["$name", "$msg_type", "$system_id"]
        return sub_keywords.copy()

    #Also going to recursively call this 
    def substitution_content(self, name, content, sub_dict=None):
        """
        Take in the configuration name and content (and optionally)
        a higher level substitution dict and perform the substitution
        on the configuration content. 
        Returns: content with substition performed
        """
        #Change is here - previously just had sub dict keys list 
        subs = self.return_sub_keywords()
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


    def inheritance(self, path_name, module_name, content):
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
                sub_content = self.get_import_content(path_name, sub_content_name)
                #Also run inheritance recursively on the subcontent: 
                sub_content = self.inheritance(path_name, sub_content_name, sub_content)
                #Read in the inheritance first 
                sub_content_config = self.deep_update(sub_content_config, sub_content)
            content = self.deep_update(sub_content_config, content)
            content = sub_content_config
        return content 


    #Legacy - when configs were python files 
    # def get_import_content(self, path_name, module_name, attribute="config"):
    #     """
    #     This takes in the path to the the imported, the module name 
    #     inside the folder path, and the attribute name to import
    #     Returns: the content tied to the attribute name in the imported file
    #     """
    #     content = {}
    #     #MARKED - this is where we would change to json! 
    #     try:
    #         import_string = f"{path_name}.{module_name}"
    #         content = getattr(importlib.import_module(import_string, package=None), attribute).copy()
    #     except Exception as e:
    #         logging.error(f"Could not import module {module_name}", exc_info=True) 
    #     return content 

    def get_import_content(self, path_name, module_name, attribute="config"):
        """
        This takes in the path to the the imported, the module name 
        inside the folder path, and the attribute name to import
        Returns: the content tied to the attribute name in the imported file
        """
        content = {}
        try:
            file_name = f"{path_name}/{module_name}.json"
            #Json file read in 
            with open(file_name) as json_config:
                content = json.load(json_config)
                #import_string = f"{path_name}.{module_name}"
                #content = getattr(importlib.import_module(import_string, package=None), attribute).copy()
        except Exception as e:
            logging.error(f"Could not import module {module_name}", exc_info=True) 
        return content 


    #Here, perform inheritance and sensor name substitution  
    def import_config(self, config_folder, module_name, attribute="config"):
        """
        General import function for configs. Takes in the sub-config
        folder, the module name within the folder, and the attribute, 
        and applies the inheritance and substitution operators to the config

        Returns: The config content 
        """
        #path_name = f"configs.{config_folder}"
        path_name = f"configs/{config_folder}"
        #Get the content
        content = self.get_import_content(path_name, module_name, attribute)
        #Run inheritance and substitution on the content 
        content = self.complete_content(path_name, module_name, content)
        return content


    def complete_content(self, path_name, module_name, content):
        """ 
        This function runs just the inheritance and substituion operations
        on a piece of config content 
        Takes in: path name, module name, attribute name, and original config content
        Returns: completed content 
        """
        content = self.inheritance(path_name, module_name, content)
        content = self.substitution_content(module_name, content)
        return content

    def import_addresses(self, active_addresses):
        """
        Specific import for addresses, since multiple message types
        Can throw off an address import 
        """
        #path_name = f"configs.addresses"
        path_name = f"configs/addresses"
        for address_name in active_addresses:
            #Get the content
            content = self.get_import_content(path_name, address_name)
            message_type = content.get("message_type", None)
            #If we have multiple messages in one address, break them all out into separate messages
            #Note that you can't inherit from a an address with multiple messages 
            if isinstance(message_type, list):
                for sub_message_type in message_type:
                    sub_address_name = f"{address_name}_{sub_message_type}"
                    sub_content = copy.deepcopy(content)
                    sub_content["message_type"] = sub_message_type
                    sub_content = self.complete_content(path_name, sub_address_name, sub_content)
                    self.addresses[sub_address_name] = sub_content
            else:
                new_content = self.complete_content(path_name, address_name, content)
                self.addresses[address_name] = new_content


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
            content_key = address_val.get(address_key, None)
            #If that doesn't exist in the content dict, add it
            if content_key != None:
                if content_dict.get(content_key, None) == None:
                    content_dict[content_key] = self.return_default_mapping_dict()
            #Append this address to this content's address fields
                content_dict[content_key]["addresses"].append(address_name)
        return content_dict

    def map_tasks(self, content_dict, tasks, task_key):
        """
        This function takes in a blank dictionary, and maps the tasks
        it takes in that are associated with a specific content type
        (address key provided) 
        Returns: the inputed dictionary, now mapped to addresses in
        it's "addresses" field  
        """
        for task_name, task_config in tasks.items():
            #If we are looking for task carriers or handlers 
            if task_key == "carrier" or task_key == "handler": 
                content_key = task_config.get("source_type", None)
                #Only return if matching, and then return name 
                if content_key != task_key: 
                    content_key = None
                else:
                    content_key = task_config.get("config_name", None)
            else:
                content_key = task_config.get(task_key, None)
            #If the key is in the task config BUT 
            #doesn't exist in the content dict, add it
            if content_key != None:
                if content_dict.get(content_key, None) == None:
                    content_dict[content_key] = self.return_default_mapping_dict()
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

    ########################## Messages ###############################
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
                    logging.debug(f"Ran {message_type} through function {handler_function} of {handler_name}")
                except Exception as e:
                    logging.error(f"Could not process with handler message of type {message_type}", exc_info=True)
        #Return the messages 
        return messages

    def check_message_triggers(self, message_type, entry_ids=[]):
        """
        This checks if this message type triggers any on_message conditions
        If it does, it executes the appropriate function 
        """
        job_ids = self.on_message_routing_dict.get(message_type)
        #If a there is a trigger on this message type
        if job_ids:
            #For every trigger on this message type 
            for job_id in job_ids:
                try:
                    #Get the function parameters and execute the function
                    job_config = self.scheduler_dict.get(job_id, {})
                    arguments = job_config.get("arguments")
                    triggered_object = job_config.get("object", None)
                    triggered_function = job_config.get("function", None)
                    overall_function = getattr(triggered_object, triggered_function)
                    logging.debug(f"Executing {job_id} to {triggered_function} on {message_type} message with arguments {arguments}")
                    if triggered_function == "send":
                        overall_function(arguments, "on_message", entry_ids=entry_ids)
                    elif triggered_function == "receive":
                        overall_function(arguments, "on_message")
                    else:
                        #Like from a task (need to still run entry ids, I think) #MARKED #CHANGE 
                        if arguments == {}:
                            overall_function(entry_ids=entry_ids, message_type=message_type)
                        else:
                            overall_function(arguments, entry_ids=entry_ids, message_type=message_type)
                except Exception as e:
                    logging.error(f"Could not run {job_id} on on_message trigger for {message_type}", exc_info=True)

    def post_messages(self, messages, address_name):
        """
        Takes in a single message or list of messages,
        And the name of the address

        Return True or False with result of adding the message
        or sending it. 
        """
        result = False
        address = self.addresses.get(address_name, {})
        message_type = address.get("message_type", None)
        try:
            #Get the handler and function
            if not isinstance(messages, list):
                messages = [messages]
            #Run the messages through the handler 
            try:
                messages = self.run_messages_through_handler(message_type, messages, address)
            except Exception as e:
                logging.error(f"Could not run {message_type} through handlers", exc_info=True)
            #Add the messages, get the return message ids 
            entry_ids = []
            for message in messages:
                try:
                    sub_result = self.add_message(message_type, message)
                    if sub_result != False:
                        entry_ids.append(sub_result)
                        logging.debug(f"Successfully added {message_type}")
                except Exception as e:
                    logging.error(f"Could not add message of type {message_type}", exc_info=True)
            if len(entry_ids) >= 1:
                #We were able to add at least one message 
                result = True
                logging.debug(f"Checking message triggers")
                try:
                    self.check_message_triggers(message_type, entry_ids=entry_ids)
                except Exception as e:
                    logging.error(f"Could not check message triggers on {message_type}; {e}", exc_info=True)
        except Exception as e:
            logging.error(f"Could not post message on address {address_name}; {e}", exc_info=True)

        if logging.root.level <= logging.DEBUG: 
            self.print_message_entries_dict()
        return result

    def post_messages_by_type(self, messages, message_type):
        """
        Takes in a single message or list of messages,
        And the name of the address

        Return True or False with result of adding the message
        or sending it. 
        """
        result = False
        try:
            #Get the handler and function
            if not isinstance(messages, list):
                messages = [messages]
            #Add the messages, get the return message ids 
            entry_ids = []
            for message in messages:
                try:
                    sub_result = self.add_message(message_type, message)
                    if sub_result != False:
                        entry_ids.append(sub_result)
                        logging.debug(f"Successfully added {message_type}")
                except Exception as e:
                    logging.error(f"Could not add message of type {message_type}", exc_info=True)
            if len(entry_ids) >= 1:
                #We were able to add at least one message 
                result = True
                logging.debug(f"Checking message triggers")
                try:
                    self.check_message_triggers(message_type, entry_ids=entry_ids)
                except Exception as e:
                    logging.error(f"Could not check message triggers on message {message_type}; {e}", exc_info=True)

        except Exception as e:
            logging.error(f"Could not post message of type {message_type}; {e}", exc_info=True)

        if logging.root.level <= logging.DEBUG: 
            self.print_message_entries_dict()
        return result
    
    def filter_messages(self, messages, entry_ids):
        """
        Takes in a list of enveloped messages and a list of message ids
        Returns only the messages with ids in the list 
        """
        send_messages = []
        for message in messages:
            if message.get("entry_id", None) in entry_ids:
                send_messages.append(message)
        return send_messages

    def pickup_messages(self, address_name, entry_ids=[]):
        """
        Takes in an address_name and optionally a list of message_ids
        Returns a list of messages corresponding to the address, and 
        filtered by message ids, potentially. 
        """
        messages = []
        try:
            #First, get the message type from the address
            address = self.addresses.get(address_name, {})
            message_type = address.get("message_type", None)
            #Get the messages from the post office
            messages = self.get_messages(message_type)
            if messages != []:
                try:
                    #Run the messages through the handler 
                    messages = self.run_messages_through_handler(message_type, messages, address)
                except Exception as e:
                    logging.error(f"Could not run {message_type} through handler", exc_info=True)
                #Optionally filter the messages 
                if entry_ids != []:
                    try:
                        messages = self.filter_messages(messages, entry_ids)
                    except Exception as e:
                        logging.error(f"Could not filter {message_type} to entry ids {entry_ids}", exc_info=True)
        except Exception as e:
            logging.error(f"Could not pick up message on address {address}", exc_info=True)
        return messages 

    def pickup_messages_by_message_type(self, message_type=None, entry_ids=[]):
        """
        Takes in an address_name and optionally a list of message_ids
        Returns a list of messages corresponding to the address, and 
        filtered by message ids, potentially. 
        """
        messages = []
        try:
            #Get the messages from the post office
            messages = self.get_messages(message_type)
            if messages != []:
                #Optionally filter the messages 
                if entry_ids != []:
                    try:
                        messages = self.filter_messages(messages, entry_ids)
                    except Exception as e:
                        logging.error(f"Could not filter {message_type} to entry ids {entry_ids}", exc_info=True)
        except Exception as e:
            logging.error(f"Could not pick up message of message_type {message_type}", exc_info=True)
        return messages 


    def envelope_message(self, message_content, address_name):
        """
        Takes in the message content (dict expected) and address name and envelopes the 
        message
        Could really do this on the system object level. 
        """
        #Get message type from address 
        address_config = self.addresses.get(address_name, {})
        message_type = address_config.get("message_type", "default")
        #Get message id field and time from message definition
        message_config = self.messages.get(message_type, {}).get("content")
        id_field = message_config.get("id_field", "id")
        time_field = message_config.get("time_field", "time")
        #Try to put in the message id and time from the message
        message_id = message_content.get(id_field, "default")
        time_value = message_content.get(time_field, None)
        if time_value == None:
            time_value = util.get_today_date_time_utc()
        #Envelope it 
        enveloped_message = {
            "msg_id": message_id,
            "msg_time": time_value,
            "msg_type": message_type,
            "msg_content": message_content
        }
        logging.debug(f"Enveloped message {enveloped_message}")
        return enveloped_message

    def envelope_message_by_type(self, message_content, message_type):
        """
        Takes in the message content (dict expected) and address name and envelopes the 
        message
        Could really do this on the system object level. 
        """
        #Get message id field and time from message definition
        message_config = self.messages.get(message_type, {}).get("content")
        id_field = message_config.get("id_field", "id")
        time_field = message_config.get("time_field", "time")
        #Try to put in the message id and time from the message
        message_id = message_content.get(id_field, "default")
        time_value = message_content.get(time_field, None)
        if time_value == None:
            time_value = util.get_today_date_time_utc()
        #Envelope it 
        enveloped_message = {
            "msg_id": message_id,
            "msg_time": time_value,
            "msg_type": message_type,
            "msg_content": message_content
        }
        logging.debug(f"Enveloped message {enveloped_message}")
        return enveloped_message


    ################# System Table Object for messages ################
    def create_message_table(self):
        """
        Creates the table entries for all the messages in use by the system
        Including the latest entry setter, the semaphore, and the contents
        Message Table looks like:
        {
            message_type: 
            {
                {
                "latest_entry_id": 0,
                "semaphore": threading.Semaphore(),
                "messages": {
                    msg_id: {<enveloped message>}
                    msg_id: {<enveloped message>}
                    }
                }
            }
        }
        
        """
        main_dict = {}
        #For each message type, create a blank message entries dictionary 
        for message_type in self.messages.keys():
            main_dict[message_type] = self.create_message_dict_entry()
        #Create the message entry dictionary 
        self.message_entries = main_dict

    def print_message_entries_dict(self, message_types="all"):
        """
        Prints all messages entries. Passing in one or a list
        of message types restrics the entries to just those types 
        """
        try:
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
            print("---------Message Table Entries--------------")
            for message_type in print_dict.keys():
                print(message_type)
                print(json.dumps(print_dict[message_type].get("messages", {}), indent=4))
        except Exception as e:
            logging.error(f"Could not print message entries dict; {e}", exc_info=True)

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
        try:
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
        except Exception as e:
            logging.error(f"Could not get all messages of type {message_type}, {e}", exc_info=True)
            try:
                self.release_message_semaphore(message_type)
            except Exception as e:
                pass 
        return send

    def get_message_semaphore(self, message_type):
        """
        Takes in a message type. Acquires the message semaphore, if 
        it exists
        """
        try:
            message_holder = self.message_entries.get(message_type, {})
            if message_holder != {}:
                message_semaphore = message_holder.get("semaphore", None)
                if message_semaphore != None:
                    message_semaphore.acquire()
                    logging.debug(f"Message semaphore for {message_type} aquired")
        except Exception as e:
            logging.error(f"Could not get message semaphore for {message_type}")
            try:
                message_semaphore.release()
            except Exception as e:
                pass 

    def release_message_semaphore(self, message_type):
        """
        Takes in a message type. Releases the message semaphore,
        if it exists 
        """
        try:
            message_holder = self.message_entries.get(message_type, {})
            if message_holder != {}:
                message_semaphore = message_holder.get("semaphore", None)
                if message_semaphore != None:
                    message_semaphore.release()
                    logging.debug(f"Message semaphore for {message_type} released")
        except Exception as e:
            logging.error(f"Could not release message semaphore for {message_type}")

    def get_latest_message_entry(self, message_type):
        """Get the latest message entry for a given
        message type 
        """
        latest = None
        try:
            self.get_message_semaphore(message_type)
            message_handler = self.message_entries.get(message_type, {})
            latest = message_handler.get("latest_entry_id", None)
            self.release_message_semaphore(message_type)
        except Exception as e:
            logging.error(f"Could not get latest message entry for {message_type}, {e}", exc_info=True)
            try:
                self.release_message_semaphore(message_type)
            except Exception as e:
                pass 
        return latest 
                    
    def add_message(self, message_type, message):
        """
        Takes in a message (after being enveloped) and 
        message type and adds a message to the message table in state. 
        Returns the msg id of the successfully added message, or False
        """
        result = False
        try:
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
                #Return the entry id 
                result = latest_entry
            else:
                logging.debug(f"{message_type} not recognized by system on add message")
        except Exception as e:
            logging.error(f"Could not add message of {message_type}, {e}", exc_info=True)
            try:
                self.release_message_semaphore(message_type)
            except Exception as e:
                pass 
        return result


    def get_messages(self, message_type):
        """
        Takes in a message type
        Returns all the messages corresponding 
        to the message type in a list 
        """
        return_messages_list = []
        try:
            message_holder = self.message_entries.get(message_type, {})
            if message_holder != {}:
                #Get the semaphore based on the message type
                self.get_message_semaphore(message_type)
                messages_dict = message_holder.get("messages", {})
                for msg_id, enveloped_message in messages_dict.items():
                    return_messages_list.append(enveloped_message.copy())
                #Release the semaphore
                self.release_message_semaphore(message_type)
            else:
                logging.debug(f"No messages found for {message_type} ")
        except Exception as e:
            logging.error(f"Could not get messages of {message_type}, {e}", exc_info=True)
            try:
                self.release_message_semaphore(message_type)
            except Exception as e:
                pass 
        return return_messages_list
    
    ######## Objects #############
    def get_message_configs_from_addresses(self, addresses):
        """
        Take in a list of address names,
        {"name_of_address": address_config}
        Return a dictionary of message configurations
        {"name of message": message_config}
        """
        return_dict = {}
        try:
            for address in addresses:
                address_dict = self.addresses.get(address, {})
                address_message = address_dict.get("message_type", None)
                if address_message:
                    message_dict = self.messages.get(address_message, {})
                    message_config = message_dict.get("content", {})
                else:
                    message_config = {}
                return_dict[address_message] = message_config
        except Exception as e:
            logging.error(f"Could not get messages configs for addresses {addresses}, {e}", exc_info=True)
        return return_dict 

    def get_send_and_receive_addresses(self, addresses):
        """
        Take in a list of addresses 
        Return two dictionaries - send addresses and receive addresses
        Dictionary indexed by address name 
        """
        send_addresses = {}
        receive_addresses = {}
        try:
            for address_name in addresses: 
                sub_address = self.addresses.get(address_name, {})
                address_type = sub_address.get("send_or_receive", None)
                if address_type == "send":
                    send_addresses[address_name] = sub_address.copy()
                elif address_type == "receive":
                    receive_addresses[address_name] = sub_address.copy()
        except Exception as e:
            logging.error(f"Could not get send and receive addresses for addresses {addresses}, {e}", exc_info=True)
        return send_addresses, receive_addresses 

    def get_object(self, path_name, module_name, return_function="return_object"):
        item = None    
        try:      
            import_string = f"{path_name}.{module_name}"
            item = getattr(importlib.import_module(import_string, package=None), return_function)
        except Exception as e:
            logging.error(f"Could not get object {path_name}.{module_name}.{return_function}, {e}", exc_info=True)
        #item = getattr(item, return_function)
        return item 

    def init_handler(self, handler_name):
        """
        Takes in the name of the handler.
        Intializes the handler object and adds it to the 
        "object" field indexed by the handler name 
        in the handlers system dictionary. 
        """
        try:
            #Get the config for the handler
            handler_dict = self.handlers.get(handler_name, {})
            handler_config = handler_dict.get("content", {})
            handler_addresses = handler_dict.get("addresses", [])
            #Get the send and recieve addresses for the handler: 
            send_addresses, receive_addresses = self.get_send_and_receive_addresses(handler_addresses)
            #Get the message configurations 
            message_configs = self.get_message_configs_from_addresses(handler_addresses)
            #This is where we need to get the init info for the actual driver 
            handler_path = "src.handlers"
            source_name = handler_config.get("source", handler_name)
            handler_wrapper = self.get_object(handler_path, source_name, return_function="return_object")
            if handler_wrapper:
                handler_item = handler_wrapper(config=handler_config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)
                handler_dict["object"] = handler_item
                logging.debug(f"Initialized handler {handler_name}")
        except Exception as e:
            logging.error(f"Could not initialize handler {handler_name}, {e}", exc_info=True)

    def init_carrier(self, carrier_name):
        """
        Takes in the name of the carrier.
        Intializes the carrier object and adds it to 
        the "object" field of carrier dictionary 
        """
        try:
            #Get the config for the handler
            carrier_dict = self.carriers.get(carrier_name, {})
            carrier_config = carrier_dict.get("content", {})
            carrier_addresses = carrier_dict.get("addresses", [])
            #Get the send and recieve addresses for the handler: 
            send_addresses, receive_addresses = self.get_send_and_receive_addresses(carrier_addresses)
            #Get the message configurations 
            message_configs = self.get_message_configs_from_addresses(carrier_addresses)
            #This is where we need to get the init info for the actual driver 
            carrier_path = "src.carriers"
            source_name = carrier_config.get("source", carrier_name)

            carrier_wrapper = self.get_object(carrier_path, source_name, return_function="return_object")
            if carrier_wrapper:
                carrier_item = carrier_wrapper(config=carrier_config, send_addresses=send_addresses.copy(), receive_addresses=receive_addresses.copy(), message_configs=message_configs)
                carrier_dict["object"] = carrier_item
                logging.debug(f"Initialized carrier {carrier_name}")
        except Exception as e:
            logging.error(f"Could not initialize carrier {carrier_name}, {e}", exc_info=True)

    def init_task(self, task_name):
        """
        Takes in the name of the task.
        Intializes the task object and adds it to 
        the "object" field of task dictionary 
        """
        try:
            #Get the config for the tasks
            task_dict = self.tasks.get(task_name, {})
            #This is where we need to get the init info for the actual driver 
            #If this task is a source file in the actual tasks folder
            if "source" in list(task_dict.keys()):
                task_path = "src.tasks"
                source_name = task_dict.get("source", task_name)
                task_wrapper = self.get_object(task_path, source_name, return_function="return_object")
                if task_wrapper:
                    task_item = task_wrapper(config=task_dict)
                    task_dict["object"] = task_item
            #Otherwise: 
            else:
                #Get the folder
                task_item = None
                source_type = task_dict.get("source_type", None)
                config_name = task_dict.get("config_name", None)
                if source_type == "carrier":
                    task_item = self.carriers.get(config_name, {}).get("object", None)
                elif source_type == "handler":
                    task_item = self.handlers.get(config_name, {}).get("object", None)
                task_dict["object"] = task_item 
        except Exception as e:
            logging.error(f"Could not intialize task {task_name}, {e}", exc_info=True)
        #Might want to think getting a return value here?

    def init_scheduler(self):
        try:
            logging.debug("Creating scheduler object")
            self.create_scheduler()
            logging.debug("Creating scheduler dictionary")
            self.create_scheduler_dict()
            logging.debug("Scheduling jobs")
            self.schedule_jobs()
        except Exception as e:
            logging.error(f"Issue initializing scheduler {e}", exc_info=True)

    def create_carrier_schedule_dict(self, scheduler_dict, on_message_routing_dict): 
        """
        Takes in the scheduler dict and on_message routing dict and 
        creates a job id for all the carrier functions 
        """
        #First, going to scheduler the carriers 
        for address_name, address_config in self.addresses.items():
            try:
                #Job ID goes - name_function_duration
                duration = address_config.get("duration", "as_needed")
                carrier_name = address_config.get("carrier", None)
                function = address_config.get("send_or_receive", None)
                job_id = f"{carrier_name}_{function}_{duration}"
                #Helps create the on_message triggering dictionary, which is very useful
                if duration == "on_message":
                    job_id = f"{carrier_name}_{function}_{duration}_{address_name}"
                    message_type = address_config.get("message_type", None)
                    job_list = on_message_routing_dict.get(message_type, [])
                    job_list.append(job_id)
                    on_message_routing_dict[message_type] = job_list
                job_dict = scheduler_dict.get(job_id, {})
                #If we don't have a job dictionary at this id:
                if not job_dict:
                    #Get the carrier object handler
                    carrier_object = self.carriers.get(carrier_name, {}).get("object", None)
                    #Create the job dictionary 
                    new_job_dict = {
                        "object_name": carrier_name,
                        "object": carrier_object,
                        "function": function,
                        "arguments": [address_name],
                        "duration": duration,
                        "type": "carrier"
                    }
                    scheduler_dict[job_id] = new_job_dict
                else:
                    #If we do, just append the addresses
                    job_dict["arguments"].append(address_name)
            except Exception as e:
                logging.error(f"Could not create job dict for address {address_name}, {e}", exc_info=True)
        return scheduler_dict, on_message_routing_dict
            

    def create_task_schedule_dict(self, scheduler_dict, on_message_routing_dict):
        """
        Takes in the scheduler dict and on_message routing dict and 
        creates a job id for all the task functions 
        NOTE: Lot of cross-over with carrier. Next refactor should improve this flow. 
        """ 
         #Next, going to schedule the tasks 
        for task_name, task_config in self.tasks.items():
            try:
                #Job ID goes - name_function_duration
                duration = task_config.get("duration", "as_needed") 
                task_object = task_config.get("object", None)
                function = task_config.get("function", None)
                arguments = task_config.get("arguments", None)
                job_id = f"{task_name}_{function}_{duration}"
                #In case we have any tasks triggered by a message, as well 
                #Probaby need to add message_type here as well (entry ids need to be in source)
                if duration == "on_message":
                    message_type = task_config.get("message_type", None)
                    job_id = f"{task_name}_{function}_{duration}_{message_type}"
                    job_list = on_message_routing_dict.get(message_type, [])
                    job_list.append(job_id)
                    on_message_routing_dict[message_type] = job_list
                new_job_dict = {
                        "object_name": task_name,
                        "object": task_object,
                        "function": function,
                        "arguments": arguments,
                        "duration": duration,
                        "type": "task"
                    }
                scheduler_dict[job_id] = new_job_dict
            except Exception as e:
                logging.error(f"Could not create job dict for task {task_name}, {e}", exc_info=True)
        return scheduler_dict, on_message_routing_dict
    #Scheduler functions 
    def create_scheduler_dict(self):
        """
        Creates a dictionary of the form:
        {
            "object_name": name of the configured class object in the system
            "object": Reference to class object that runs the function
            "job_id": Unique id of the job
            "function": function to run
            "arguments": arguments the pass to the function, in a list
            "duration": How often the job should be run in seconds, or "always"
            "type": "task" or "carrier", depending on which it is
        }
        The sub-dictionary above is part of a larger dictionary, indexed 
        by the job_id

        This also creates the on_message trigger dictionary for 
        easier lookup and use by the system 
        {
            message_type: [list_of_job_ids_triggered_by_message]
        }

        """
        scheduler_dict = {}
        on_message_routing_dict = {}
        try:
            scheduler_dict, on_message_routing_dict = self.create_carrier_schedule_dict(scheduler_dict, on_message_routing_dict)
            scheduler_dict, on_message_routing_dict = self.create_task_schedule_dict(scheduler_dict, on_message_routing_dict)
        except Exception as e:
            logging.error("Issue creating scheduler dictionary")
        self.scheduler_dict = scheduler_dict
        self.on_message_routing_dict = on_message_routing_dict

    def schedule_jobs(self):
        """
        Takes in no arguments
        Schedules the jobs from the scheduling dict on the scheduler
        """
        for job_id, job_config in self.scheduler_dict.items():
            try:
                duration = job_config.get("duration", "as_needed")
                job_object = job_config.get("object", None)
                arguments = job_config.get("arguments", [])
                if job_config.get("type", "task") == "carrier":
                   arguments = [arguments, duration]
                #Annoying way to make sure arguments are good to go 
                else:
                    if arguments == {} or arguments == []:
                        arguments = []
                    else:
                        arguments = [arguments]
                function = job_config.get("function", None)
                #If its a seconds interval
                if str(duration).isnumeric():
                    self.scheduler.add_job(getattr(job_object, function), 'interval', args=arguments, id=job_id, seconds=int(duration), jitter=10)
                    logging.debug(f"Scheduled job id {job_id} to run every {duration} seconds")
                #Otherwise, if its an always job 
                elif str(duration) == "always":
                    self.scheduler.add_job(getattr(job_object, function), args=arguments, id=job_id, misfire_grace_time=None)
                    logging.debug(f"Scheduled job id {job_id} to run always")
            except Exception as e:
                logging.error(f"Could not schedule job {job_id}", exc_info=True)

    def start_scheduler(self):
        """
        Start the job scheduler 
        """
        try:
            self.scheduler.start()
            logging.info("Started scheduler")
        except Exception as e:
            logging.error(f"Could not start scheduler, {e}", exc_info=True )

    def print_scheduled_jobs(self):
        """
        Takes no arguments. Prints jobs currently 
        scheduled on scheduler 
        """
        try:
            all_jobs = self.scheduler.get_jobs()
            print("Scheduled Jobs")
            for job in all_jobs:
                print(f"JOB ID: {job.id} | TRIGGER: {job.trigger} | NEXT_RUN: {job.next_run_time} | FUNCTION: {job.func} | ARGS: {job.args}")
        except Exception as e:
            logging.error(f"Could not print all scheduled jobs, {e}", exc_info=True)

    def print_scheduler_dict(self):
        """
        Takes no arguments
        Prints out the scheduler dictionary 
        """
        try:
            print("Scheduler Dictionary")
            print(json.dumps(self.scheduler_dict, indent=4, default=str))
        except Exception as e:
            logging.error(f"Could not print the scheduler dictionary, {e}", exc_info=True)

    def print_on_message_routing_dict(self):
        """
        Takes no arguments
        Prints out the scheduler dictionary 
        """
        try:
            print("On Message Routing Dictionary")
            print(json.dumps(self.on_message_routing_dict, indent=4, default=str))
        except Exception as e:
            logging.error(f"Could not print the on_message routing dictionary, {e}", exc_info=True)

    #End system class definition 

    def disconnect_carriers(self): 
        """
        Takes no arguments but attempts to disconnect
        All carriers available
        """
        for carrier_name, carrier_dict in self.carriers.items():
            #MARKED
            carrier_object = carrier_dict.get("object", None)
            if carrier_object != None:
                #Try to disconnect it
                logging.debug(f"Attempting to disconnect {carrier_name}")
                try:
                    carrier_object.disconnect()
                except Exception as e:
                    logging.error(f"Could not disconnect carrier {carrier_name}: {e}", exc_info=True)


def return_object(system_config=None):
    """
    Returns an instance of the system object 
    """
    return System(system_config)


if __name__=="__main__":
    system = return_object()
    system.print_configs(["addresses", "messages", "carriers", "handlers"])
    system.print_message_entries_dict()
    