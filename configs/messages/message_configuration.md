## 
# Message Definitions 
A message definition should be a dictionary with the following form: 
message = {
    "inheritance": A string or list of string of messages this message inherits from. 

    "id_field": The identification field of the message content. This will usually identify the device sending it, but may
    be another way of identifying distinct messages

    "time_field": The field of the message the identifies where the time of message generation/receipt is located 
}

Messages exchanged by the system between processes will be packaged in the following format:
{
"msg_type": the type of message 

"msg_id": the id of the message, indicated by the id_field

"msg_time": the time the message was received

Added before?? 

"msg_entry" (optional): The incrementing message number by carrier, which helps carriers determine if the message has been seen already. This will be present if the message is coming from the system message table. It will not be present otherwise. 

"carrier_name": Name of configured carrier that recieved the message 

"msg_content": The actual content of the message 
} 
