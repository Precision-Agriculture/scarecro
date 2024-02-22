#Need to think about this class a little bit more. 

class Communication:
    """
    Communication class for listening protocols and outward communication. 
    """
    def __init__(self, routes=[], communication_config={}):
        """
        This takes in a list of routes and the communication config and sets up the communication object. 
        """
        pass 

        self.routes = route 
        self.communication_config = communication_config

    def connect(self):
        """
        Connects to the communication scheme. Returns false 
        if the connection failed. 
        """
        return True

    def disconnect(self):
        """
        Disconnects from the communication scheme. Returns false
        if the disconnect failed. 
        """
        return True

    def reconnect(self):
        """
        Reconnects to the communication scheme, if different 
        operation from connect/disconnect
        """
        return True

    def return_connection_status(self):
        """
        Function should return True if the communication is currently connected
        And False otherwise 
        """
        return True 


     def receive(self): 
        """

        """

        pass 

    def send(self):
        """

        """

        pass 



def return_object(routes=[], communication_config={}):
    return Communication(routes=routes, communication_config=communication_config)

   

   
    

