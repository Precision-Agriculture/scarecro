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


## Class Diagram
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

__Handlers__: A dictionary stored in self.handlers of the form: 

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

self.carriers: TODO 

self.tasks: TODO 

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

### Sending and Receiving Messages, To/From Carriers 
TODO: Expand on this 
* envelope_message
* post_messages
* pickup_messages 


### Running Tests 


## Configurations
TODO: Link to all the configuration READMEs. 
TODO: Make sure you note inheritance and keyword substitution. 

## Writing a New Carrier

## Writing a New Handler

## Writing a New Task 