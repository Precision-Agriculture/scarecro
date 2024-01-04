class DataSource:
    """
    Super class for data sources. Data sources should inherit from this class.
    For most data sources, at minimum the process function should be overridden. 

    In most cases, the init function will also be overridden.
    
    There are two different data cleaning functions, one for gateway and one for middle agent.
    Use the gateway version for cleaning that doesn't require an external internet call, and 
    the middle agent version for any cleaning that will require and external internet call. 
    In most cases, the gateway version should be sufficient. 
    
    The test function is mainly for sensors whose operations can be checked at startup to determine
    if they can be read from. In general, this is only relevant for wired sensors. 
    """
    def __init__(self, config):
        pass 

    def process(self, message, id=None):
        """
        This function takes in a message as input and returns the formatting reading. 
        The id field is optional and would generally only be used if more than one type of data source
        is wired and has no inherent ID field. 
        """
        return message 

    def data_cleaning_gateway(self, message, id=None):
        """
        This function takes in a messages as input (and optional id), formats the message, 
        and returns the reading. This function is meant to be executed only on the gateway. 
        """
        return message 

    def data_cleaning_middle_agent(self, message, id=None):
        """
        This function takes in a messages as input (and optional id), formats the message, 
        and returns the reading. This function is meant to be executed only on the middle agent. 
        """
        return message 

    def test(self, id=None):
        """
        This takes in an optional data source id and is meant to test the function of 
        the data source on startup. Generally used for a wired data source whose result
        may change listening behavior. 
        Returns True or False
        """
        return True

    def sensor_specific_task(self, id=None):
        """
        This is a mere prototype for a sensor task function. 
        Some sensors may need specific functionality, which may require the database
        or other parts of the system. Feel free to add functions here which can be run 
        by the system like other tasks. 
        """
        pass 
    