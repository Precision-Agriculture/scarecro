from datetime import datetime, timedelta, tzinfo
from datetime import timezone
from datetime import date
import pytz
from dateutil import tz 
import logging 



class SwitchdocSensors:
    """
    This class uses information from Switchdoc Labs to parse 
    sensor information 
    """
    def __init__(self, config={}, send_addresses={}, receive_addresses={}, message_configs={}):
        #These are optional - if your program needs them 
        """
        Takes in: a configuration dictionary for this handler,
        A dictionary of addresses for the handler for sending, (dictionary?)
        A dictionary of addresses for the handler for receiving (dictionary?), 
        A dictionary of message definitions indicated in the addresses 
        """
        self.config = config.copy()
        self.send_addresses = send_addresses.copy()
        self.receive_addresses = receive_addresses.copy()
        self.message_definitions = message_configs.copy()
        logging.info("Initialized switchdoc sensors handler")
    

    def envelope_id_override(self, message_envelope, message_content): 
        message_def = self.message_definitions.get(message_envelope.get("msg_type", None), {})
        message_envelope["msg_content"] = message_content
        message_envelope["msg_id"] = message_content.get(message_def.get("id_field", "id"), "default")
        message_envelope["msg_time"] = message_content.get(message_def.get("time_field", "time"), "default")
        return message_envelope


    def parse_weather_rack(self, raw_var): 
        """
        Function takes in raw weather rack packet and returns
        A clean weather rack packet 
        Taken from original SDL code 
        """
        data_dict = {}
        #First, get time data into 
        #Need timezone eventually to be CONFIGURABLE I think 
        get_time = datetime.strptime(raw_var['time'], "%Y-%m-%d %H:%M:%S")
        time_utc = get_time.astimezone(pytz.UTC)
        time_utc = time_utc.replace(tzinfo=timezone.utc)
        data_dict['time'] = time_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")
        #Now model field
        data_dict['model'] = raw_var["model"]
        #Device Field
        data_dict['device'] = raw_var['device']
        #get the ID next 
        data_dict["id"] = raw_var["id"]
        #battery field:
        data_dict['batterylow'] = raw_var['batterylow']
        #average wind speed
        aveWind = raw_var['avewindspeed']
        if aveWind > 500.0 or aveWind < 0.0:
            data_dict["error"] = 'Invalid Average Wind Speed Value '
            return data_dict
        data_dict['avewindspeed'] = round(aveWind/10.0,1)
        #gust windspeed
        gustWind = raw_var['gustwindspeed']
        if gustWind > 500.0 or gustWind < 0.0:
            data_dict["error"] = 'Invalid Gust Wind Speed Value '
            return data_dict
        data_dict['gustwindspeed'] = round(gustWind/10.0,1)
        #wind direction
        data_dict['winddirection'] = raw_var['winddirection']
        #cumulative rain 
        cumulRain = raw_var['cumulativerain']
        if cumulRain > 65535.0 or cumulRain < 0.0:
            data_dict["error"] = 'Invalid Cumulative Rain Value '
            return data_dict
        data_dict['cumulativerain'] = round(cumulRain/10.0,1)
        #Now temperature.  
        wTemp = raw_var["temperature"]
        #ALL OR NOTHING? OR PERIODIC -- ask! COMMENT HERE
        #First, deal with an errors in hex:
        if wTemp == 0x7fa or wTemp == 0x7fc or wTemp == 0x7fd:
            #MARKED - should go away later
            logging.info(f"Invalid Temperature: {wTemp}")
            #Temp invalid, Humidity invalid. 
            data_dict["error"] = "Invalid Temp Value"
            return data_dict
        #Now the conversion formula (converts value to normal decimal value)
        wTemp = (wTemp - 400)/10.0
        #Check if we still have valid reading
        if wTemp > 140.0 or wTemp < -40.0:
            #MARKED - should go away later
            logging.info(f"Invalid Temperature: {wTemp}")
            #Temp invalid, Humidity invalid. 
            data_dict["error"] = "Invalid Temp Value"
            return data_dict
        data_dict['temperature'] = round(((wTemp - 32.0)/(9.0/5.0)),2)
        #Then humidity 
        ucHumi = raw_var["humidity"]
        if ucHumi > 100.0 or ucHumi < 10.0:
            # bad humidity
            data_dict["error"] = "Invalid humidity Value"
            return data_dict
        data_dict["humidity"] = ucHumi
        #Light
        light = raw_var["light"]
        if light == 0x1fffa or light == 0x1fffb or light == 0x1fffd or light > 128000.0 or light < 0.0:
        #if light == 0x1fffa or light == 0x1fffb or light == 0x1fffd or light > 1000000.0 or light < 0.0:
            #data_dict["error"] = "Invalid lightValue"
            #return data_dict
            logging.info("Invalid light value")
        data_dict["light"] = raw_var["light"]
        #UV
        wUVI = raw_var["uv"]
        if wUVI >= 0xfa or wUVI == 0xfb or wUVI == 0xfd:
            data_dict["error"] = "Invalid UV Value"
            return data_dict
        data_dict['uv'] = round(wUVI/10.0, 1)
        #Mic
        data_dict['mic'] = raw_var['mic'] 
        #Mod
        data_dict['mod'] = raw_var['mod'] 
        #Freq
        data_dict['freq'] = raw_var['freq'] 
        #Rssi
        data_dict['rssi'] = raw_var['rssi']
        #Snr
        data_dict['snr'] = raw_var['snr']
        #Noise
        data_dict['noise'] = raw_var['noise']
        return data_dict

        #From SkyWeather2 
    def returnPercentLeftInBattery(self, currentVoltage, maxVolt):
        if(maxVolt > 12):
            returnPercent = ((currentVoltage - 11.00)/(2.6)) * 100.00
            if (returnPercent > 100.00):
                returnPercent = 100.0
            if (returnPercent < 0.0):
                returnPercent = 0.0
            return returnPercent
        else:
            scaledVolts = currentVoltage / maxVolt
            if (scaledVolts > 1.0):
                    scaledVolts = 1.0
            if (scaledVolts > .9686):
                    returnPercent = 10*(1-(1.0-scaledVolts)/(1.0-.9686))+90
                    return returnPercent
            if (scaledVolts > 0.9374):
                    returnPercent = 10*(1-(0.9686-scaledVolts)/(0.9686-0.9374))+80
                    return returnPercent
            if (scaledVolts > 0.9063):
                    returnPercent = 30*(1-(0.9374-scaledVolts)/(0.9374-0.9063))+50
                    return returnPercent
            if (scaledVolts > 0.8749):
                    returnPercent = 20*(1-(0.8749-scaledVolts)/(0.9063-0.8749))+11
                    return returnPercent
            if (scaledVolts > 0.8437):
                    returnPercent = 15*(1-(0.8437-scaledVolts)/(0.8749-0.8437))+1
                    return returnPercent
            if (scaledVolts > 0.8126):
                    returnPercent = 7*(1-(0.8126-scaledVolts)/(0.8437-0.8126))+2
                    return returnPercent
            if (scaledVolts > 0.7812):
                    returnPercent = 4*(1-(0.7812-scaledVolts)/(0.8126-0.7812))+1
                    return returnPercent
            return 0

    def twos_comp(self, val, bits):
        """compute the 2's complement of int value val"""
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val   


    def parse_solar_max(self, myState):
        """
        Function takes in raw solar max packet and returns
        A clean solar max packet 
        Taken from original SDL code 
        """
        solar_max_dict = {}
        # only accept SolarMAX2 Protocols (8,10,11)
        myProtocol = myState['weathersenseprotocol']
        if ((myProtocol == 8) or (myProtocol == 10) or (myProtocol == 11)):
            try:
                batteryPower =  float(myState["batterycurrent"])* float(myState["batteryvoltage"])/1000.0
                loadPower  =  float(myState["loadcurrent"])* float(myState["loadvoltage"])/1000.0
                solarPower =  float(myState["solarpanelcurrent"])* float(myState["solarpanelvoltage"])/1000.0
                batteryCharge = self.returnPercentLeftInBattery(myState["batteryvoltage"], 4.2)
                get_time = datetime.strptime(myState['time'], "%Y-%m-%d %H:%M:%S")
                time_utc = get_time.astimezone(pytz.UTC)
                time_utc = time_utc.replace(tzinfo=timezone.utc)
                time = time_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")
                solar_max_dict["batteryVoltage"] = float(myState["batteryvoltage"])
                solar_max_dict["batteryCurrent"] = float(myState["batterycurrent"])
                solar_max_dict["solarVoltage"] = float(myState["solarpanelvoltage"])
                solar_max_dict["solarCurrent"] = float(myState["solarpanelcurrent"])
                solar_max_dict["loadVoltage"] = float(myState["loadvoltage"])
                solar_max_dict["loadCurrent"] = float(myState["loadcurrent"])
                solar_max_dict["batteryPower"] = batteryPower 
                solar_max_dict["solarPower"] = solarPower
                solar_max_dict["loadPower"] = loadPower
                solar_max_dict["batteryCharge"] = batteryCharge
                solar_max_dict["SolarMaxInsideTemperature"] = float(myState["internaltemperature"])
                solar_max_dict["SolarMaxInsideHumidity"] = float(myState["internalhumidity"]) 
                #Changed some stuff here 
                solar_max_dict["time"] = time
                solar_max_dict["id"] = myState["deviceid"]
                #Not sure we need the following 
                solar_max_dict["protocolversion"] = myState["protocolversion"]
                solar_max_dict["softwareversion"] = myState["softwareversion"]
                solar_max_dict["weathersenseprotocol"] = myState["weathersenseprotocol"]
                solar_max_dict["auxa"] = myState["auxa"]
                solar_max_dict["messageID"] = myState["messageid"]
                logging.info(f"Solar Max Reading {solar_max_dict}")
            except Exception as e:
                logging.error("SolarMax protocol issue", exc_info=True)
        
        return solar_max_dict

    def parse_aqi(self, state): 
        """
        Function takes in raw aqi packet and returns
        A clean aqi packet 
        Taken from original SDL code 
        """
        # weathersense protocol 15
        new_dict = {}
        myProtocol = state['weathersenseprotocol']
        batteryPower =  round(float(state["batterycurrent"])* float(state["batteryvoltage"])/1000.0, 3)
        loadPower  =  round(float(state["loadcurrent"])* float(state["loadvoltage"])/1000.0, 3)
        solarPower =  round(float(state["solarpanelcurrent"])* float(state["solarpanelvoltage"])/1000.0, 3)
        batteryCharge = round(self.returnPercentLeftInBattery(state["batteryvoltage"], 4.2), 3)
        myaqi = aqi.to_aqi([
        (aqi.POLLUTANT_PM25, state['PM2.5A']),
        (aqi.POLLUTANT_PM10, state['PM10A'])
        ])
        if (myaqi > 500):
                myaqi = 500
        #MARKED
        logging.info(f"myaqi= {myaqi}")
        state['AQI'] = int(myaqi)

        new_dict["deviceid"] = state["deviceid"]
        new_dict["protocolversion"] = state["protocolversion"]
        new_dict["softwareversion"] = state["softwareversion"]
        new_dict["weathersenseprotocol"] = state["weathersenseprotocol"]
        new_dict["PM1_0S"] = state["PM1.0S"]
        new_dict["PM2_5S"] = state["PM2.5S"]
        new_dict["PM10S"] = state["PM10S"]
        new_dict["PM1_0A"] = state["PM1.0A"]
        new_dict["PM2_5A"] = state["PM2.5A"]
        #MARKED - THIS DOESN'T SEEM RIGHT
        new_dict["PM10A"] = state["PM10S"]
        new_dict["AQI"] = state["AQI"]
        new_dict["batteryvoltage"] = state["batteryvoltage"]
        new_dict["batterycurrent"] = state["batterycurrent"]
        new_dict["loadvoltage"] = state["loadvoltage"]
        new_dict["loadcurrent"] = state["loadcurrent"]
        new_dict["solarvoltage"] = state["solarpanelvoltage"]
        new_dict["solarcurrent"] = state["solarpanelcurrent"]
        new_dict["auxa"] = state["auxa"]
        new_dict["batterycharge"] = batteryCharge
        new_dict["messageID"] = state["messageid"]
        new_dict["batterypower"] = batteryPower
        new_dict["loadpower"] = loadPower
        new_dict["solarpower"] = solarPower
        #Also the time
        utc_curr_time = datetime.now(tz=pytz.UTC)
        time_string = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
        new_dict["time"] = time_string

        #MARKED
        logging.info(f"AQI reading {new_dict}")
        return new_dict


    def parse_thunder_board(self, state):
        """
        Function takes in raw thunder_board packet and returns
        A clean thunderboard packet 
        Taken from original SDL code 
        """
        # weathersense protocol 16
        new_dict = {}
        try:
                myProtocol = state['weathersenseprotocol']
                batteryPower =  float(state["batterycurrent"])* float(state["batteryvoltage"])/1000.0
                loadPower  =  float(state["loadcurrent"])* float(state["loadvoltage"])/1000.0
                solarPower =  float(state["solarpanelcurrent"])* float(state["solarpanelvoltage"])/1000.0
                batteryCharge = self.returnPercentLeftInBattery(state["batteryvoltage"], 4.2) 
                new_dict["deviceid"] = state["deviceid"]
                new_dict["protocolversion"] = state["protocolversion"]
                new_dict["softwareversion"] = state["softwareversion"]
                new_dict["weathersenseprotocol"] = state["weathersenseprotocol"]
                new_dict["irqsource"] = state['irqsource']
                new_dict["previousinterruptresult"] = state['previousinterruptresult']
                new_dict["lightninglastdistance"] = state['lightninglastdistance']
                new_dict["sparebyte"] = state['sparebyte']
                new_dict["lightningcount"] = state['lightningcount']
                new_dict["interruptcount"] = state['interruptcount']
                new_dict["batteryvoltage"] = state["batteryvoltage"]
                new_dict["batterycurrent"] = state["batterycurrent"]
                new_dict["loadvoltage"] = state["loadvoltage"]
                new_dict["loadcurrent"] = state["loadcurrent"]
                new_dict["solarvoltage"] = state["solarpanelvoltage"]
                new_dict["solarcurrent"] = state["solarpanelcurrent"]
                new_dict["auxa"] = state["auxa"]
                new_dict["batterycharge"] = batteryCharge
                new_dict["messageID"] = state["messageid"]
                new_dict["batterypower"] = batteryPower
                new_dict["loadpower"] = loadPower
                new_dict["solarpower"] = solarPower
                #Also the time
                utc_curr_time = datetime.now(tz=pytz.UTC)
                time_string = utc_curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
                print("-----------HERE-----------")
                print(time_string)
                new_dict["time"] = time_string
                logging.info(f"Thunder Board Reading: {new_dict}")
        except Exception as e:
                logging.error("Could not process Thunder Board packet", exc_info=True)
        return new_dict

    
    def parse_weather_rack_3(self, var):
        """
        Function takes in raw weather_rack_3 packet and returns
        A clean weather_rack_3 packet 
        Taken from original SDL code 
        """
        data_dict = {}
        try:
            #First, get time data into 
            get_time = datetime.strptime(var['time'], "%Y-%m-%d %H:%M:%S")
            time_utc = get_time.astimezone(pytz.UTC)
            time_utc = time_utc.replace(tzinfo=timezone.utc)
            data_dict['time'] = time_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")
            data_dict["messageid"] = var["messageid"]
            data_dict["deviceid"] = var["deviceid"]
            #Temp and humidity 
            wTemp = var["temperature"]
            #wTemp = self.twos_comp(var["temperature"], 16);
            ucHumi = var["humidity"]

            wTemp = wTemp / 10.0
            # deal with error condtions
            if (wTemp <= 140.0):
                data_dict["temperature"] = wTemp
            if (ucHumi <= 1000.0):
                # bad humidity
                data_dict["humidity"] = round(ucHumi/10.0, 1)

            #Wind, PM, Light, Misc.
            data_dict["windspeed"]= round(var["windspeed"] / 10.0, 1)
            data_dict["winddirectiondegrees"] = var["winddirectiondegrees"]
            data_dict["windforce"] = var["windforce"]
            data_dict["noise"] = round(var["noise"]/10.0, 1)
            data_dict["rain"] = round(var["rain"] / 10.0, 1)
            data_dict['mic'] = var["mic"]
            data_dict["model"] = var["model"]
            data_dict["PM2_5"] = var["PM2_5"]
            data_dict["PM10"] = var["PM10"]
            data_dict["hwlusx"] = var["hwlux"]
            data_dict["lwlux"] = var["lwlux"]
            data_dict["sunlight_visible"] = var["hwlux"] *256*256 + var["lwlux"] 
            data_dict["lightvalue20W"] = var["lightvalue20W"]
            #AQI
            try:
                myaqi = aqi.to_aqi([
                    (aqi.POLLUTANT_PM25, var['PM2_5']),
                    (aqi.POLLUTANT_PM10, var['PM10'])
                    ])
                if (myaqi > 500):
                        myaqi = 500
                data_dict["aqi"] = int(myaqi)
            except Exception as e:
                logging.info("Could not process aqi")

            #Pressure
            data_dict["pressure"] = var["pressure"]
            BarometricPressure = var["pressure"] 
            #MARKED - Check out 
            config_altitude = self.config.get("altitude", False)
            if config_altitude:
                #calculates the pressure at sealevel when given a known altitude in meters     
                BarometricPressureSeaLevel = (BarometricPressure * 100000) / pow(1.0 - config_altitude / 44330.0, 5.255)
                BarometricPressureSeaLevel = round(BarometricPressureSeaLevel / 100000, 2)
                data_dict["pressure_sea_level"] = BarometricPressureSeaLevel
            return data_dict
        except Exception as e:
            logging.error("Could not clean and build weather_rack_3", exc_info=True)
            return {}

    def parse_wr3_power(self, state):
        """
        Function takes in raw wr3_power packet and returns
        A clean raw wr3_power packet 
        Taken from original SDL code 
        """
        data_dict = {}
        try:
            data_dict = state
            data_dict["battery_power"] =  float(state["batterychargecurrent"])* float(state["batteryvoltage"])
            data_dict["load_power"]  =  float(state["loadcurrent"])* float(state["loadvoltage"])
            data_dict["solar_power"] =  float(state["solarpanelcurrent"])* float(state["solarpanelvoltage"])
            get_time = datetime.strptime(state['time'], "%Y-%m-%d %H:%M:%S")
            time_utc = get_time.astimezone(pytz.UTC)
            time_utc = time_utc.replace(tzinfo=timezone.utc)
            data_dict['time'] = time_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")
            return data_dict
        except Exception as e:
            logging.error("Could not clean and build wr3_power message", exc_info=True)
            return {} 

    def process_switchdoc_sensor_message(self, message_type, messages):
        """
        This function takes in a message_type and a list of messages
        It returns a list of messages, processed in some way 
        """
        try:
            for message in messages:
                new_message = {}
                sub_message = message.get("msg_content", {})
                if message_type == "weather_rack":
                    new_message = self.parse_weather_rack(sub_message)
                elif message_type == "solar_max": 
                    new_message = self.parse_solar_max(sub_message) 
                elif message_type == "aqi":
                    new_message = self.parse_aqi(sub_message)  
                elif message_type == "thunder_board":
                    new_message = self.parse_thunder_board(sub_message) 
                elif message_type == "weather_rack_3":
                    new_message = self.parse_weather_rack_3(sub_message) 
                elif message_type == "wr3_power":
                    new_message = self.parse_wr3_power(sub_message) 
                if new_message == {}:
                    #logging.debug(f"Error processing weather rack message")
                    return [] 
                message = self.envelope_id_override(message, new_message)
            return messages
        except Exception as e:
            logging.error(f"Could not process switchdoc sensor messages: {e}")
            return [] 
        

def return_object(config={}, send_addresses={}, receive_addresses={}, message_configs={}):
    return SwitchdocSensors(config=config, send_addresses=send_addresses, receive_addresses=receive_addresses, message_configs=message_configs)






