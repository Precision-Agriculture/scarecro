import sys
import time 
import logging 
import json 
import boto3
sys.path.append("../scarecro")
import system_object
import util.util as util 
#https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html

#This gets to be an insane amount of input if not surpressed
if logging.root.level <= logging.DEBUG:
    logging.getLogger('boto3').setLevel(logging.INFO)
    logging.getLogger('boto').setLevel(logging.INFO)
    logging.getLogger('botocore').setLevel(logging.INFO)
    logging.getLogger('s3transfer').setLevel(logging.INFO)


class S3_Bucket():
    def __init__(self, config, send_addresses, receive_addresses, message_configs):
        """
        S3 Clients need in the config: 
            bucket_name: name of the S3 bucket that will be read/written to
            access_key_id: Access key id of the S3 bucket
            secret_access_key: secret access key of the S3 bucket
            path: optional file path start of any files in the bucket (no trailing / allowed)
        """
        #arguments passed in 
        self.config = config.copy() 
        self.monitor_connection = self.config.get("monitor_connection", False)
        self.send_addresses = send_addresses.copy()
        self.receive_addresses = receive_addresses.copy()
        self.message_configs = message_configs.copy()
        #Set up connection info 
        self.bucket_name = self.config.get("bucket_name", None)
        self.access_key_id = self.config.get("access_key_id", None)
        self.secret_access_key = self.config.get("secret_access_key", None)
        self.path = self.config.get("path", "")
        #System id 
        self.system_id = self.config.get("system_id", "default")
        self.sent_entries = {}
        try:
            self.s3_client = boto3.client('s3',
                            aws_access_key_id = self.access_key_id,
                            aws_secret_access_key = self.secret_access_key
                            )
        except Exception as e:
            logging.error(f"Could not intialize S3 client: {e}", exc_info=True)

        #Map sub-paths to addresses and messages 
        self.map_paths()
        #Set up message definitions for looking up messages 
        logging.info("Initialized S3 carrier")


    def map_paths(self):
        """
        Get information from the send and receive addresses 
        To map databases to addresses and vice versa
        """
        self.all_addresses = {**self.send_addresses, **self.receive_addresses}
        sub_path_address_mapping = {}
        address_sub_path_mapping = {}
        for address_name, address_config in self.all_addresses.items():
            s3_config = address_config.get("additional_info", {})
            sub_path = s3_config.get("sub_path", None)
            sub_path_address_mapping[sub_path] = address_name
            address_sub_path_mapping[address_name] = sub_path
        self.sub_path_address_mapping = sub_path_address_mapping
        self.address_sub_path_mapping = address_sub_path_mapping

    def download_file(self, cloud_path, disk_path):
        """
        This function takes the cloud s3 path of the file 
        And the disk path of the new file
        And downloads the cloud file to the disk 
        """
        try:
            #file_name - in bucket
            #object_name - on disk 
            response = self.s3_client.download_file(self.bucket_name, cloud_path, disk_path)
        except Exception as e:
            logging.error(f"Could not download S3 {cloud_path} to {disk_path} for reason {e}")

    def upload_file(self, cloud_path, disk_path):
        """
        This function takes the cloud s3 path of the file 
        And the disk path of the new file
        And uploads the disk file to the cloud 
        """
        try:
            response = self.s3_client.upload_file(disk_path, self.bucket_name, cloud_path)
        except Exception as e:
            logging.error(f"Could not upload S3 {disk_path} to {cloud_path} for reason {e}")


    def receive(self, address_names, duration):
        """
        High level exposure function of the carrier 
        Receives a list of addresses (all with same duration). Depending 
        on the duration and the address, it sets itself
        up to 'receive' messages. 
        This function will not work for the "always" duration  
        MARKED - not really defined? - need specific file 
        """ 
        pass 

    def make_path_name(self, sub_path):
        if self.path == None or self.path == "":
            use_path = self.path 
        else:
            use_path = f"{self.path}/"
        if sub_path == None or sub_path == "":
            use_sub_path = sub_path
        else:
            use_sub_path = f"{sub_path}/"
        final_path = f"{use_path}{use_sub_path}"
        return final_path

    def send(self, address_names, duration, entry_ids=[]):
        """
        High level exposure function of the carrier
        Takes in an optional list of entry ids
        Grabs the messages and publishes them, optionally filtering by ID 
        No "always" duration is really defined for this driver, don't use with always 
        This is expected to be executed mostly "on message" 
        """
        for address_name in address_names:
            try:
                #Pick up the messages - only if we haven't already sent them
                #MARKED - may also want for MQTT 
                sent_entries = self.sent_entries.get(address_name, [])
                #Don't resend old messages 
                pick_up_list = [entry for entry in entry_ids if entry not in sent_entries]
                messages = system_object.system.pickup_messages(address_name, entry_ids=pick_up_list)
                new_entry_ids = []
                #Send each message individually                    
                for message in messages:
                    #Mark for sending
                    entry_id = message.get("entry_id", None)
                    new_entry_ids.append(entry_id)
                    #Get the filename
                    content = message.get("msg_content", {})
                    #Get the filename
                    file_name = content.get("file_name", None)
                    if file_name:
                        #Disk path defaults to just the file name 
                        disk_path = content.get("disk_path", file_name)
                        #If the cloud path already configured, great. 
                        cloud_path = content.get("cloud_path", None)
                        #Otherwise - use s3 path associated with address 
                        if cloud_path == None:
                            sub_path = self.address_sub_path_mapping.get(address_name, "")
                            final_path = self.make_path_name(sub_path)
                            cloud_path = f"{final_path}{file_name}"
                        logging.debug(f"Image upload disk path {disk_path}")
                        logging.debug(f"Image upload cloud path {cloud_path}")
                        self.upload_file(cloud_path, disk_path)
                #Record sent entries 
                if new_entry_ids != []:
                    self.sent_entries[address_name] = new_entry_ids
            except Exception as e:
                logging.error(f"Could not upload file on address {address_name}", exc_info=True)
    
def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return S3_Bucket(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)
