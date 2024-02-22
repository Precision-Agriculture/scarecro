class Fake():
    def __init__(self, config, addresses, message_definitions):
        self.name = config.get("name", None)
        self.addresses = addresses 
        self.message_definitions = message_definitions
        #Make a table mapping messages to addresses?  

    #Splitting of message types will actually be up to 
    #The system logic  - might need to make that a param,
    #actually, when it comes to dealing with shared objects. 
    def receive(msg_types):
        #TODO: Have this actually generate the time, please  
        spoofed_message_content = {
            "id": "fake_id",
            "time": "now",
            "place": "here",
            "person": "you!" 
        }
        spoofed_message = {
            "msg_type": "test_message",
            "msg_id": "fake_id",
            "msg_time": spoofed_message_content["time"],
            "carrier_name": self.name,
            "msg_content": spoofed_message_content 
        }
        #Don't return anything - add it to the system message table

    def send(message_type, messages, address_name):
        #Going to get the message type from the system message table. 

        pass 

    




    
