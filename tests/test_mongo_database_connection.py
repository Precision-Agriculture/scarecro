
import sys
sys.path.append("../scarecro")
import importlib 
import json 

#TODO: Doc strings for all tests 
#Also need a better way to configure tests, I think 
#This code is not very dry. Should functionalize out inserting, deleting, and checking test data, I think. 

def return_test_record():
    test_record  = {
        "id": "test_record_1",
        "status": "unchanged",
        "time": "2023-01-01T00:00:00.000000"
    }
    return test_record.copy()

def return_delete_test_record_query():
    query = {
        "op": "=",
        "field": "id",
        "value": "test_record_1"
    }
    return query.copy()

def return_update_record_query():
    query = [
        {
        "op": "=",
        "field": "id",
        "value": "test_record_1"
        },
        {
        "op": "=",
        "field": "status",
        "value": "changed"
        },
    ]
    return query.copy()

def test_get_all_records_in_time_range(database_class, collection_name, auto_config={}):
    min_time = auto_config["time_range"]["min_time"]
    max_time = auto_config["time_range"]["max_time"]
    time_field = auto_config["time_range"]["time_field"]
    ids = auto_config["time_range"]["ids"]
    id_field = auto_config["time_range"]["id_field"]
    results = database_class.get_all_records_in_time_range(min_time, max_time, time_field, ids, id_field, collection_name)
    if results == {}:
        return_val = False
    else:
        print(f"Number of results {len(results)}")
        return_val = True
    print(f"Time Range Pull Result: {return_val}")
    if return_val == False:
        print("(A False value could also mean no records match, not necessarily a software failure)")

    return return_val


def test_get_record(database_class, collection_name):
    test_record_1 = return_test_record()
    success = database_class.insert_records(test_record_1, collection_name)
    print(f"Record was inserted? {success}")
    get_record = database_class.get_record(collection_name, "test_record_1", "id")
    if get_record != []:
        got_record = True
    else:
        got_record = False
    print(f"Got Record? : {got_record}")
    print(f"Record: {get_record}")
    if success and got_record:
        return_val = True
    else:
        return_val = False
    delete_query = return_delete_test_record_query()
    delete_succ = database_class.delete_records(delete_query, collection_name, verbose=True)
    print(f"Succesfully deleted this test case? {delete_succ}")
    return return_val

def test_delete_record(database_class, collection_name):
    test_record_1 = return_test_record()
    test_record_2 = return_test_record()
    success = database_class.insert_records(test_record_1, collection_name)
    #success = database_class.insert_records([test_record_1, test_record_2], collection_name)
    print(f"Record was inserted? {success}")
    can_find = database_class.check_record_existence("test_record_1", "id", collection_name)
    print(f"Could find record in database? {can_find}")
    delete_query = return_delete_test_record_query()
    delete_succ = database_class.delete_records(delete_query, collection_name, verbose=True)
    if success and can_find and delete_succ:
        return_val = True
    else:
        return_val = False
    print(f"Succesfully deleted this test case? {delete_succ}")
    return return_val 

def test_update_record(database_class, collection_name):
    test_record_1 = return_test_record()
    insert_success = database_class.insert_records(test_record_1, collection_name)
    print(f"Record was inserted? {insert_success}")
    new_record = return_test_record()
    new_record["status"] = "changed"
    update_success = database_class.update_record(collection_name, "test_record_1", "id", new_record)
    print(f"Record was updated? {update_success}")
    update_query = return_update_record_query()
    can_find = database_class.return_records_matching_query(update_query, collection_name)
    print(f"Could find record in database? {can_find}")
    if insert_success and update_success and can_find:
        return_val = True
    else:
        return_val = False 
    delete_query = return_delete_test_record_query()
    delete_succ = database_class.delete_records(delete_query, collection_name, verbose=True)
    print(f"Succesfully deleted this test case? {delete_succ}")
    return return_val 
    #Then delete, in a sec

def test_insert_record(database_class, collection_name):
    test_record_1 = return_test_record()
    test_record_2 = return_test_record()
    success = database_class.insert_records(test_record_1, collection_name)
    #success = database_class.insert_records([test_record_1, test_record_2], collection_name)

    print(f"Record was inserted? {success}")
    can_find = database_class.check_record_existence("test_record_1", "id", collection_name)
    print(f"Could find record in database? {can_find}")
    if success and can_find:
        return_val = True
    else:
        return_val = False
    delete_query = return_delete_test_record_query()
    delete_succ = database_class.delete_records(delete_query, collection_name, verbose=True)
    print(f"Succesfully deleted this test case? {delete_succ}")
    return return_val 
    
def test_a_query_to_the_database(database_class, collection_name, query):
    results = database_class.return_records_matching_query(query, collection_name, verbose=True)
    if results == []:
        return_val = False
    else:
        print(f"Number of results {len(results)}")
        return_val = True
    print(f"Query Result: {return_val}")
    if return_val == False:
        print("(A False value could also mean no records match, not necessarily a software failure)")
    return return_val  
    

#Probably only valid for Mongo 
def test_getting_a_collection(database_class, collection_name):
    collection = database_class.get_collection(collection_name)
    print(f"Collection Type: {type(collection)}")
    if collection != None and collection != False:
        return_value = True   
    else:
        return_value = False
    print(f"Collection Retrieval Result: {return_value}")
    return return_value


def connect_to_specific_database(database_driver, database_name, database_config):
    """
    Input: Database Driver from user selection, database name from user selection
    and import config
    connects to database name indicated and returns connection result
    """
    specific_database_name_config = database_config[database_name]
    database_class = database_driver.return_database_instance(specific_database_name_config)
    connection_status = database_class.connect()
    return connection_status, database_class 

def disconnect_from_database(database_class):
    disconnection_status = database_class.disconnect()
    return disconnection_status


def test_connecting_and_disconnecting(database_driver, database_name, database_config, prompt_mode=True):
    """
    Input: Database Driver, database name
    3. connect and disconnect from the database
    4. print results
    """
    print(f"Connecting to {database_name}...")
    connection_status, database_class = connect_to_specific_database(database_driver, database_name, database_config)
    print(f"Connection Status Result: {connection_status}")
    print("Attempting Disconnect...")
    disconnection_status = database_class.disconnect()
    print(f"Disconnection Status Result: {disconnection_status}")
    if connection_status and disconnection_status:
        return True 
    else:
        return False 


def get_database_driver_and_config(database_driver_name):
    #This allows a dynamic import. 
    database_driver_string = "data_endpoints."+database_driver_name
    database_driver = importlib.import_module(database_driver_string, package=None)
    #Import the config
    config_string = "configs.data_endpoints."+database_driver_name
    database_config_module =  importlib.import_module(config_string, package=None)
    database_config = database_config_module.config
    return database_driver, database_config

def return_test_options_dict():
    test_options = {
        "1": "1. Test connection to and disconnecting from the database",
        "2": "2. Test getting a particular collection from the database (Will create, but not maintain, collection if doesn't exist)",
        "3": "3. Test a query to the database",
        "4": "4. Test inserting a record to the database",
        "5": "5. Test updating a record in the database",
        "6": "6. Test deleting a record from the database",
        "7": "7. Test checking a record's existence in the database",
        "8": "8. Test getting a record from the database",
        "9": "9. Test getting all records in a time range",
    }
    return test_options.copy()

def run_test(test_selection, database_driver_name, database_driver, database_name, database_config, prompt_mode=False, collection_name=None, auto_config=None):
    test_options = return_test_options_dict()
    print(test_options[str(test_selection)])
    test_number = int(test_selection)
    if test_number == 1:
        result = test_connecting_and_disconnecting(database_driver, database_name, database_config, prompt_mode=True)
    else:
        connection_status, database_class = connect_to_specific_database(database_driver, database_name, database_config)
        if test_number == 2:
            result = test_getting_a_collection(database_class, collection_name)
        if test_number == 3:
            query = auto_config["query"]
            result = test_a_query_to_the_database(database_class, collection_name, query)
        if test_number == 4:
            result = test_insert_record(database_class, collection_name)
        if test_number == 5:
            result = test_update_record(database_class, collection_name)
        if test_number == 6: 
            result = test_delete_record(database_class, collection_name)
        if test_number == 7: 
            result = test_insert_record(database_class, collection_name)
        if test_number == 8:
            result = test_get_record(database_class, collection_name)
        if test_number == 9:
            #Clean up. Come on. 
            result = test_get_all_records_in_time_range(database_class, collection_name, auto_config=auto_config)
        disconnection_status = disconnect_from_database(database_class)
    return result 

def test_database_prompt_mode():
    """
    Allows user to select options to test database from 
    """
    #Get type of database from user  
    database_driver_name = input("Testing the database connection. What driver are you using?\n")
    database_driver, database_config = get_database_driver_and_config(database_driver_name)

    database_options = list(database_config.keys())
    print("Databases found: ")
    for sub_database in database_options:
        print(sub_database)
    database_name = input("Type the database name you would like to connect to: \n")    

    #Lists user options for tests
    print("Here are the potential tests that can be run. Please select from the following:")
    test_options = return_test_options_dict()
    for key, value in test_options.items():
        print(value)

    test_number = input("Select the number test you would like to run\n")
    print(f"You selected test {test_number}")

    if int(test_number) > 1:
        #Type collection desired
        collection_name = input("Type the collection name you want to use: \n")
        run_test(test_number, database_driver_name, database_driver, database_name, database_config, prompt_mode=True, collection_name=collection_name)   
    else:
        run_test(test_number, database_driver_name, database_driver, database_name, database_config, prompt_mode=True, collection_name=None)

def test_database_auto_mode():
    """
    Run tests automatically from a script-wide configuration
    """ 
    test_summary = {}
    #Get the driver and config 
    database_driver_name = auto_config["database_driver"]
    database_driver, database_config = get_database_driver_and_config(database_driver_name)
    #Get the specific database config
    database_name = auto_config["database_name"]
    specific_database_config = database_config[database_name]
    #Get collection 
    collection_name = auto_config["default_data_source"]

    print(f"Using database driver: {database_driver_name}")
    print(f"Using database: {database_name}")
    print(f"Default collection: {collection_name}")
    
    #Now actually run the tests 
    for test_number in auto_config["tests_to_run"]:
        print("----------------")
        result = run_test(test_number, database_driver_name, database_driver, database_name, database_config, prompt_mode=False, collection_name=collection_name, auto_config=auto_config)
        test_summary[test_number] = result
    print_test_summary(test_summary, auto_config)

def print_test_summary(test_summary, auto_config):
    print("*********************")
    print("For configuration: ")
    print(json.dumps(auto_config, indent=4))
    test_options = return_test_options_dict()
    print("---------RESULTS--------")
    for key, value in test_summary.items():
        print(test_options[str(key)])
        print(f"Result: {value}" )

auto_config = {
    "tests_to_run": [5],
    "database_driver": "mongodb",
    "database_name": "SOAC",
    "default_data_source": "gateway_stats",
    "query": 
        {
        "op": "is",
        "field": "id",
        "value": "test_record_1"
        },
    "time_range":{
        "min_time": "2023-08-01T00:00:00.000000",
        "max_time": "2023-08-01T02:00:00.000000",
        "time_field": "time",
        "ids": ['1'],
        "id_field": "id"
    }
}

#Create fake test data for all test cases, in the future
#This is good for now, but more powerful later. 
if __name__=="__main__":
    prompt_mode = input("Prompt Mode? Y/N\n")
    if prompt_mode == "Y" or prompt_mode == 'y' or prompt_mode == "yes" or prompt_mode == "Yes":
        #MARKED 
        #Going forward, I'm not sure interactive mode is the best choice. 
        #Might want to import autoconfig? and gitignore?
        test_database_prompt_mode()
    else:
        test_database_auto_mode()
