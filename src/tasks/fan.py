import time 
import os 
import subprocess
import re
import logging  


class Fan:
    """
    The fan class controls fans via configured power pins
    It expects three things in it's configuration:
    1. power_pins: a list of numeric pins that the fans are wired to
    2. fan_on_temp: The temperature, in Celsius, when the fans 
    should turn on 
    3. fan_off_temp: The temperature, in Celsius, when the fans
    should turn off 
    """
    def __init__(self, config={}):
        """
        Initializes the task with configuration provided 
        """
        self.config = config.copy()
        #Power pins - by default, 18 and 5 
        self.power_pins = self.config.get("power_pins", [18, 5])
        self.fan_on_temp = self.config.get("fan_on_temp", 37.0)
        self.fan_off_temp = self.config.get("fan_off_temp", 34.0)
        self.fans_running = False 
        self.temp_formatted = None


    def turn_on_fans(self):
        """
        Turns on all fans connected to configured
        power pins 
        """
        logging.debug(f"Turning on Fan, temp: {self.tempformatted}")
        for pin in self.power_pins: 
            try:
                command = f"pigs p {pin} 255"
                logging.debug(f"Running Command: {command}")
                os.system(command)
                self.fans_running = True 
            except Exception as e:
                logging.error(f"Could not turn on fan on pin {pin}; {e}", exc_info=True)

    def turn_off_fans(self):
        """
        Turns off all fans connected to configured
        power pins 
        """
        logging.debug(f"Turning off Fan, temp: {self.temp_formatted}")
        for pin in self.power_pins: 
            try:
                command = f"pigs p {pin} 0"
                os.system(command)
                self.fans_running = False
            except Exception as e:
                logging.error(f"Could not turn off fan on pin {pin}; {e}", exc_info=True)


    #Checks if the temp justifies the need for the fan. 
    def fan_check(self):
        try:
            logging.info("Fan Check!")
            err, pi_temp = subprocess.getstatusoutput("vcgencmd measure_temp")
            temp = re.search(r'-?\d.?\d*', pi_temp)
            self.temp_formatted = float(temp.group())
            if self.temp_formatted >= self.fan_on_temp and self.fans_running == False:
                self.turn_on_fans()
            elif self.temp_formatted <= self.fan_off_temp and self.fans_running == True:
                self.turn_off_fans
        except Exception as e:
            logging.error(f"Could not perform fan check, {e}", exc_info=True)
                
    
def return_object(config):
    return Fan(config)


