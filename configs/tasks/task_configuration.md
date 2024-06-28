## Tasks
Carriers are configured with carrier specific information that
will vary substantially by the particular carrier. 

Task configurations should have similar 

source: python source code file name where the task will be implemented. 
    If you don't have a source file, you should have a name of an ALREADY-CONFIGURED carrier or handler, and the following fields
        "source_type": <carrier or handler>
        "config_name": <name of the config of the carrier or handler ALREADY TIED TO AN ADDRESS>

function: the task function to be run 

arguments: a dictionary of keyword arguments to the task function, if applicable. Can pass in an empty dictionary, otherwise. 

duration: How often a task should be run. a number in seconds, or "always" or "as_needed", or "on_message". If "on_message", you will need to be have an additional key, "message_type". 

We strongly encourage you to use a send function through a carrier rather than a task for most on_message queues, since send functions come with a notion of what messages to pickup. However, the same or similar scheme can be used by a task if necessary. 




All task object source code classes should have the following functions:

init() - the initialization function, which takes in the configuration of the task 





