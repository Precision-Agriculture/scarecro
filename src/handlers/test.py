class TestMessage:
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
    def __init__(self, config={}, send_addresses={}, receive_addresses={}, message_configs={}):
        #These are optional - if your program needs them 
        """
        Takes in: a configuration dictionary for this handler,
        A dictionary of addresses for the handler for sending, (dictionary?)
        A dictionary of addresses for the handler for receiving (dictionary?), 
        A dictionary of message definitions indicated in the addresses 
        """
        self.config = config.copy()
        self.send_addresses = send_addresses.copy()
        self.receive_addresses = receive_addresses.copy()
        self.message_definitions = message_configs.copy()
        logging.info("Initing test handler")


    def process(self, message_type, messages):
        """
        This function takes in a message_type and a list of messages
        It returns a list of messages 
        """
        for message in messages:
            sub_message = message.get("msg_content", {})
            sub_message["processed_by_fake_message_handler"] = True
        return messages 
        
    def process_out(self, message_type, messages):
        """
        This function takes in a message_type and a list of messages
        It returns a list of messages 
        """
        for message in messages:
            sub_message = message.get("msg_content", {})
            sub_message["processed_by_fake_message_handler_out"] = True
        return messages 
        


def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return TestMessage(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)
