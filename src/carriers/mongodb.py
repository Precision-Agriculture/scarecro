import sys 
import pymongo
import logging 
import json
import copy 
sys.path.append("../scarecro")
import system_object
import util.util as util 

class Mongodb():
    """
    MongoDB Database subclass
    Driver for mongo 
    """
    def __init__(self, config, send_addresses, receive_addresses, message_configs):
        """
        Uses configuration to set itself up.
        Needs: 
            connection_url
            version
            database_name
        """
        #For mongo, need to know if gateway or middle agent
        #Because gateways use slightly outdated version. 
        self.config = config.copy()
        self.send_addresses = send_addresses.copy()
        self.receive_addresses = receive_addresses.copy()
        self.message_configs = message_configs.copy()
        
        self.connection_url = self.config.get("connection_url", "127.0.0.1:27017")
        self.database_name = self.config.get("database_name", None)
        self.version = self.config.get("version", 4.0)
        if self.version >= 4.0:
            self.new_driver = True
        else:
            self.new_driver = False
        self.persistent_connection = self.config.get("persistent_connection", True)
        self.retain_days = self.config.get("retain_days", False)
        self.connected = False
        self.sent_entries = {}
        self.map_collections()
        if self.persistent_connection:
            self.connect()
        logging.info("Initialized MongoDB Carrier")

    def map_collections(self):
        """
        Get information from the send and receive addresses 
        To map databases to addresses and vice versa
        """
        self.all_addresses = {**self.send_addresses, **self.receive_addresses}
        collection_address_mapping = {}
        address_collection_mapping = {}
        collection_message_mapping = {}
        message_collection_mapping = {}
        for address_name, address_config in self.all_addresses.items():
            db_config = address_config.get("additional_info", {})
            message_type = address_config.get("message_type", {})
            collection = db_config.get("collection", None)
            collection_address_mapping[collection] = address_name
            address_collection_mapping[address_name] = collection
            collection_message_mapping[collection] = message_type
            #Might be more than one
            collection_list = message_collection_mapping.get(message_type, [])
            collection_list.append(collection)
            message_collection_mapping[message_type] = collection_list
        self.collection_address_mapping = collection_address_mapping
        self.address_collection_mapping = address_collection_mapping
        self.message_collection_mapping = message_collection_mapping
        self.collection_message_mapping = collection_message_mapping

    def connect(self):
        """
        Takes no arguments 
        connects to the database 
        """
        self.connected_name = self.database_name 
        return_val = False
        try:
            self.client = pymongo.MongoClient(self.connection_url)
            self.connected = True
            return_val = True
        except Exception as e:
            logging.error(f"Could not connect to mongo with this database {self.connected_name}", exc_info=True)
        return return_val

    def disconnect(self):
        """
        Takes no arguments 
        Disconnects from the database 
        """
        return_val = False
        try:
            self.client.close()
            self.connected = False
            return_val = True
        except Exception as e:
            logging.error(f"Could not disconnect database", exc_info=True)
        logging.info("Mongodb disconnected")
        return return_val

    def reconnect(self):
        """
        Reconnects to the database, if operation
        different from connect/disconnect
        """
        return_val = False
        try:
            logging.error("Attempting to reconnect.")
            succ = self.connect()
            if succ:
                self.connected = True
            else:
                self.connected = False
            logging.error(f"Connected to database? {succ}")
            return_val= succ
        except Exception as e:
            logging.error("Reconnect error", exc_info=True)
            return_val =  False 
        return return_val

    def get_collection(self, db_collection):
        return_val = False
        try:
            db_name = self.connected_name
            collection = getattr(getattr(self.client, db_name), db_collection)
            return_val = collection
        except Exception as e:
            self.reconnect()
            logging.error("Could not get this collection", exc_info=True)
        return return_val
    
    def convert_time_stamp(self, records, data_source_name):
        try:
            message_name = self.collection_message_mapping.get(data_source_name, None)
            message_dict = self.message_configs.get(message_name, {})
            time_field = message_dict.get("time_field", "time")
            for record in records:
                prev_time_string = record[time_field]
                record[time_field] = util.convert_string_to_datetime(prev_time_string)
        except Exception as e:
            logging.error(f"Could not convert timestamp to python datetime {data_source_name}", exc_info=True)
        return records 

    def insert_records(self, records, data_source_name):
        """
        Takes a list of records, and the data collection 
        Insert a record or list of records into the database.
        Might need to indicate any mapping's here before insert. 
        """
        collection = self.get_collection(data_source_name) 

        #Handle the time field conversion here - datetime is converted to BSON
        records = self.convert_time_stamp(records, data_source_name)
        #End time field conversion 

        return_val = True
        try:
            if not self.new_driver:
                collection.insert(records)
            else:
                if isinstance(records, list):
                    collection.insert_many(records)
                else:
                    collection.insert_one(records)
            return_val =  True
        except Exception as e:
            logging.error(f"Unable to insert to collection {data_source_name}", exc_info=True)
            self.reconnect()    
            return_val = False
        return return_val

    def get_record(self, data_source_name, record_id, record_id_field):
        """
        Get a 1 particular record - will probably keep this 
        """
        return_val = []
        collection = self.get_collection(data_source_name)
        try:
            query = {str(record_id_field): record_id}
            results = list(collection.find(query))
            if results != []:
                return_val = results[0]
        except Exception as e:
            self.reconnect()
            logging.error(f'Could not get local record', exc_info=True)
            return return_val

    ###### ---------------------Recovery Stuff-----------------------------#######
    def get_all_records_in_time_range(self, min_time, max_time, message_type, collection_name):
        """
        Gets all the records in a given time range.
        This returns a list of records for a given collection in 
        the time range. It uses the message type to determine 
        the time field. 
        """
        #Get the message time field
        message_config = self.message_configs.get(message_type, {})
        time_field = message_config.get("time_field", "time")
        collection = self.get_collection(collection_name)
        #Pull the bulk data 
        return_list = []
        query = {}
        query[time_field] = {"$gte": min_time, "$lte": max_time}
        try:
            return_list = list(collection.find(query, {"_id": False}).sort(time_field, 1))
            if return_list == []:
                logging.debug(f'No entries for this time frame for collection {collection_name}')
            else:
                #Add the recovery value to a new source field
                for item in return_list:
                    item["source"] = "recovery"
        except Exception as e:
            self.reconnect()
            logging.error(f'Issue with getting records in time range', exc_info=True)
        return return_list

    def get_message_type_from_collection(self, collection_name): 
        """
        Take in a collection name and get a mapped message
        type back 
        """
        address_name = self.collection_address_mapping.get(collection_name, None)
        address_config = self.all_addresses.get(address_name, {})
        message_type = address_config.get("message_type", None)
        return message_type 

    def post_recovery_data_message(self, msg_content, recovery_data):
        """
        Post the recovery data message from Mongo driver
        """
        try:
            message = msg_content.copy()
            message_type = "recovery_data"
            message["id"] = system_object.system.return_system_id()
            message["entity"] = "mongodb"
            message["time"] = util.get_today_date_time_utc()
            message["recovery_data"] = recovery_data.copy()
            enveloped_message = system_object.system.envelope_message_by_type(message, message_type)
            system_object.system.post_messages_by_type(enveloped_message, message_type)
        except Exception as e:
            logging.error(f"Could not post recovery data message from mongodb; {e}", exc_info=True)
    
    def fetch_recovery_data(self, message_type=None, entry_ids=[]):
        """      
        This function receives the message type given by the
        on_message trigger as well as the entry id of the 
        message. This function picks up the appropriate message 
        It then posts a fetched recovery data message to the system
        NOTE: This function is a little bit ugly and could possibly
        be improved in the future 
        """
        try:
            recovery_data = {} 
            messages = system_object.system.pickup_messages_by_message_type(message_type=message_type, entry_ids=entry_ids)
            for single_message in messages:
                #For each message, get the lost and restored connection time
                msg_content = single_message.get("msg_content", {})
                lost_connection_time = msg_content.get("lost_connection_time", False)
                restored_connection_time = msg_content.get("restored_connection_time", False)
                #Get the data from the database 
                all_collections = list(self.collection_address_mapping.keys())
                for single_collection in all_collections:
                    try:
                        #Get the recovery data 
                        message_type = self.collection_message_mapping[single_collection]
                        entries = self.get_all_records_in_time_range(lost_connection_time, restored_connection_time, message_type, single_collection)
                        #If the recovery data ain't empty, add it 
                        if entries != []:
                            recovery_data[message_type] = entries
                    except Exception as e:
                        logging.error(f"Could not get recovery entries for {single_collection}; {e}", exc_info=True)
                #If we actually have some recovery data 
                if recovery_data != {}:
                    self.post_recovery_data_message(msg_content, recovery_data)
        except Exception as e:
            logging.error(f"MongoDB could not fetch recovery data {e};", exc_info=True)

    def eliminate_against_main(self, entries, main_db_entries, min_date_main_db, max_date_main_db, time_field, id_field, accept_rate):
        """
        This function eliminates duplicate entries between the 
        recovery data and main database 
        """
        try:
            exclude_entries = []
            for entry in entries:
                curr_time = entry[time_field]
                #If the main DB pulls are outside the range for this entry:
                min_main_time_plus_accept_rate = util.add_to_time(min_date_main_db, -accept_rate)
                max_main_time_plus_accept_rate = util.add_to_time(max_date_main_db, accept_rate)
                if curr_time < min_main_time_plus_accept_rate or curr_time > max_main_time_plus_accept_rate:
                    #Then it's not a duplicate; keep going 
                    continue
                lower_limit = util.add_to_time(curr_time, -accept_rate)
                upper_limit = util.add_to_time(curr_time, accept_rate)
                for main_entry in main_db_entries:
                    #If they have the same ID
                    if main_entry[id_field] == entry[id_field]:
                        #And if the time is within the range - then this entry is a duplicate 
                        if (main_entry[time_field] > lower_limit and main_entry[time_field] < upper_limit):
                            #duplicate - pop it off
                            logging.debug(f"Duplicate: Popping off entry: {entry}")
                            exclude_entries.append(entry)
                            break
            new_entries = [x for x in entries if x not in exclude_entries]
            logging.debug(f"Removed {len(exclude_entries)} entries")
        except Exception as e:
            logging.debug(f"Error in filtering process: {e}", exc_info=True)
        return new_entries


    def eliminate_duplicates(self, lost_connection_time, restored_connection_time, collection_name, message_type, entry_list):
        """ 
        If a given address is configured with an acceptance rate,
        This function will eliminate duplicates against the database.
        If will return only the new messages to accept 
        """
        return_list = entry_list
        try:
            #See if the 
            relevant_address = self.collection_address_mapping[collection_name]
            address_config = self.send_addresses[relevant_address]
            add_info = address_config.get("additional_info", {})
            duration = add_info.get("eliminate_duplicates", None)
            #If there is a collection rate 
            if not isinstance(duration, (int, float)):
                logging.debug(f"No need to eliminate duplicates for {message_type}")
            else:
                try:
                    #Get the entries
                    message_config = self.message_configs.get(message_type, {})
                    time_field = message_config.get("time_field", "time")
                    id_field = message_config.get("id_field", "id")
                    first_entry_time = entry_list[0].get(time_field, lost_connection_time)
                    last_entry_time = entry_list[-1].get(time_field, restored_connection_time)
                    start_pull = util.add_to_time(first_entry_time, -duration)
                    end_pull = util.add_to_time(last_entry_time, duration)
                    new_entries = self.get_all_records_in_time_range(start_pull, end_pull, message_type, collection_name) 
                except Exception as e:
                    logging.debug(f"Couldn't get main database entries for filtering: {e}", exc_info=True)
                try:
                    #Filter them against the main database 
                    filtered_entries = self.eliminate_against_main(entry_list, new_entries, start_pull, end_pull, time_field, id_field, duration)
                    return_list = filtered_entries
                except Exception as e:
                    logging.debug(f"Couldn't filter database and recovery messages for reason {e}", exc_info=True)
        except Exception as e:
            logging.debug(f"Couldn't eliminate duplicate messages for reason {e}", exc_info=True)
        return return_list 


    def handle_recovery_data_message(self, message_type=None, entry_ids=[]):
        """      
        This function receives the message type given by the
        on_message trigger as well as the entry id of the 
        message. This function picks up the appropriate message 
        It then adds the recovery data it needs as appropriate 
        After checking for duplicates
        This function is a tad ugly - prime for refactoring 
        """
        try:
            messages = system_object.system.pickup_messages_by_message_type(message_type=message_type, entry_ids=entry_ids)
            for single_message in messages:
                #For each message, get the lost and restored connection time
                msg_content = single_message.get("msg_content", {})
                lost_connection_time = msg_content.get("lost_connection_time", False)
                restored_connection_time = msg_content.get("restored_connection_time", False)
                recovery_data = msg_content.get("recovery_data", {})
                #For each message type and list of entries we recovered
                for message_type, entry_list in recovery_data.items():
                    try:
                        #Get the collection mapped from the message_type
                        relevant_collections = self.message_collection_mapping.get(message_type, [])
                        logging.debug(f"Going to recover data for collections {relevant_collections}")
                        for collection_name in relevant_collections:
                            #Possibly eliminate duplicates from the message?
                            #CHANGE is here - MARKED 
                            try:
                                new_entry_list = self.eliminate_duplicates(lost_connection_time, restored_connection_time, collection_name, message_type, entry_list)
                                entry_list = new_entry_list
                            except Exception as e:
                                logging.debug(f"Error eliminating duplicates: {e}", exc_info=True)
                                #Insert the new records to the right collection 
                            if entry_list != []:       
                                self.insert_records(copy.deepcopy(entry_list), collection_name)
                    except Exception as e:
                        logging.error(f"Could not insert recovery data for {message_type}; {e}", exc_info=True)
        except Exception as e:
            logging.error(f"Could not handle recovery data message in mongo; {e}", exc_info=True)

    ######### -------------------- Updater Stuff -------------------------------- ####### 
    def get_configuration(self, config_folder, config_name, config_id): 
        """
        Get the stored configuration based on it's config_folder
        And configuration ID 
        """
        #Might want to make this configured 
        returned_config = {} 
        collection_name = "configurations"
        collection = self.get_collection(collection_name)
        #Pull the bulk data 
        query = {"config_id": config_id, "config_folder": config_folder}
        try:
            configuration = list(collection.find(query, {"_id": False}).limit(1))
            if configuration == []:
                logging.debug(f"No configuration found")
            else:
                returned_config = configuration[0].get("config_content", {})
        except Exception as e:
            self.reconnect()
            logging.error(f'Issue with getting config {config_id} {config_folder}; {e}', exc_info=True)
        return returned_config
            
    def fetch_configurations(self, message_type=None, entry_ids=[]):
        """      
        This function receives the message type given by the
        on_message trigger as well as the entry id of the 
        message. This function picks up the appropriate message 
        It then posts a fetched configuration message to the system
        """
        messages = system_object.system.pickup_messages_by_message_type(message_type=message_type, entry_ids=entry_ids)
        for single_message in messages:
            try:
                #Get the content
                single_message_content = single_message.get("msg_content", {})
                #Get the relevant keys
                config_folder = single_message_content.get("config_folder", None)
                config_name = single_message_content.get("config_name", None)
                config_id = single_message_content.get("config_id", None)
                #Query for the config
                config = self.get_configuration(config_folder, config_name, config_id)
                #Create the new message by adding the config 
                logging.debug(f"Configuration Fetched: {config}")
                if config != {}:
                    fetched_message = single_message_content.copy()
                    fetched_message["config_content"] = config
                    fetched_message["id"] = system_object.system.return_system_id()
                    #Envelope and Post It 
                    enveloped_message = system_object.system.envelope_message_by_type(fetched_message, "fetched_config")
                    system_object.system.post_messages_by_type(enveloped_message, "fetched_config")
            except Exception as e:
                logging.error(f"Could not fetch new configuration for {single_message}; {e}", exc_info=True)
    
    #################### Tasks Code for Utility #####################################
    def clean_database(self):
        """
        This function deletes all records a configued
        number of days old.
        I am not in love with the complexity of this function  
        """
        logging.debug("Database clean task")
        #We will limit this to send addresses 
        if self.retain_days:
            logging.debug("Database configured to be cleaned")
            try:
                #Get all the collections from the address 
                curr_time = util.get_today_date_time_utc()
                #Get the subtract seconds - 86400 is number of seconds in a day
                subtract_seconds = -86400*self.retain_days
                #Delete all records before this datetime 
                limit_time = util.add_to_time(curr_time, subtract_seconds)
                #Get all the send addresses and attempt to clean 
                for address_name in self.send_addresses.keys():
                    collection_to_clean = self.address_collection_mapping.get(address_name, False)
                    if collection_to_clean:
                        msg_type = self.collection_message_mapping.get(collection_to_clean, None)
                        if msg_type:
                            #Get the time field
                            time_field = self.message_configs.get("time_field", "time")
                            query = {time_field: {"$lt": limit_time}}
                            collection = self.get_collection(collection_to_clean) 
                            try:
                                if self.new_driver:
                                    collection.delete_many(query)
                                else:
                                    collection.remove(query)
                                logging.debug("Successfully cleaned database")
                            except Exception as e:
                                self.reconnect()
                                logging.error(f"Could not delete query from database {collection_to_clean}", exc_info=True)
            except Exception as e:
                logging.error(f"Could not clean database for reason {e}", exc_info=True)
            

    # Receive and Send Functions 
    def receive(self, address_names, duration):
        """
        Takes in the address names and the duration
        """
        pass 
        
        #Receive not defined for this driver 

    def send(self, address_names, duration, entry_ids=[]):
        """
        Takes in address_names, the duration, and optionally
        a list of entry ids. 
        Grabs the appropriate messages and sends them if not 
        already sent. 
        """
        #Connect if not a persistent connection 
        if not self.persistent_connection:
            self.connect()
        #Pickup the messages
        for address_name in address_names:
            #Get the collection name
            collection_name = self.address_collection_mapping.get(address_name, None)
            messages = system_object.system.pickup_messages(address_name, entry_ids=entry_ids)
            #Insert them into the database if they aren't already
            content_send_list = []
            sent_entries = self.sent_entries.get(collection_name, [])
            new_entry_ids = []
            for message in messages:
                entry_id = message.get("entry_id", None)
                new_entry_ids.append(entry_id)
                #Send only if we haven't already sent it
                if entry_id not in sent_entries:
                    content = message.get("msg_content", {})
                    if content:
                        content_send_list.append(copy.deepcopy(content))
            self.sent_entries[collection_name] = new_entry_ids
            #If we indeed have new messages, send 'em 
            if content_send_list != []:
                succ = self.insert_records(content_send_list, collection_name)
                logging.debug(f"Inserted records for {address_name} into database")
                if not succ:
                    logging.error(f"Could not send messages on address {address_name} for collection {collection_name}", exc_info=True)
        #Disconnect if not a persistent connection 
        if not self.persistent_connection:
            self.disconnect() 
    

def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return Mongodb(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)

         