# SCARECRO POST

SCARECRO Post is an IoT model with configurable message transmission elements. In particular, you can configure:

* The type of message
Analogy: birthday card, bill payment, pizza coupon
Technology: sensor reading, API data, form entry

* The type of carrier:
Analogy: mail truck, mail person, mail plane, etc. 
Technology: MQTT, HTTP, S3, etc.


* The type of address:
Analogy: House mailbox, business mailbox
Technology: Database, Mobile App 


* The type of handler 
Analogy: Person writing to pen pal, business creating marketing campaign
Technology: message processing code 

## Messages
to do...

## Addresses
to do...

## Carriers

Carriers in a post office scenario vary based on the function they perform. A mail person might be good for small packages in a close neighborhood. A mail truck might be suited for packages and envelopes on a snowy mountain culdesac. And a cargo boat might be needed to ship furniture to overseas, and a freight plane might be needed to get a message somewhere as quickly as possible. 

In the same way, different messages and payloads might be sent via different transportation protocols based on their individual requirements in an IoT system. Frequent, lightweight messages might be sent best through the MQTT protocol, while once-a-day pictures may need to be directly uploaded to an S3 bucket. Binary software images for a downstream Data Gator might be best suited for an HTTP server. The right carrier needs to be configured and implemented for the right job. 

Carriers are modeled in software as a class structure. They are initialized with their configuration, a list of sending addresses, a list of receiving addresses, and a list of message configurations for the messages types indicated by the addresses. Depending on how the code is implemented, they may or may not need this information -- that is up to the implementer to decide. They have one or both of the following functions:

send - takes in a list of addresses, and sends messages corresponding to those addresses when called

receive - takes in a list of addresses, and receives messages corresponding to those addresses when called. 

These functions will be instantiated to run based on the duration of the addresses they recieve: (Note: Either function will ONLY be called with addresses that have the same duration!)


If the duration is "always":
    The function will be called once and run forever. In this case, the carrier should be configured to run the function forever without dying 

If the duration is a number of seconds:
    The function will be called once every corresponding number of seconds. It should not hang a program. 


If the duration is "as_needed":
    The function will not be called directly by the scheduler. It is assumed that it will be called by another function. 

If duration is "on_message" (relevant only for receive addresses):
    The function will be called every time a message corresponding to its address is received 

The carriers interact with the post office (main system) with the following two functions:

* post_messages: the function takes in a single message or list of messages and an address name and accepts a message(s) into the post office (runs them through any handlers first). This would typically be used in the receive function. It returns True or False as a result (whether it was successful). 

* pickup_messages: the function takes in an address and an optional list of message ids (typically just in the on_message duration case) and only picks up the messages corresponding to the address. If a list of message ids is provided, it will filter the messages it picks up by the message ids. Returns a list of corresponding messages (runs them through the handlers first). This would typically be used by the send function. 

## Handlers 

to do...


## Post Office
The post office is modeled internally by a dictionary with the following form: 

    {
    message_type: 
        {            
        "latest_entry_id": 0,
            "semaphore": threading.Semaphore(),
            "messages": 
            {
                msg_id: {<enveloped message>}
                msg_id: {<enveloped message>}
            }
        }
                
    }

    Where enveloped messages are dictionaries with the following fields:

    {
        "msg_id": the id of the actual message
        "msg_time": The time of receipt of the message
        "msg_type": The type of message
        "msg_content": The content of the message
        "entry_id": The id of the message entry, added by the post office. This is roughly equivalent to a postmark and tracks unique messages. This is missing prior to posting the message, but present after (hence the postmark equivalence)
    }


Incidentally, the main system object is stored in the variable "system" in the system_object.py file. All changes (like initializing it and using its functions) should occur by using "system_object.system".  This is a bit strange with the python import system. 

## Scheduling 
Regular routes:
    to do...

Perpetual Routes:
    to do...