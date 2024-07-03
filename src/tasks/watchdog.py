import RPi.GPIO as GPIO
import time
import logging


#This might be better placed in the handler??? 
class Watchdog:
    """
    Watchdog class for patting the watchdog timer. 
    Configuration should include the pin the watchdog
    timer uses. 
    """
    def __init__(self, config={}):
        """
        Initializes the task with configuration provided 
        """
        self.config = config.copy()
        self.pin = self.config.get("pin", 4) 
        logging.info("Initializing a Watchdog Class") 
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
      
    def pat_the_dog():
        # pat the watchdog timer 
        logging.info("------Patting The Dog------- ")
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, False)
        time.sleep(0.2)
        GPIO.output(self.pin, True)
        GPIO.setup(self.pin, GPIO.IN)


def return_object(config):
    return Watchdog(config)