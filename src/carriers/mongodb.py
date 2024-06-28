import sys 
import pymongo
import logging 
import json
sys.path.append("../scarecro")
import system_object


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
        
        all_addresses = {**self.send_addresses, **self.receive_addresses}
        collection_address_mapping = {}
        address_collection_mapping = {}
        for address_name, address_config in all_addresses.items():
            db_config = address_config.get("additional_info", {})
            collection = db_config.get("collection", None)
            collection_address_mapping[collection] = address_name
            address_collection_mapping[address_name] = collection
        self.collection_address_mapping = collection_address_mapping
        self.address_collection_mapping = address_collection_mapping

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

    def build_sub_query(self, query_dict):
        try:
            op = query_dict["op"]
            field = query_dict["field"]
            value = query_dict["value"]
            if op == "=" or op == "is":
                query = {field: value}
            if op == ">":
                query = {field: {"$gt": value}}
            if op == "<":
                query = {field: {"$lt": value}}
            if op == ">=":
                query = {field: {"$gte": value}}
            if op == "<=":
                query = {field: {"$lte": value}}
            #Will have to rethink this one
            #if op == "in":
                #query = {field: {"$lte": value}}
        except Exception as e:
            logging.error("Could not build query in query function", exc_info=True)
            query = {}
            field=""
        return query, field 

    def build_query(self, query):
        final_query = {}
        if isinstance(query, list):
            for query_dict in query:
                sub_query, field = self.build_sub_query(query_dict)
                if field in list(final_query.keys()):
                    final_query[field].update(sub_query[field])
                else:
                    final_query[field] = sub_query[field]
        else:
            query_dict = query
            final_query, field = self.build_sub_query(query_dict)
        return final_query
   

    def insert_records(self, records, data_source_name):
        """
        Takes a list of records, and the data collection 
        Insert a record or list of records into the database.
        """
        collection = self.get_collection(data_source_name) 
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
        
    # Right now it only takes one new record, so bear that in mind! 
    def update_record(self, data_source_name, record_id, record_id_field, new_record):
        """
        Update existing record with new information 
        Provide the new record to update the existing record with
        Based on a key 
        """
        return_val = False
        collection = self.get_collection(data_source_name)
        try:
            #compound ID
            if isinstance(record_id_field, list):
                query = {}
                for field, id_val in zip(record_id_field, record_id):
                    query[field] = id_val
            #Non-compound ID
            else:
                query = {record_id_field : record_id}
            if self.device == "gateway":
                results = collection.update(query, new_record, upsert=True)
            else:
                results = collection.replace_one(query, new_record, upsert=True) 
            if self.device != "gateway":
                if results.acknowledged:
                    return_val= True
            else:
                #Bit of an assumption here for gateway, unfortunately. 
                return_val = True
        except Exception as e:
            self.reconnect()
            logging.error(f'Could not update record', exc_info=True)
        return return_val 

    def delete_records(self, query, data_source_name, verbose=False):
        """
        Delete existing records from the database
        """
        collection = self.get_collection(data_source_name) 
        return_val = True
        final_query = self.build_query(query)
        if verbose:
            print(f"Final query {final_query}")
        if final_query != {}:
            try:
                if self.device == "gateway":
                    collection.remove(final_query)
                else:
                    collection.delete_many(final_query)
            except Exception as e:
                self.reconnect()
                logging.error(f"Could not delete query from database collection", exc_info=True)
                return_val = False
        return return_val  

    def check_record_existence(self, record_id, record_id_field, data_source_name):
        """
        Check to see if a given record exists in the database
        """
        return_val = False
        collection = self.get_collection(data_source_name) 
        try:
            results = list(collection.find({record_id_field: record_id}))
            logging.debug(f'Resuts from record pull: {results}')
            if results != []:
                return_val = True
        except Exception as e:
            self.reconnect()
            logging.error(f'Could not find local record', exc_info=True)
        return return_val 

    def get_record(self, data_source_name, record_id, record_id_field):
        """
        Get a 1 particular record
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

    def return_query(self, data_source_name, query):
        return_list = []
        collection = self.get_collection(data_source_name) 
        try:
                results = list(collection.find(query, {"_id": 0}))
                return results
        except Exception as e:
            self.reconnect()
            logging.error(f"Could not execute database query")
            return return_list

    def return_records_matching_query(self, query, data_source_name, verbose=False):
        """
        Query the database and return matching records
        """
        try:
            final_query = self.build_query(query)
            if verbose:
                print(f"Final Query {final_query}")
            if final_query != {}:
                try:
                    results = self.return_query(data_source_name, final_query)
                    return results
                except Exception as e:
                    logging.error(f'Issue executing record query', exc_info=True)
                    return []
        except Exception as e:
            self.reconnect()
            logging.error(f'Could not get records with query {query}', exc_info=True)
        return []


    #This needs to be majorly workshopped.
    #Marked - time with no time format specificed 
    #CHANGE - Please fix this. It makes my heart hurt.  
    def get_all_records_in_time_range(self, min_time, max_time, time_field, ids, id_field, data_source_name):
        """
        Gets all the records in a given time range.
        This returns a dictionary with the entries indexed as "main_entries" (in a list)
        and the minimum and maximum date in the pulled range as "min_date", and "max_date",
        in the likely case that they are different from the provided boundaries
        """
        collection = self.get_collection(data_source_name)
        #Pull the bulk data 
        query = {}
        if ids != [] and id_field != "error":
            query[id_field] = {"$in": ids }
        if time_field != "error":
            query[time_field] = {"$gte": min_time, "$lte": max_time}
        try:
            main_db_entries = list(collection.find(query, {"_id": False}).sort(time_field, 1))
            if main_db_entries == []:
                logging.debug(f'No entries for this time frame')
                return {"main_entries": [], "min_date": "error", "max_date": "error"}
            min_date_main_db = main_db_entries[0][time_field]
            max_date_main_db = main_db_entries[-1][time_field]
            return_dict = {"main_entries": main_db_entries, "min_date": min_date_main_db, "max_date": max_date_main_db}
            return return_dict
        except Exception as e:
            self.reconnect()
            logging.error(f'Issue with getting records in time range', exc_info=True)
            return {"main_entries": [], "min_date": "error", "max_date": "error"}


    def receive(self, address_names, duration):
        """
        Takes in the address names and the duration
        """
        pass 
        #These functions should never block - no "always"
        #duration defined for this driver (makes no sense)

        #Get the addresses 

        #Actually receive does not make a whole lot of sense here
        #Should not be receiving new messages from a database
        #So maybe don't define this guy at all? 

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
                        content_send_list.append(content)
            self.sent_entries[collection_name] = new_entry_ids
            #If we indeed have new messages, send 'em 
            if content_send_list != []:
                succ = self.insert_records(content_send_list, collection_name)
                if not succ:
                    logging.error(f"Could not send messages on address {address_name} for collection {collection_name}", exc_info=True)
        #Disconnect if not a persistent connection 
        if not self.persistent_connection:
            self.disconnect() 
    

def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return Mongodb(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)

         