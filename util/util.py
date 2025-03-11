from datetime import datetime, timedelta, tzinfo
from datetime import timezone
from datetime import date
import pytz
from dateutil import tz 


#Help from here: https://stackoverflow.com/questions/25856985/how-to-get-difference-in-seconds-between-two-strings
#And here: https://stackoverflow.com/questions/127803/how-do-i-parse-an-iso-8601-formatted-date
#Compares the seconds between each. Returns the difference in total seconds
def compare_seconds(time_string_1, time_string_2):
    #Get datetime objects from time strings
    time_1 = datetime.strptime(time_string_1, "%Y-%m-%dT%H:%M:%S.%f")
    time_2 = datetime.strptime(time_string_2, "%Y-%m-%dT%H:%M:%S.%f")
    #Subtract the two and take the absolute value of the difference in seconds
    time_diff = time_2 - time_1
    time_diff = time_diff.total_seconds()
    return time_diff

#Help from here! https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime 
def convert_utc_to_local(og_time, format="string"):
    time = datetime.strptime(og_time, "%Y-%m-%dT%H:%M:%S.%f")
    utc_zone = tz.gettz('UTC')
    local_zone = tz.gettz('America/New_York')
    time = time.replace(tzinfo=utc_zone)
    #MARKED
    time = time.astimezone(local_zone)
    time_string = time.strftime("%Y-%m-%dT%H:%M:%S.%f") 
    if format == 'string':
        return time_string
    else:
        return time

#Help from here: https://www.geeksforgeeks.org/get-current-date-using-python/ 
#And here: #Help from here: https://stackoverflow.com/questions/4530069/how-do-i-get-a-value-of-datetime-today-in-python-that-is-timezone-aware
def get_today_date_time_local(format="string"):
    #MARKED
    local_time_zone = 'US/Eastern'
    time_zone = pytz.timezone(local_time_zone)
    now = datetime.now(time_zone)
    now_string = now.strftime("%Y-%m-%dT%H:%M:%S.%f") 
    if format == 'string':
        return now_string
    else:
        return now

#Get the current datetime in UTC - defaults to string 
def get_today_date_time_utc(format="string"): 
    get_time = datetime.now()
    time_utc = get_time.astimezone(pytz.UTC)
    time_utc = time_utc.replace(tzinfo=timezone.utc)
    if format == 'string':
        return time_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")
    else:
        return time_utc


#Help from here: https://thispointer.com/how-to-add-minutes-to-datetime-in-python/ 
#Might need to return this as a datetime too 
def add_to_time(time_string, seconds):
    #Get datetime objects from time strings
    time = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%f")
    #Subtract the two and take the absolute value of the difference in seconds
    if seconds > 0:
        final_time = time + timedelta(seconds=seconds)
    else:
        final_time = time - timedelta(seconds=abs(seconds))
    return final_time.strftime("%Y-%m-%dT%H:%M:%S.%f")

def convert_string_to_datetime(time_string):
    the_time = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%f")
    return the_time 


# #Might want to override the time field there. 
# def envelope_message(msg_id, time, message_type, message):
#     envelope_dict = {
#         "msg_id": msg_id,
#         "msg_time": time,
#         "msg_type": message_type,
#         "msg_content": message
#     }
#     return envelope_dict.copy()

def forward_backward_map_additional_info(addresses):
    """
    Takes in a dictionary address_name: address_config 
    Or a list of dictionaries of this form
    Creates a dictionary that maps the addresses' 
    additional info forward and backward
    dict[keyword]["value"]][keyword] = address_name
    and
    dict[keyword]["address_name"][address_name] = [value]
    """
    if isinstance(addresses, list):
        address_dictionary = {}
        for sub_address in addresses:
            address_dictionary = {**address_dictionary, **sub_address}
    mapping_dict = {} 
    for address_name, address_config in address_dictionary.items():
        add_info = address_config.get("additional_info", {})
        #Forwards and backwards map the additional info. 
        for key, value in add_info.items():
            if key not in list(mapping_dict.keys()):
                mapping_dict[key] = {"value": {}, "address_name": {}}
            mapping_dict[key]["value"][value] = address_name
            mapping_dict[key]["address_name"][address_name] = value
    return mapping_dict 
