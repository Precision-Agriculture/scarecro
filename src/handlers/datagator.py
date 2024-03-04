class DataGator:
    """
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
        print("Initing test handler")


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
    return DataGator(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)
