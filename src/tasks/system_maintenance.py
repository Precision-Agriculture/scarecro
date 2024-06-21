import time 
import os 
import logging 

class SystemMaintenance:
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
        print("Initializing a System Maintenance Class") 
        self.alert_email = self.config.get("alert_email", None) 

    #Alert via configured email  
    #MARKED - NEEDS CONSIDERABLE CHANGES               
    def alert(message):
        #MARKED - need to incorporate
        logging.debug(f"Alert message {message}")
        if state_func.check_system_dict_item_value("blynk"):
            blynk_info = state_func.check_system_dict_item_value("blynk")
            if blynk_info["use_blynk"]:
                try:
                    blynk_func.blynkTerminalUpdate(message)
                except Exception as e:
                    logging.error("Could not alert blynk", exc_info=True)
        try:
            f = open("alerts.txt", 'w')
            f.write(message+'\n')
            f.close()
        except Exception as e:
            logging.error(f"Couldn't write alert to file", exc_info=True)
        try:
            alert_email = self.alert_email
            if isinstance(alert_email, list):
                alert_list = alert_email
            else:
                alert_list = [alert_email]
                
            alert_string = "Alert from "+ state_func.check_system_dict_item_value("instance")+state_func.check_system_dict_item_value("instance_id")+ ": "+ message
            for alert_person in alert_list:
                logging.info(f"Alerting {alert_person}")
                exec_string = "mpack -s "+ "\""+alert_string+"\" " + "alerts.txt " + alert_person
                os.system(exec_string)
            return True
        except Exception as e:
            logging.error(f"Could not alert", exc_info=True)
            return False
      

        

def return_object(config):
    return SystemMaintenance(config)