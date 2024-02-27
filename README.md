# scarecro
The Sensor Collection and Remote Environment Care Reasoning Operation (SCARECRO) software repo

## Status
This repository is a work in progress. An initial version of SCARECRO is implemented in several test areas. We are currently in the process of refactoring the software as we release it open-source. 


## Structure of Repo
* communication
    This folder contains the classes and files for communication drivers in a system. 

* configs
    This folder contains configurations for this system. All items in the subfolders are git-ignored in order to allow customization for a particular device. It contains the following subfolders:
        * communication:
            Contains the configurations for commuication drivers (MQTT, for example)
        * data_endpoints: 
            Contains the configurations for all databases and other data endpoints (like Blynk, for example). 
        * data_sources:
            Contains the configurations for all data sources, like sensors. 
        * other
            Contains all other configurations, if necessary 

* data_endpoints
    This folder contains the classes and files for the data endpoints (most likely databases) for a given system 

* data_sources 
    This folder contains the classes and files for a given data source in the system 

* examples
    This folder contains example structures and configurations for use in the system and for testing 

* tasks
    This folder contains the classes and files for system tasks

* tests
    This folder contains system tests 

* util
    This folder contains useful functions (for instance, time conversion) that all other programs are permitted to import and use 


KEEP TRACK - I think this format is actually going to work a LOT better! 

## Stored State Messages

Messages Received by the System are stored in state with this format:  

| Message Type | Message ID | Entry ID |
| ------------ | ---------- | -------- |
| weather_rack |     21     |  101234  |


* Message Type: The type of message, usually the same name as or related to the data source in a sensor case. 


## Message Type Configurations

Message types in your system are configured with the following parameters

* Inheritance: Single name or list name of other configurations this configuration can inherit from. Inheritance can be multiple and will go from left to right, with rightmost items overriding precending. Any keys specific in the particular configuration will override others 

* id_field: (optional?) the field that identifies a specific instance of a message sender 

* time_field: (optional) the field that contains timing information for the message. By default, the system uses ISO (which standard) for all timestamps 

* class object: An object that will contain initialization and processing functions for the given message, if necessary. The object will be initialized with the message type configuration information 

* init_info: Any additional information relevant to instantiating the information 

* incoming routes - single or list of incoming route objects. See structure below. 

* outgoing routes - single or list of outgoing route objects. See structure below. 




#HOW will this work for multiple wired interfaces????? - Think through -- Might need two incoming routes with slightly different initialization info? Individual overrides - that would probably work with some more thought. For wired -- would probably work. Need to run a psuedocode practice initialization for all of these! 

### Route Object: 

Incoming Routes are dictionaries with the following formats:

* route_name: index of route (in dictionary - might need to look at this)

* function - function in the communication object this is associated with (generally send/recieve)

* communication_type: Name of a communication type configuration, which will become a communication object associated with this message 

* process_function: The name of the function associated with the class object for the message to execute if a message is received on this route. The function will receive the message in a dictionary format. It expects a (at some point...?) a message in return. 

* individual: True or False. If True, it will instantiate a unique communication object for the message in this route. If False, it may share the same communication object among messages referencing the same communication. If False - will get passed a list of communication objects 

* init_info: Any additional configuration information to pass to the communication driver, handled by the route. (I think this replaces what you have in notes as message keys)

* ??? Outgoing route - rate, on_change (messgage and device id - don't think we have to compound Id --- but possibly???)

## Notes 
* see if you can model everything else in this system this way. 




## Communication Config

* name (same as communication name?)

* driver: class name of communication driver used 

* inheritance: (Same as message)

* rate: Continuously connected, or run at a periodic rate 

* init_info: Any initialization info for the communication 

(Do I need the ability to add a publisher or route or sum'thin?)

Making a communication object - gets communication config and list of routes

Making a message object - gets message configuration 








## Instantiating Communciation 

get all the message 
see what are shared and what are individual 

## System Configuration

To configure your system, list

* the active messages in the system. This will instantiate the any attached communications listed in the incoming and outgoing routes, if any. 

* Names of the active tasks in the system 

## Configuration reserved keyworks 
'$name' replaces a field in a message name with the message name or the communication name 




## State 

* Messages in State 

* Message configurations

* Communication Objects - 

* Communciation configurations and associated messages/routes? 

* Data Store Objects (and associated messages)


Messages, Routes, and Tasks: The Building Blocks of the SCARECRO System 


## Config to State Object 

Get all messages 

Figure out individual communication objects

Figure out shared communication objects

Create unique names for unique communication object

Associate each message with a communication object

Associate each communication object with one or more messages 


* * Need to able to add, subtract, and change communciation objects and message associations on the fly, I think??? Maybe not - could also just restart. 

Keep track of these in accessible tables. 

Same with routes and communication objects, and class objects and messages? 






