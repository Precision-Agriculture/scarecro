# SCARECRO 
The Sensor Collection and Remote Environment Care Reasoning Operation (SCARECRO) software repo

## Status
This repository is a work in progress. An initial version of SCARECRO is implemented in several test areas. We are currently in the process of refactoring the software as we release it open-source. 

## Structure of Repo
* __configs__: The configs folder contains configuration files for the given SCARECRO system. Each SCARECRO system will have different configuration files. These files are git-ignored for a given repo except for certain example files. The configs folder contains several sub-folders, depending on the type of config. 
    * addresses 
    * carriers
    * handlers
    * messages
    * other
    * system
    * tasks

More about configurations is explained later in the ReadMe 
* __examples__: This folder will contain useful example code. Currently not implemented. 

* __generated_data__: This folder should be empty on a brand-new repo and will contain data that the SCARECRO system generates as it runs, if configured. (Think: Pictures the system has the camera take, logs, etc). The data in this folder is git-ignored. 

* __src__: Contains the source files for the SCARECRO system. Includes sub-folders: 
    * carriers:
    * handlers
    * other
    * system
    * tasks

The src sub folders contain the code implementation of SCARECRO item classes. 
* __tests__: Contains code to test pieces and parts of the system. 

* __util__: Contains general utility code/functions for use by the system. 

The system_object.py file will be used by the repo to create the global system object the system makes use of. 


## Class or System Diagram
TODO: Insert a class diagram that relates all the system components together. 

## Basic Concepts
There are two basic concepts to the SCARECRO system:

* __source code__: The actual software implementing a given class type or functionality, and 

* __configurations__: The configured instances of a class or function implemented in the source code. 

What's key is that there can be multiple configurations for one implementation of the source code. We have found that to be necessary to handle multiple types of communication protocol, message type, database, etc. 

## Basic Classes
There are several basic classes of object in the SCARECRO system. These are: 

* __messages__: These are the most basic type of configuration in the system. Messages must at least contain an id_field (to indicate what actor sent the message) and a time field (to indicate when the message was sent). Messages    

* __carriers__: Carriers send and receive messages. There analogous component in the post office illustration could be a mail car, a mail truck, a door-to-door mail carrier, or even a mail plane. Carrier configurations should have, at minimum, a source field indicating the source code implementation of the carrier.

* __handlers__: Handlers are objects that deal with message content, including structuring, reorganizing, interpreting, or reorganizing message content. Handlers may not be necessary in all cases, especially if a message comes ready to use from a sensor. Handlers can be different on a incoming or outgoing message, or may only be used in one or the other. Handler functionality could be implemented entirely within a carrier, but it is often useful to separate this functionality, especially when working with multiple different brands of sensors using the same communication protocol (like several bluetooth sensors with different manufacturers). Handler configurations, should, at minimum, have a source field which indicates their source code class implementation. 
Why are handlers necessary? Sometimes you might have a group of sensors that use related interpration or cleaning functions which are useful to have decoupled from the actual sending/receiving procotols, especially if those protocols are shared with others types of sensors or data sources. 

* __addresses__: The address configuration is necessary to actually send and receive messages, and ties together carriers, handlers, and messages. Configured addressed have an inheritance field (similar to the other objects) That allows them to inherit configuration values from other addresses, a message_type field indicating what type of message is to be sent or received, a handler field indicating the name of the handler config to be used, a handler_function field, indicating the function name to be used on the handler class, a send_or_receive function, which can take the value "send" or "receive" to indicate if the address is incoming or outgoing, and a "duration" field. There are 4 possible durations: "always", (typically only relevant on a "receive" message), indicating that the the carrier should always be listening for this message, a value in seconds (integer value), which indicates how often the message will be sent or received, "on_message" (only releavant on a "send" message), indicating the message should be sent as soon as one is received, and "as_needed", which indicates the send or receive is triggered by something else and has no default triggering behavior. Finally, addresses have an "additional_info" field which should link to a dictionary of additional key-pairs that may relevant for any functionality in the system. For instance, certain carriers may requre per-message string matches. Some additional info may be implemented at the message level, or at the address level - programmer's choice. 

* __tasks__: TODO: Implement. Tasks are system (post office in the analogy)-specific functionality vital to keep the processes running smoothly. 

* __system__: The system object is a special type of class to configure system parameters. It is described in more detail in a later section. 


## System Object 

### System Configuration 
The system object is configured by default under the "system" folder in the "configs" folder. The system object configuration dictionary expects the following fields: 

* __"id"__: The id of the instantiated system 
* __"addresses"__: a list of address configuration names that the user would like to have active in the system
* __"tasks"__: a list of task configuration names that the user would like to have active in the system 

The system configuration  essentially details what kind of functionality should be active in a given implementation of a SCARECRO system. It is the most basic blueprint of a given gateway or middle agent for which it is relevant. 

Again, by default this lives in the "system" folder under the "configs" folder with the name "system.py". However, this can be overriden by passing a different system dictionary configuration object to the system object. This is handy for test scripts and when testing different configurations.  

### System Object Responsibilities 
The system object is the main "brain" of the SCARECRO system. It is responsible for:
* Initializing itself with the proper functionality it is configured for. This includes:
    * Ensuring proper inheritance on all configurations
    * Ensuring keyword substituion on all configurations
    * Ensuring source code exists for all configurations  
* Scheduling all system behavior, including:
    * All carrier sending/receiving functions, at the proper duration, or linked to the proper trigger
    * All tasks the system must run 
    * And tying handler functions to incoming or outgoing messages
* ADD ... ? 

## Stored State Messages
TODO: Maybe move this into a more relevant section? 
Messages Received by the System are stored in state as a "message table" which is actually a dictionary of this format:   

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

For example, let's say we receive ave the following messages: 

- A message from a weather rack sensor with ID 21 (received first)
- A message from weather rack sensors with ID 39 (received second)
- A message from bmp280 sensor with ID 301 (received third)

The dictionary in the system state would look like this 

    {
        weather_rack: {
            "latest_entry_id": 1
            "semaphore": <semaphore_object_000>,
            "messages": {
                21: {
                    "entry_id": 0
                    "msg_id": 21, 
                    "msg_time": "2024-05-16T00:00:00.000000",
                    "msg_type": "weather_rack"
                    "msg_content": {
                        "temperature": 60
                        ...
                    }
                    ...
                },
                39: {
                    "entry_id": 1
                    "msg_id": 39, 
                    "msg_time": "2024-05-16T00:05:00.000000",
                    "msg_type": "weather_rack" 
                    "msg_content": {
                        "temperature": 43
                        ...
                    }
                    ...
                },

            }
        "bmp280": {
            "latest_entry_id": 0,
            "semaphore":  <semaphore_object_001>,
            "messages": {
                "301": 
                {
                    "entry_id": 0
                    "msg_id": 301, 
                    "msg_time": "2024-05-16T00:15:00.000000"
                    "msg_type": "bmp280" 
                    "msg_content": {
                        "pressure": 52
                        ...
                }
            }
    }

Which basically corresponds to a table that would look like this: 

| Message Type | Message ID | Entry ID | Message Content | 
| ------------ | ---------- | -------- | -------- | 
| weather_rack |     21     |  0  | {temperature: 60,...} |
| weather_rack |    39      |  1  |  {temperature: 43,...}|
| bmp280       |    301     |  0  | {pressure: 52, ...} | 

If we get a new weather rack message from ID 21, with a new reading, the underlying dictionary would update: 

    {
        weather_rack: {
            "latest_entry_id": 2
            "semaphore": <semaphore_object_000>,
            "messages": {
                21: {
                    "entry_id": 2
                    "msg_id": 21, 
                    "msg_time": "2024-05-16T00:00:00.000000",
                    "msg_type": "weather_rack"
                    "msg_content": {
                        "temperature": 56
                        ...
                    }
                    ...
                },
                39: {
                    "entry_id": 1
                    "msg_id": 39, 
                    "msg_time": "2024-05-16T00:05:00.000000",
                    "msg_type": "weather_rack" 
                    "msg_content": {
                        "temperature": 43
                        ...
                    }
                    ...
                },

            }
        "bmp280": {
            "latest_entry_id": 0,
            "semaphore":  <semaphore_object_001>,
            "messages": {
                "301": 
                {
                    "entry_id": 0
                    "msg_id": 301, 
                    "msg_time": "2024-05-16T00:15:00.000000"
                    "msg_type": "bmp280" 
                    "msg_content": {
                        "pressure": 52
                        ...
                }
            }
    }

And this would correspond to a message table that looks like: 
| Message Type | Message ID | Entry ID | Message Content | 
| ------------ | ---------- | -------- | -------- | 
| weather_rack |     21     |  2  | {temperature: 56,...} |
| weather_rack |    39      |  1  |  {temperature: 43,...}|
| bmp280       |    301     |  0  | {pressure: 52, ...} |

You can see that only the latest message from each possible sender (indicated by the message id) is kept by the system in order to avoid massive memory bloat. If message histories need to be kept, the maintainers would recommend utilizing a database carrier trigged on message receipt, or else implementing this functionality in a handler or carrier. 

## System Behavior 



### Initializing the system 

The system will initialize when it creates a system object. The system object expects a system configuration dictionary to be located in configs/system in a file called system.py, which contains one variable named "system" linked to a dictionary (system = {...}). However, this expectation can be overriden by passing the system a custom system configuration dictionaryt, which it will use instead. To initialize, the system will do the following: 

1. __Grab all the address configs__, from those listed in the system configs. The system will try and resolve inheritahance and substitutions in the address configs at this step. 

2. __Grab all the message configs__, related to the active addresses. The system will try and resolve all inheritance and substitution in the message configs at this step. 

3. __Get all the handler configs__, related to the active addresses. The system will try and resolve all inheritance and substitution in the handler configs at this step. 

4. __Grab all the carrier configs__, related to the active addresses. The system will try and resolve all inheritance and substitution in the carrier configs at this step. 

5. __Grab all task configs__, indicated as active in the system configuration. 

6. __Create a message table__: This system will create an internal message table, with a new entry for each configured message in the system. This new entry for each message is a dictionary with the latest_entry_id field defaulting to 0, a new semaphore object specific to that message type, and a "messages" field linked to an empty dictionary. 

NOTE: Need to indicate what these objects look like IN THE SYSTEM - TODO 

7. __Instantiate the handler objects__: The system will create a new handler object from indicated source code based on the active handler object configurations. This will be stored in the system handler dict (self.handlers) indexed by the handler name.  

8. __Instantiate the carrier objects__: The system will create a new carrier from the indicated source code based  on the active carrier object configurations. This will be stored in the system carrier dict (self.carriers) indexed by the carrier name. 

9. __Instantiate the task objects__: TODO: Fill in 

10. __Create a scheduler__: The system will create a new python APScheduler scheduler (self.scheduler) to handle threading tasks. By default, there is a maximum of 50 thread workers in the scheduler. 

11. __Initialize the scheduler__: The system will create an initialization dictionary for scheduled system tasks based on the active addresses and tasks 

12. __Start the scheduler__: The system will start the job scheduler. This is a non-blocking start, and there must be logic elsewhere in the program to to keep the program running forever without returning. 


### Underlying system storage of objects and configurations 

__Addresses__: 
A dictionary stored in self.addresses of the form: 

    {
        "address_name": address configuration
    }

For example: 

    {
        "datagator_mqtt_in": {
            "inheritance": [],
            "message_type": "datagator",
            "handler": "datagator",
            "handler_function": "process",
            "send_or_receive": "receive",
            "carrier": "mqtt_sensor_listener",
            "duration": "always",
            "additional_info": {
                "topic": "datagator"
            }
        },
        "datagator_mqtt_out": {
            "inheritance": [],
            "message_type": "datagator",
            "handler": "datagator",
            "handler_function": "process",
            "send_or_receive": "send",
            "carrier": "mqtt_sensor_listener",
            "duration": 10,
            "additional_info": {
                "topic": "datagator_2"
            }
        }
    }

__Messages__: 
A dictionary stored in the variable self.messages of the form: 

    {
        "message_name": {
            "addresses": [list of addresses that use the message],
            "content": message config,
        }
    }

For example: 

    {
        "datagator": {
            "addresses": [
                "datagator_mqtt_in",
                "datagator_mqtt_out"
            ],
            "content": {
                "inheritance": [],
                "id_field": "id",
                "time_field": "time"
            }
        }
    }

__Handlers__: A dictionary stored in self.handlers variables of the form: 

    {
        "handler_name": {
            "addresses": [list of addresses that use this handler],
            "content": handler config, 
            "object": reference to actual class object of handler instantiation 
        }  
    }

For example: 

    {
        "datagator": {
            "addresses": [
                "datagator_mqtt_in",
                "datagator_mqtt_out"
            ],
            "content": {
                "source": "datagator"
            },
            "object": "<src.handlers.datagator.DataGator object at 0x7f4982dd3940>"
        }
    }

__Carriers__:

A dictionary stored in the self.carriers variable of the form: 

    {
        "carrier_name": {
            "addresses": [list of addresses that use this carrier],
            "content": carrier config, 
            "object": reference to actual class object of carrier instantiation 
        }  
    }

For example: 

    {
        "mqtt_sensor_listener": {
            "addresses": [
                "datagator_mqtt_in",
                "datagator_mqtt_out"
            ],
            "content": {
                "source": "mqtt",
                "mqtt_url": "b56765a64ba74fa582ab3cadc77f918a.s2.eu.hivemq.cloud",
                "mqtt_port": 8883,
                "mqtt_username": "soacdevice",
                "mqtt_password": "Mc1nt0sh",
                "qos": 1,
                "client_id": "sensor_listener"
            },
            "object": "<src.carriers.mqtt.MQTT_Client object at 0x7f49807a3208>"
        }
    }


__Tasks__: 
A dictionary stored in the self.tasks variable of the form: 

    {
        "task_name": task config
    }

For example: 

{
    "fake_print_often": {
        "source": "fake_task_options",
        "function": "obnoxious_print",
        "arguments": {},
        "duration": 8,
        "object": "<src.tasks.fake_task_options.FakeTasks object at 0x7f4dd5d06ac8>"
    }
}

### Scheduling functions and tasks 
In order to schedule system functionality correctly, the system needs to understand what functions need to be run when. So, the system creates a dictionary for the scheduler with the following form: 

    {
        "job_id":
        {
            "object_name": name of the configured class object in the system
            "object": Reference to class object that runs the function
            "job_id": Unique id of the job
            "function": function to run
            "arguments": arguments the pass to the function, in a list
            "duration": How often the job should be run in seconds, or "always"
            "type": "task" or "carrier", depending on which it is
        }
    }

This object is stored in __self.scheduler_dict__. During this process, however, it creates another important dictionary that tracks which of these jobs should be executed not by the scheduler, but by an on_message event. This dictionary looks like: 

    {
        "message_type": [job_id_1, job_id_2,...]
    }

Where each message type in the dictionary has a list of associated job ids that should execute if a message of that type is received. This is stored in __self.on_message_routing_dict__. 

The above dictionaries are created based on the durations configured in both the addresses and the tasks configurations. 

After the __scheduler_dict__ object is created, the jobs can be scheduled with the scheduler. Jobs with a numeric duration or a duration equal to "always" are scheduled with the scheduler. Jobs with a duration that doesn't fit these categories are not scheduled. Carriers and tasks are scheduled nearly the same way, except carrier object functions expect the duration value, which is appended to their arguments field of the job scheduling. 

### Posting and Picking Up Messages from the Post Office

#### Posting Messages from Carrier to the Post Office

Carriers (see Writing a New Carrier) should have at minimum, a receive or send function. If the carrier is written to receive messages, at some point in the receive function (or in a sub-function executed by the receive function), the carrier should at some point use the __post_messages__ function of the system object to drop the messages off at the post office. The function takes two arguments:

1. The message (or list of messages), in enveloped format,
2. The name of the address the message is being sent on 

To envelope the message, the carriers can either implement the enveloping format around the message themselves, or they can use the envelope_message function of the system object. The __envelope_message__ function takes two arguments:

1. The raw message (in a dictionary format)
2. The address associated with the message 

This function uses the message field information to try and envelope the message. However, any envelope information can be overriden by the handler, which is often useful if the raw data is not in the correct format yet or if the message keeps track of the reading time separately from the system receipt. 

The envelope_message function:
* Uses the message id_field information to get the message id
* Uses the current time in UTC to populate the time field
* Uses the message type from the address to populate the message type field
* Puts the passed message into the "msg_content" field 

TODO: Add envelope code example 

When the enveloped message(s) is/are posted along with the address via the "post_messages" function, the following occurs:

* All messages are run through their configured handler, if they have one. The handler may make changes to the time field or id field, depending on how it parses content 
* The message is added to the message table in the system. This "stamps" the message, added the "latest_entry_id" field to the envelope structure. The latest entry id is also updated in the internal message table structure. 
* The message is checked for any "on_message" triggers that need to be executed if that particular message is received. Those triggers are then executed. 

#### Picking Up Messages from the Post Office to the Carrier
The carrier picks up post office messages via the __pickup_messages__ function. This function takes in the address name, and can optionally take in a keyword argument of __entry_ids__. The entry_ids are a list of entry ids in the message table (and in the stamped message envelope). This is a useful argument for on_message carrier triggers, as it allows them to only pick up the new message. When this keyword is not supplied, all messages corresponding to the address are picked up and returned as a list. 

#### Importing the System Object

For carrier to use the system object, the carrier needs to import the system object: 

    import system_object 


Then the carrier will need to reference the functions on the system attribute of the system object, like:

    system_object.system.pickup_messages(address_name)


## Running Tests 
Test are generally stored in the __tests__ folder and are name test_<speficic_item_tested>.py 

The recommended way to run tests is by invoking them from the root of the scarecro folder: 

    python3 tests/example_test.py 

## Configurations
TODO: Link to all the configuration READMEs. 
TODO: Make sure you note inheritance and keyword substitution. 

## Writing a New Carrier

At the most basic level, a carrier is a python class with 2 required functions: 

* an init function, which is called when a new instance of the class is made 

* Either a __send__ function, or a __receive__ function, or both, depending on what the carrier class is capable of. 

Outside of whatever the named carrier class is, there should be a return_object function that takes in the same init functions as the carrier (described later) and returns an instance of the carrier class. 

### The code file
The code file should have 
* imports, including (most likely) the import of the system object 
* The class stucture 
* The return object function, returning an instance of the object 

### The imports
A developer will likely have their own code-specific imports, but most likely they will also be importing the system object to post and/or pickup messages. This import looks like: 

    #This line moves the system path up a directory 
    sys.path.append("../scarecro")
    import system_object


### The class structure 
The class can be named whatever you want in python. For example, the top level class declaration for the 433 MHz carrier looks like: 

    class Radio_433():

### The init function 
The init function for a carrier will always take in 4 arguments, which are passed in by the system: 

    def __init__(self, config, send_addresses, receive_addresses, message_configs):

These 4 arguments are:

* config: The configuration for the carrier, passed in as the configuration dictionary 
* send_addresses: A dictionary of addresses that this carrier should be sending messages on, or an empty dictionary if there are no addresses for this function. This dictionary takes the form:

    {
        address_name: address_config 
    }

* receive addresses: A dictionary of addresses that this carrier should be receiving messages on, or an empty dictionary if there are no addresses for this function. This dictionary also takes the form: 

    {
        address_name: address_config 
    } 

* message_configs: A dicionary of message configs indexed by message name. This contains all messages used by either send or receive addresses. It takes the form: 

    {
        message_type: message_config 
    }

The init function of a carrier would typically store all these variables in its own class variable for use by the carrier. As a __tip__, most carriers also want to make some sort of address mapping lookup table based on the messages they receive or send. This mapping information is usually defined somewhere in the address config, and allows the carrier to somehow tie the messages it receives on whatever protocol it uses to a specific address. 

For example, here is the init function for the 433 MHz carrier: 

    def __init__(self, config, send_addresses, receive_addresses, message_configs):
            """
            This driver doesn't really need anything configuration-wise
            String matches and drivers are provided on an address level 
            """
            #For mongo, need to know if gateway or middle agent
            #Because gateways use slightly outdated version. 
            self.config = config.copy()
            self.send_addresses = send_addresses.copy()
            self.receive_addresses = receive_addresses.copy()
            self.message_configs = message_configs.copy()
            self.create_mappings()
            self.cmd = ['/usr/local/bin/rtl_433', '-q', '-M', 'level', '-F', 'json']

You can see that the actual carrier config doesn't contain a lot of info for this carrier. Often, for a carrier, the carrier config will contain remote connection info like a username/password. 

However, the carrier init function copies all the init arguments to it's own class variables. It also has a subprocess command it uses as a class variable. In it's init function, it runs a create_mappings() function will ties the string match information provided on the address level to info it will receive in it's SDR stream. The create_mappings() function looks like: 

    def create_mappings(self):
            matches_address_mapping = {}
            address_matches_mapping = {}
            driver_address_mapping = {}
            address_driver_mapping = {}

            all_addresses = {**self.send_addresses, **self.receive_addresses}
            for address_name, address_config in all_addresses.items():
                add_info = address_config.get("additional_info", {})
                string_matches = add_info.get("string_matches", [])
                driver = add_info.get("driver", None)
                driver_address_mapping[driver] = address_name
                address_driver_mapping[address_name] = driver
                for match in string_matches:
                    matches_address_mapping[match] = address_name
                address_matches_mapping[address_name] = string_matches
            self.matches_address_mapping = matches_address_mapping
            self.address_matches_mapping = address_matches_mapping
            self.driver_address_mapping = driver_address_mapping
            self.address_driver_mapping = address_driver_mapping

In the additional_info section of the address, this carrier expects a "string_matches" field which allows it to tie this address to stream information. It creates these ties from address to string match and from string match to address. It also matches the "driver" field of the address to the driver command argument it will need to use when initializing the SDR listen stream. 

### The recieve function 
The receive function takes in 2 arguments:
* __address_names__: A list of address names 

### Documenting a New Carrier 

* send/receive function or both and the supported durations for all 
* 

## Writing a New Handler

### Documenting a New Handler 

## Writing a New Task 

### Documenting a New Task 

## Currently implemented 
### Currently implemented carriers