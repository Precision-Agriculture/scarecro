#Need to think about this class a little bit more. 

class Communication:
    """
    Communication class for listening protocols and outward communication. 
    """
    def __init__(self, config):
        """
        This sets up the communication thread as needed. 
        """
        pass 

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

    def subscribe(self, routes):
        """
        This will have the communication begin listening on some sort of route
        or routes. Returns False for failure.  
        """
        pass  


    def publish(self, routes, message):
        """
        This will have the communication publish on some sort of 
        route or routes 
        """
        pass 


    def request(self, routes, message):
        """
        Sends a request on some sort of route or routes. 
        """
        pass 
        

    def send_request_await_response(self, routes, message, timeout=60):
        """
        This sends a request and then awaits a response back. 
        """
        response = "" 
        return response  

    def return_connection_status(self):
        """
        Function should return True if the communication is currently connected
        And False otherwise 
        """
        return True 

