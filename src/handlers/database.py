import sys
sys.path.append("../scarecro")

class Database:
    """
    Super class for Database object 
    """
    def __init__(self, config):
        """
        Uses configuration to set itself up.
        """
        pass 

    def connect(self):
        """
        connects to the database 
        """
        pass 

    def disconnect(self):
        """
        Disconnects from the database 
        """
        pass 

    def reconnect(self):
        """
        Reconnects to the database, if operation
        different from connect/disconnect
        """
        pass 

    def insert_records(self, records, data_source_name):
        """
        Insert a record or list of records into the database.
        """
        pass 

    def update_record(self, data_source_name, record_id, record_id_field, new_record):
        """
        Update existing record with new information 
        Will likely need additional info
        """
        pass 

    def delete_records(self, records, data_source_time):
        """
        Delete existing records from the database
        """
        pass 

    def check_record_existence(self, record_id, record_id_field, data_source_name):
        """
        Check to see if a given record exists in the database
        """
        return False 

    def get_record(self, data_source_name, record_id, record_id_field):
        """
        Get a particular record
        """
        pass 

    def return_records_matching_query(self, query, data_source_name):
        """
        Query the database and return matching records
        """
        records = []
        return records 

    def get_all_records_in_time_range(self, min_time, max_time, time_field, data_source_name):
        """
        Gets all the records in a given time range
        """
        records = []
        return records 

    # def get_last_n_reported_records(self, data_source_name, n):
    #     """
    #     Get the last n reported records for a given data source
    #     """
    #     records = []
    #     return records 



