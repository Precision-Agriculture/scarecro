## Addresses
Addresses should be a dictionary of the following form:

config = {
    "inheritance": a name of list of other names addresses to inherit from

    "message_type": the type of message this address deals with. If this is a list, the underlying system will break the address into multiple addresses by message type, naming them <address_name>_<message_type>. An address cannot inherit from another address with multiple messages. 

    "handler": the name of the handler config for this message before send/after receive. This can be None, if no processing is needed. 

    "handler_function": the function in the processing object that will receive the message for processing as its argument. 

    "send_or_receive": "send" or "recieve", indicating whether the is the receiving address for a message or the sending addresses for a message

    "carrier": The object that will send or receive the message.

    "duration": How often the message is sent through the system. This can be:
         "always", if the message is always being sent or recieved, 
          a value in seconds, for how often the message is being sent or received, 
          "on_message", for a sender that sends on every new message coming through, or
          "as_needed", if the send or received is triggered by something else on an as_needed basis 
    }
    
    "additional_info": This is any additional information that may be needed to send the message effectively. This might be message-specific endpoint information, for example, for a sender or receiver. This will likely vary by carrier. 


## This needs to move 

In system dict, addresses are in dict:

addresses: {
address_name: address_content
}

and system config??? 

while everything else is: 

messages:
{
    message_name: {
        addresses: [],
        content: {<message_content>}
    }
}
