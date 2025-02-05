import time 
import os 
import logging 
import sys 
sys.path.append("../scarecro")
import system_object
import util.util as util 


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
        self.alert_emails = self.config.get("alert_emails", None) 
        self.system_id = config.get("system_id", "000")
        self.lost_connection_patience = self.config.get("system_lost_connection_patience", 2)
        logging.info("Initialized a System Maintenance Class") 
        self.system_times_without_connection = 0
        self.reboot_alerted = False 
        

    #Alert via configured email  
    #MARKED - NEEDS CONSIDERABLE CHANGES   

    def check_connection(self):
        """
        Checks the system connection status. 
        If the system has lost connection mode 
        """ 
        logging.debug("Checking system connection status")
        system_lost_connection_status = system_object.system.return_system_lost_connection()
        logging.debug(f"System lost connection status {system_lost_connection_status}")
        if system_lost_connection_status == True:
            self.system_times_without_connection += 1
        else:
            self.system_times_without_connection = 0
        logging.debug(f"System times without connection {self.system_times_without_connection}")
        if self.system_times_without_connection >= self.lost_connection_patience:
            #Send Email Alert message 
            try:
                alert_message = f'Lost connection reboot {time.strftime("%Y-%m-%d %H:%M:%S")}'
                if self.reboot_alerted == False:
                    self.alert(alert_message)
                    self.reboot_alerted = True
                #Reboot 
                self.reboot() 
            except Exception as e:
                logging.error(f"System Maintenance: Could not alert and reboot: {e}", exc_info=True)

    def reboot(self):
        """
        Function takes no arguments 
        But tries to disconnect 
        but reboots down the raspberry pi 
        """
        #In the future - may want to handle this with a message? 
        #Disconnect all carriers to ensure no lagging connections 
        #MARKED - make sure this doesn't kill our mqtt persistent connection? 
        system_object.system.disconnect_carriers()
        #Give 30 seconds to disconnect 
        time.sleep(30)
        #Reboot command 
        os.system("sudo shutdown -r")

    def alert(self, message):
        #MARKED - need to incorporate
        logging.debug(f"Alert message {message}")
        try:
            f = open("generated_data/alerts.txt", 'a+')
            f.write(message+'\n')
            f.close()
        except Exception as e:
            logging.error(f"Couldn't write alert to file", exc_info=True)
        try:
            alert_emails = self.alert_emails
            if isinstance(alert_emails, list):
                alert_list = alert_emails
            else:
                alert_list = [alert_emails]
                
            alert_string = f"Alert from {self.system_id}: {message}"
            for alert_person in alert_list:
                logging.info(f"Alerting {alert_person}")
                exec_string = "mpack -s "+ "\""+alert_string+"\" " + "generated_data/alerts.txt " + alert_person
                os.system(exec_string)
            return True
        except Exception as e:
            logging.error(f"Could not alert", exc_info=True)
            return False
    

def return_object(config):
    return SystemMaintenance(config)