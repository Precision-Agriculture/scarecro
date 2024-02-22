#Might kill this guy! 

class Task:
    """
    This is the task super class. 
    Tasks may import most other modules (as well as other tasks)
    to run period system functionality. Sub classes may
    add functionality.
    """
    def __init__(self):
        """
        This function is a good place to include any necessary system 
        configuration information.
        """
        pass 
  
    def run(self):
        """
        This part of the task will be actually executed by the scheduler. 
        The function should exit gracefully and in a timely manner if run periodically.
        If run forever, the task should hang. 
        """
        pass 