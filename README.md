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

