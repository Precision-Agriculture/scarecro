import sys
import time 
import requests
import logging 
import json 
sys.path.append("../scarecro")
import system_object
import util.util as util 
#Help from the documentation here: https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#multiple

class Blynk():
    def __init__(self, config, send_addresses, receive_addresses, message_configs):
        """
        Blynk needs in its config:
            Blynk url: URL of blynk server
            Blynk auth: Authentication string for Blynk 
            (Optional) Units : English or Metric
            (Optional) Device IDs - IDs of specific devices 
        """
        #arguments passed in 
        self.config = config 
        self.send_addresses = send_addresses 
        self.receive_addresses = receive_addresses
        self.message_configs = message_configs


        #latest_message_states 
        self.device_ids = self.config.get("device_ids", {})

        #Get a lot of unit information out of the configurations
        self.units = self.config.get("units", "Metric")
        if self.units.lower() == "english":
            self.wind_speed_unit = "MPH"
            self.wind_speed_coefficient = 2.237
            self.temp_unit = "F"
            self.rain_units = "in"
            self.pressure_units = "in"
            self.pressure_coef = 0.2953
            self.sea_pressure_coef = 0.2953
            self.rain_coef = 1/25.4
        else:
            self.wind_speed_unit = "KPH"
            self.temp_unit = "C"
            self.wind_speed_coefficient = 3.6
            self.rain_units = "mm"
            self.pressure_units = "hPa"
            self.pressure_coef = 10
            self.sea_pressure_coef = 1
            self.rain_coef = 1

        self.blynk_url = self.config.get("blynk_url", None)
        self.blynk_auth = self.config.get("blynk_auth", None)
        self.request_start_string = f"{self.blynk_url}/{self.blynk_auth}" 
        self.timeout_val = self.config.get("timeout", 5)
        self.address_entry_id_dict = {}
        self.switchdoc_image_url = "http://www.switchdoc.com/SkyWeatherNoAlpha.png"

        self.sent_entries = {}
        try:
            #Do the blynk initializations
            #Rainbow
            self.update_value("V5", 0)  
            #OLED      
            self.update_value("V6", 0)
            #Flash strip
            self.update_value("V30", 0)
            #B Trend LED
            self.update_value("42", 255)
            #Lightning LED
            self.update_value("43", 255)
            #Update units buton
            if self.units.lower() == "english":
                self.update_value("V8", 0)
            else:
                self.update_value("V8", 1)
            #Artifact 
            r = requests.get(self.request_start_string+'/update/V42?color=%2300FF00', timeout=self.timeout_val)
            #Switchdoc Image Display
            self.update_url_display("V70", self.switchdoc_image_url)
            logging.info("Blynk Initialized")
        except Exception as e:
            logging.error(f"Issue initalizing blynk {e}", exc_info=True)


    def get_update_value_request_string(self, value_id, value):
        """
        Takes in a blynk value id to update and the value
        Returns a string formatted for the blynk request
        """
        return_string = f"{self.request_start_string}/update/{value_id}?value={value}"
        return return_string

    def update_value(self, value_id, value):
        """
        Takes in a blynk value id to update and the updated value 
        Creates the string and sends a request
        """
        request_string = self.get_update_value_request_string(value_id, value)
        r = requests.get(request_string, timeout=self.timeout_val)

    def CtoF(self, temperature):
        """
        Converts temperature from C to F 
        """
        return (9.0/5.0)*temperature + 32.0
    
    def returnWindDirection(self, windDirection):
        if (windDirection > 315.0+1.0):
            return "NNW"
        if (windDirection > 292.5+1.0):
            return "NW"
        if (windDirection > 270.0+1.0):
            return "WNW"
        if (windDirection > 247.5+1.0):
            return "W"
        if (windDirection > 225.0+1.0):
            return "WSW"
        if (windDirection > 202.5+1.0):
            return "SW"
        if (windDirection > 180.0+1.0):
            return "SSW"
        if (windDirection > 157.5+1.0):
            return "S"
        if (windDirection > 135.0+1.0):
            return "SSE"
        if (windDirection > 112.5+1.0):
            return "SE"
        if (windDirection > 90.0+1.0):
            return "ESE"
        if (windDirection > 67.5+1.0):
            return "E"
        if (windDirection > 45.0+1.0):
            return "ENE"
        if (windDirection > 22.5+1.0):
            return "NE"
        if (windDirection > 0.0+1.0):
            return "NNE"
        return "N"

    def update_terminal(self, terminal_id, update_string):
        """
        Function takes in a terminal id and an update 
        And posts it to the appropriate terminal 
        """
        terminal_map = {
            "V31": "status event",
            "V32": "main_terminal",
            "V75": "solar_max_line",
            "V33": "solar_terminal",
            "V44": "last_sample_time"
        }
        try:
            put_header={"Content-Type": "application/json"}
            val = update_string 
            if terminal_id == "V32" or terminal_id == "V33":
                val = f'{time.strftime("%Y-%m-%d %H:%M:%S")}: {val}'
            put_body = json.dumps([val])
            logging.debug(f"blynk Terminal Update: {terminal_map.get(terminal_id, None)} {val}")
            r = requests.put(f"{self.request_start_string}/update/{terminal_id}", data=put_body, headers=put_header, timeout=self.timeout_val)
            logging.debug(f"blynk terminal_update:POST:r.status_code: {terminal_map.get(terminal_id, None)} {r.status_code}")
        except Exception as e:
            logging.error("exception in terminal update", exc_info=True)
            
    
    def update_url_display(self, url_id, url):
        """
        Takes in a url ID and url 
        And updates the appropriate blynk button 
        """
        r = requests.get(f"{self.request_start_string}/update/{url_id}?urls={url}", timeout=self.timeout_val)
    
    def update_value_with_header(self, value_id, value):
        """
        Takes in a value id to be updated(button/slot)
        And a value
        And updates the value using the header request
        """
        put_header={"Content-Type": "application/json"}
        put_body = json.dumps([value])
        update_string = f"{self.request_start_string}/update/{value_id}"
        r = requests.put(update_string, data=put_body, headers=put_header, timeout=self.timeout_val)
        logging.debug(f"blynkEventUpdate:POST:r.status_code: {r.status_code}")


    def round_stringify_send(self, reading, value_id, key, rounding=2, multiply=1, units=None, stringify=True):
        """
        Takes in a reading, value id, a key for the reading, an
        optional number to round to, an optional muliply number, and 
        optional units to add 
        And sends the processed value via a request
        """
        value = reading.get(key, None)
        if value:
            if multiply:
                value = value*multiply
            if rounding:
                value = round(value, rounding)
            if stringify:
                value = str(value)
            if units:
                value = f"{value}{units}"
            self.update_value_with_header(value_id, value)


    def send_weather_rack(self, reading):
        """
        Takes in a reading and sends updates to blynk
        For the weather rack sensor 
        """
        #Temperature
        temperature_raw = reading.get("temperature", None)
        if temperature_raw != None:
            if self.units.lower() == "english": 
                temperature = round(self.CtoF(temperature_raw), 1)
            temperature = f"{temperature} {self.temp_unit}"
            self.update_value_with_header("V0", temperature)
            self.update_value_with_header("V10", round(temperature_raw))
        #Humidity 
        self.round_stringify_send(reading, "V1", "humidity", rounding=None)
        self.round_stringify_send(reading, "V11", "humidity", rounding=None, stringify=False)
        self.round_stringify_send(reading, "V19", "humidity", rounding=None, stringify=False)
        #Average wind speed 
        self.round_stringify_send(reading, "V9", "avewindspeed", rounding=1, multiply=self.wind_speed_coefficient, units=self.wind_speed_unit)
        #Wind Direction 
        winddirection = reading.get("winddirection", None)
        if winddirection:
            winddirection = f"{round(winddirection)} {self.returnWindDirection(winddirection)}"
            self.update_value_with_header("V2", winddirection)
        #Rain
        self.round_stringify_send(reading, "V3", "cumulativerain", rounding=2, multiply=self.rain_coef, units=self.rain_units)
        rainfall = reading.get("cumulativerain", None)
        #Sunlight 
        self.round_stringify_send(reading, "V4", "light", rounding=0)
        self.round_stringify_send(reading, "V130", "light", rounding=0)
        logging.debug("Blynk weather_rack Updated") 

    def send_aqi(self, reading):
        """
        Takes in a reading and sends updates to blynk
        For the aqi sensor 
        """
        self.round_stringify_send(reading, "V7", "AQI", rounding=None, stringify=False)
        self.round_stringify_send(reading, "V20", "AQI", rounding=None, stringify=False)
        logging.debug("Blynk AQI Updated")

    


    def send_solar_charger(self, reading): 
        """
        Takes in a reading and sends updates to blynk
        For the renogy solar charger sensor 
        """
        #First, time  
        local_time = util.convert_utc_to_local(reading["time"])
        self.update_terminal("V75", local_time)
        #Solar Voltage
        self.round_stringify_send(reading, "V50", "pv_voltage", rounding=2)
        #Solar Current
        self.round_stringify_send(reading, "V51", "pv_current", rounding=2)
        #Battery Voltage 
        self.round_stringify_send(reading, "V52", "battery_voltage", rounding=2)
        #Battery Current 
        self.round_stringify_send(reading, "V53", "charging_amp_hours_today", rounding=1)
        #Load Voltage
        self.round_stringify_send(reading, "V54", "load_voltage", rounding=2)
        #Load Current
        self.round_stringify_send(reading, "V55", "load_current", rounding=1)
        #Battery Power
        self.round_stringify_send(reading, "V60", "battery_percentage", rounding=1, units="W")
        #Solar Power 
        self.round_stringify_send(reading, "V61", "pv_power", rounding=1, units="W")
        #Load power 
        self.round_stringify_send(reading, "V62", "load_power", rounding=1, units="W")
        #Controller temperature
        self.round_stringify_send(reading, "V76", "controller_temperature", rounding=1, units=self.temp_unit)
        #Artifact
        self.update_value_with_header("V77", "0")
        #Battery Percentage 
        self.round_stringify_send(reading, "V56", "battery_percentage", rounding=1)
        self.round_stringify_send(reading, "V127", "battery_percentage", rounding=1)
        logging.debug("Blynk Solar Charger Updated")
        

    def send_bmp280(self, reading): 
        """
        Takes in a reading and sends updates to blynk
        For the bmp280 sensor 
        """
        self.round_stringify_send(reading, "V40", "BarometricPressureSeaLevel", rounding=2, multiply=self.pressure_coef, units=self.pressure_units)
        self.round_stringify_send(reading, "V41", "BarometricPressureSeaLevel", rounding=2, multiply=self.sea_pressure_coef)
        logging.debug("Blynk bmp280 Updated")     

    def disconnect(self):
        """
        In current implementation, function takes no arguments
        And only prints a message to the console. 
        """
        logging.info("Disconnect Blynk: No actions needed for Blynk disconnect in this driver.")  

    def receive(self, address_names, duration):
        """
        Receives a list of addresses (all with same duration). Depending 
        on the duration and the address, it sets itself
        up to 'receive' spoofed messages and post them
        to the system post office along with an address 
        """
        pass


    def send(self, address_names, duration, entry_ids=[]):
        """
        Takes in an optional list of entry ids
        Grabs the messages and publishes them, optionally filtering by ID 
        """
        #Send time as terminal update 
        try:
            val = time.strftime("%Y-%m-%d %H:%M:%S") 
            self.update_terminal("V44", val)
        except Exception as e:
            logging.error(f"Could not update blynk termainal: {e}", exc_info=True)

        for address_name in address_names:
            try:
                #Get the messages
                messages = system_object.system.pickup_messages(address_name, entry_ids=entry_ids)
                new_entry_ids = []
                sent_entries = self.sent_entries.get(address_name, [])
                #Send each message individually 
                for message in messages:
                    entry_id = message.get("entry_id", None)
                    new_entry_ids.append(entry_id)
                    #Send only if we haven't already sent it
                    if entry_id not in sent_entries:
                        logging.debug(f" Blynk Picking up messages for {address_name}")
                        content = message.get("msg_content", {})
                        msg_type = message.get("msg_type", None)
                        if msg_type == "weather_rack":
                            if content.get("id", None) == self.device_ids.get("weather_rack", None):
                                self.send_weather_rack(content)
                        elif msg_type == "renogy_solar_charger":
                            if content.get("deviceid", None) == self.device_ids.get("renogy_solar_charger", None):
                                self.send_solar_charger(content)
                        elif msg_type == "bmp280":
                            self.send_bmp280(content)
                        elif msg_type == "aqi":
                            self.send_aqi(content)
                self.sent_entries[address_name] = new_entry_ids
            except Exception as e:
                logging.error(f"Error updating blynk on address {address_name}; {e}", exc_info=True)

def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return Blynk(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)
