import time 

class FakeTasks:
    """
    This is the task super class. 
    Tasks may import most other modules (as well as other tasks)
    to run period system functionality. Sub classes may
    add functionality.
    """
    def __init__(self, config={}):
        """
        Initializes the task with configuration provided 
        """
        self.config = config.copy()
        self.duration = self.config.get("duration", )
        print("initializing the fake task object")
  
    def giant_print(self):
        """
        Prints a big obnoxious blob of text
        """
        print("________________________________________")
        print("########################################")
        print("----------------------------------------")
        print("Hello from an obnoxious print statement!")
        print("----------------------------------------")
        print("########################################")
        print("________________________________________")
        

    def obnoxious_print(self, empty_dict):
        """
        Prints something
        If duration is forever, prints every 20 seconds 
        """
        self.giant_print()
        if self.duration == "forever":
            prev = time.time()
            curr = time.time()
            while True:
                if curr - prev > 20:
                    giant_print()
                    prev = curr 
        

def return_object(config):
    return FakeTasks(config)