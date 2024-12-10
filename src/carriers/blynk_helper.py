key_value_dict = {
    "V30": "flash_strip", #(0-1?),
    "V6": "oled", #(1 for on, 0 off)
    "V5": "rainbow", #0 or 1?,
    "V42": "b_trend", #LED - pressyre?
    "V43": "lightning", #LED,
    "V8": "units": #0 or 1 English or Metric
    "V31": "status", #0 or 1??? 
    "V32": "terminal_update", #String that foes to terminal 
    "V75": "solar_packet", #Also a string
    "V33": "?? - Solar Terminal but can't find", #String?
    "V70": "photo", #photo url or value 
    "V44": "last_sample_time", #string
    "V7": "air_quality", #I think from bmp280? indoor?
    "V20": "air_quality_graph_trace",
    "V0": "temperature", 
    "V10": "temperature_graph_trace",
    "V1": "humidity",
    "V11": "?? - supposed to be humidity also",
    "V9": "wind_speed",
    "V19": "?? wind or humidity",

}

#Not sure this is worth doing?? 

#Get
#Post Value 
#Post string -- 




def returnWindSpeedUnit():
	blynk_info = state_func.check_system_dict_item_value("blynk")
	if (blynk_info["English_Metric"] == True):
		# return Metric 
		return "KPH"
	else:
		return  "MPH"

def returnWindSpeed(wind):
	blynk_info = state_func.check_system_dict_item_value("blynk")
	if (blynk_info["English_Metric"] == True):
		# return Metric 
		return wind*3.6
	else:
		return wind*2.237

def returnWindDirection(windDirection):
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


def returnTemperatureCF(temperature):
    blynk_info = state_func.check_system_dict_item_value("blynk")
    if (blynk_info["English_Metric"] == True):
        # return Metric 
        return temperature
    else:
        return (9.0/5.0)*temperature + 32.0

def returnTemperatureCFUnit():
    blynk_info = state_func.check_system_dict_item_value("blynk")
    if (blynk_info["English_Metric"] == True):
        # return Metric 
        return "C"
    else:
        return  "F"



def blynkInit():
    # initalize button states
    blynk_info = state_func.check_system_dict_item_value("blynk")
    blynk_start_string = blynk_info["blynk_url"]+blynk_info["blynk_auth"]
    try:
        if (blynk_info["debug_blynk"]):
            logging.info("Entering blynkInit:")

        r = requests.get(blynk_start_string+'/update/V5?value=0', timeout=timeout_val)
        if (runOLED == True):
            r = requests.get(blynk_start_string+'/update/V6?value=1', timeout=timeout_val)
        else:        
            r = requests.get(blynk_start_string+'/update/V6?value=0', timeout=timeout_val)
        r = requests.get(blynk_start_string+'/update/V30?value=0', timeout=timeout_val)
        # initialize LEDs
        r = requests.get(blynk_start_string+'/update/V42?value=255', timeout=timeout_val)
        r = requests.get(blynk_start_string+'/update/V43?value=255', timeout=timeout_val)

        if (blynk_info["debug_blynk"]):
            logging.info(f'blynk_info[\"English_Metric\"] = {blynk_info["English_Metric"]}')
        if (blynk_info["English_Metric"] == 0):
            r = requests.get(blynk_start_string+'/update/V8?value=0', timeout=timeout_val)
        else:        
            r = requests.get(blynk_start_string+'/update/V8?value=1', timeout=timeout_val)

        if (blynk_info["debug_blynk"]):
            logging.info("Exiting blynkInit:")

    except Exception as e:
        logging.error("exception in blynkInit", exc_info=True)
        return 0


def blynkEventUpdate(Event):
    blynk_info = state_func.check_system_dict_item_value("blynk")
    blynk_start_string = blynk_info["blynk_url"]+blynk_info["blynk_auth"]
    try:
        put_header={"Content-Type": "application/json"}
        val = Event 
        put_body = json.dumps([val])
        if (blynk_info["debug_blynk"]):
            logging.info(f"blynkEventUpdate: {val}")
        r = requests.put(blynk_start_string+'/update/V31', data=put_body, headers=put_header, timeout=timeout_val)
        if (blynk_info["debug_blynk"]):
            logging.info(f"blynkEventUpdate:POST:r.status_code: {r.status_code}")
        return 1
    except Exception as e:
        logging.error("exception in blynkEventUpdate", exc_info=True)
        return 0

def blynkTerminalUpdate(entry):
    blynk_info = state_func.check_system_dict_item_value("blynk")
    blynk_start_string = blynk_info["blynk_url"]+blynk_info["blynk_auth"]
    try:
        put_header={"Content-Type": "application/json"}

        entry = time.strftime("%Y-%m-%d %H:%M:%S")+": "+entry+"\n"
        put_body = json.dumps([entry])
        if (blynk_info["debug_blynk"]):
            logging.info(f"blynkStateUpdate:Pre:put_body: {put_body}")
        r = requests.put(blynk_start_string+'/update/V32', data=put_body, headers=put_header, timeout=timeout_val)
        if (blynk_info["debug_blynk"]):
            logging.info(f"blynkStateUpdate:POST:r.status_code: {r.status_code}")
    except Exception as e:
        logging.error("exception in blynkTerminalUpdate", exc_info=True)
        return 0

def blynkSolarMAXLine(entry):
    blynk_info = state_func.check_system_dict_item_value("blynk")
    blynk_start_string = blynk_info["blynk_url"]+blynk_info["blynk_auth"]
    try:
        put_header={"Content-Type": "application/json"}

        put_body = json.dumps([entry])
        if (blynk_info["debug_blynk"]):
            logging.info(f"blynkSolarMAXUpdate:Pre:put_body: {put_body}")
        r = requests.put(blynk_start_string+'/update/V75', data=put_body, headers=put_header, timeout=timeout_val)
        if (blynk_info["debug_blynk"]):
            logging.info(f"blynkSolarMAXUpdate:POST:r.status_code: {r.status_code}")
    except Exception as e:
        logging.error("exception in blynkSolarMAXUpdate", exc_info=True)
        return 0
    


def blynkUpdateImage():
    #Blynk.setProperty(V1, "urls", "https://image1.jpg", "https://image2.jpg");
    blynk_info = state_func.check_system_dict_item_value("blynk")
    blynk_start_string = blynk_info["blynk_url"]+blynk_info["blynk_auth"]
    try:
        if (blynk_info["debug_blynk"]):
                logging.info(f"blynkUpdateImage:started")
        """
        r = requests.get(blynk_start_string+'/update/V70?value=2') # Picture URL
        if (blynk_info["debug_blynk"]):
                print "blynkUpdateImage:OTHER:r.status_code:",r.status_code
        #r = requests.get(blynk_start_string+'/update/V70?urls=http://www.switchdoc.com/2.jpg') # Picture URL
        #r = requests.get(blynk_start_string+'/update/V70?urls=http://www.switchdoc.com/skycamera.jpg,http://www.switchdoc.com/2.jpg') # Picture URL
        r = requests.get(blynk_start_string+'/update/V70?value=1;url=http://www.switchdoc.com/skycamera.jpg')
        if (blynk_info["debug_blynk"]):
                print "blynkUpdateImage:OTHER:r.status_code:",r.status_code
        r = requests.get(blynk_start_string+'/update/V70?value=2;url=http://www.switchdoc.com/2.jpg') # Picture URL
        if (blynk_info["debug_blynk"]):
                print "blynkUpdateImage:OTHER:r.status_code:",r.status_code

        r = requests.get(blynk_start_string+'/update/V70?value=2') # Picture URL
        if (blynk_info["debug_blynk"]):
                print "blynkUpdateImage:OTHER:r.status_code:",r.status_code
        """
        r = requests.get(blynk_start_string+'/update/V70?urls=http://www.switchdoc.com/SkyWeatherNoAlpha.png', timeout=timeout_val) # Picture URL

    except Exception as e:
        logging.error("exception in blynkUpdateImage", exc_info=True)
        return 0

def map_renogy(message):
   new_message = {}
   new_message["batteryVoltage"] = message["battery_voltage"]
   new_message["batteryCurrent"] = message["charging_amp_hours_today"]
   new_message["solarVoltage"] = message["pv_voltage"]
   new_message["solarCurrent"] = message["pv_current"]
   new_message["loadVoltage"] = message["load_voltage"]
   new_message["loadCurrent"] = message["load_current"]
   new_message["batteryPower"] = message["battery_percentage"] #Setting 
   new_message["solarPower"] = message["pv_power"]
   new_message["loadPower"] = message["load_power"]
   new_message["batteryCharge"] = message["battery_percentage"]
   new_message["SolarMaxInsideTemperature"] = message["controller_temperature"]
   new_message["SolarMaxInsideHumidity"] = 0 #Setting
   new_message["time"] = message["time"]
   return new_message 


def blynkStateUpdate():
    logging.info("Updating Blynk")
    #We want to send the info 
    blynk_info = state_func.check_system_dict_item_value("blynk")
    blynk_start_string = blynk_info["blynk_url"]+blynk_info["blynk_auth"]
    #Then we need to get the reading we will use for the blynk ID. 
    wr_id = False 
    wr = {}
    if "blynk_wr_id" in list(blynk_info.keys()):
        wr_id = blynk_info["blynk_wr_id"]
        sensor_name = "weather_rack"
        #state_func.get_sensor_semaphore(sensor_name) #We don't get semaphores anymore since we are getting them BEFORE updating. 
        if sensor_name in state_func.get_sensor_name_list():
            instances = state_func.check_sensor_dict_item_value(sensor_name)["instances"]
            if wr_id in list(instances.keys()):
                wr = instances[wr_id].copy()
        #state_func.release_sensor_semaphore(sensor_name)

    solar_max_id = False
    solar_max = {}
    #CHANGE HERE - update for renogy 
    if "blynk_solar_max_id" in list(blynk_info.keys()):
        solar_max_id = blynk_info["blynk_solar_max_id"]
        #sensor_name = "solar_max"
        sensor_name = "renogy_solar_charger"
        
        #state_func.get_sensor_semaphore(sensor_name)
        if sensor_name in state_func.get_sensor_name_list():
            instances = state_func.check_sensor_dict_item_value(sensor_name)["instances"]
            if solar_max_id in list(instances.keys()):
                solar_max = instances[solar_max_id].copy()
                if sensor_name == "renogy_solar_charger":
                   solar_max = map_renogy(solar_max)
        #state_func.release_sensor_semaphore(sensor_name)

    bmp280_id = False
    bmp280 = {}
    if "blynk_bmp280_id" in list(blynk_info.keys()):
        bmp280_id = blynk_info["blynk_bmp280_id"]
        sensor_name = "bmp280"
        #state_func.get_sensor_semaphore(sensor_name)
        if sensor_name in state_func.get_sensor_name_list():
            instances = state_func.check_sensor_dict_item_value(sensor_name)["instances"]
            if bmp280_id in list(instances.keys()):
                bmp280 = instances[bmp280_id].copy()
        #state_func.release_sensor_semaphore(sensor_name)

    aqi_id = False
    aqi = {}
    if "blynk_aqi_id" in list(blynk_info.keys()):
        aqi_id = blynk_info["blynk_aqi_id"]
        sensor_name = "aqi"
        #state_func.get_sensor_semaphore(sensor_name)
        if sensor_name in state_func.get_sensor_name_list():
            instances = state_func.check_sensor_dict_item_value(sensor_name)["instances"]
            if aqi_id in list(instances.keys()):
                aqi = instances[aqi_id ].copy()
        #state_func.release_sensor_semaphore(sensor_name)


   
    # do not blynk if no main reading yet
    if wr !={} or solar_max != {} or bmp280 != {} or aqi != {}:
        try:
            blynkUpdateImage()
            #MARKED - can I get rid of this? 
            put_header={"Content-Type": "application/json"}

            # set last sample time 
            put_header={"Content-Type": "application/json"}
            val = time.strftime("%Y-%m-%d %H:%M:%S")  
            put_body = json.dumps([val])
            if (blynk_info["debug_blynk"]):
                logging.info(f"blynkEventUpdate: {val}")
            r = requests.put(blynk_start_string+'/update/V44', data=put_body, headers=put_header, timeout=timeout_val)
            if (blynk_info["debug_blynk"]):
                logging.info(f"blynkEventUpdate:POST:r.status_code: {r.status_code}")


            #First, AQI: 
            # do the graphs
            if aqi != {}:
                try:
                    #V7
                    val = aqi["AQI"]
                    put_body = json.dumps([val])
                    if (blynk_info["debug_blynk"]):
                        logging.info(f"blynkStateUpdate:Pre:put_body: {put_body}")
                    r = requests.put(blynk_start_string+'/update/V7', data=put_body, headers=put_header, timeout=timeout_val)
                    if (blynk_info["debug_blynk"]):
                        logging.info(f"blynkStateUpdate:POST:r.status_code:{r.status_code}")

                    # outdoor Air Quality - V20
                    val = aqi["AQI"]
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V20', data=put_body, headers=put_header, timeout=timeout_val)
                    #MARKED
                    logging.info("AQI UPDATED")
                except Exception as e:
                    logging.error("Could not update blynk with AQI", exc_info=True)
        

            if wr != {}:
                try: 
                    val = returnTemperatureCF(wr["temperature"])
                    tval = "{0:0.1f} ".format(val) + returnTemperatureCFUnit()
                    put_body = json.dumps([tval])
                    r = requests.put(blynk_start_string+'/update/V0', data=put_body, headers=put_header, timeout=timeout_val)

                    val = returnTemperatureCF(wr["temperature"])
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V10', data=put_body, headers=put_header, timeout=timeout_val)

                    val = wr["humidity"]
                    put_body = json.dumps(["{0:0.1f}%".format(val)])
                    r = requests.put(blynk_start_string+'/update/V1', data=put_body, headers=put_header, timeout=timeout_val)

                    val = wr["humidity"]
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V11', data=put_body, headers=put_header, timeout=timeout_val)

                    #"WindSpeed": "avewindspeed"
                    #wind
                    val = returnWindSpeed(wr["avewindspeed"])
                    tval = "{0:0.1f}".format(val) + returnWindSpeedUnit()
                    put_body = json.dumps([tval])
                    r = requests.put(blynk_start_string+'/update/V9', data=put_body, headers=put_header, timeout=timeout_val)

                    #now humidity
                    #val = util.returnWindSpeed(state.WindSpeed)
                    val = wr["humidity"]
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V19', data=put_body, headers=put_header, timeout=timeout_val)

                    #wind direction
                    val = "{0:0.0f}/".format(wr["winddirection"]) + returnWindDirection(wr["winddirection"])
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V2', data=put_body, headers=put_header, timeout=timeout_val)

                    #rain 
                    val = "{0:0.2f}".format(wr["cumulativerain"]) 
                    if (blynk_info["English_Metric"] == 1):
                        tval = "{0:0.2f}mm".format(wr["cumulativerain"]) 
                    else:
                        tval = "{0:0.2f}in".format(wr["cumulativerain"] / 25.4) 
                    put_body = json.dumps([tval])
                    r = requests.put(blynk_start_string+'/update/V3', data=put_body, headers=put_header, timeout=timeout_val)

                    #Sunlight 
                    val = "{0:0.0f}".format(wr["light"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V4', data=put_body, headers=put_header, timeout=timeout_val)

                    #Sunlight  for Graph
                    val = "{0:0.0f}".format(wr["light"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V130', data=put_body, headers=put_header, timeout=timeout_val)

                    #MARKED
                    logging.info("WEATHER RACK UPDATED")
                except Exception as e:
                    logging.error("Could not update blynk with weather rack info", exc_info=True)

            if bmp280 != {}:
                try: 
                    #barometric Pressure 
                    if (blynk_info["English_Metric"] == 1):
                        tval = "{0:0.2f}hPa".format(bmp280["BarometricPressureSeaLevel"]*10.0)
                    else:
                        tval = "{0:0.2f}in".format((bmp280["BarometricPressureSeaLevel"] * 0.2953)) 
                    put_body = json.dumps([tval])
                    r = requests.put(blynk_start_string+'/update/V40', data=put_body, headers=put_header, timeout=timeout_val)

                    #barometric Pressure graph
                    if (blynk_info["English_Metric"] == 1):
                        tval = "{0:0.2f}".format(bmp280["BarometricPressureSeaLevel"]) 
                    else:
                        tval = "{0:0.2f}".format((bmp280["BarometricPressureSeaLevel"] * 0.2953)) 
                    put_body = json.dumps([tval])
                    r = requests.put(blynk_start_string+'/update/V41', data=put_body, headers=put_header, timeout=timeout_val)
                    #MARKED
                    logging.info("BMP280 UPDATED")
                except Exception as e:
                    logging.error("Could not update blynk with bmp280 info", exc_info=True)

            #CHANGE HERE - make the substitutions here 
            if solar_max != {}:
                try:
                    #solar data
                    local_time = util.convert_utc_to_local(solar_max["time"])
                    blynkSolarMAXLine(local_time)
                    val = "{0:0.2f}".format(solar_max["solarVoltage"]) 
                    
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V50', data=put_body, headers=put_header, timeout=timeout_val)

                    val = "{0:0.1f}".format(solar_max["solarCurrent"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V51', data=put_body, headers=put_header, timeout=timeout_val)

                    val = "{0:0.2f}".format(solar_max["batteryVoltage"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V52', data=put_body, headers=put_header, timeout=timeout_val)

                    val = "{0:0.1f}".format(solar_max["batteryCurrent"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V53', data=put_body, headers=put_header, timeout=timeout_val)

                    val = "{0:0.2f}".format(solar_max["loadVoltage"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V54', data=put_body, headers=put_header, timeout=timeout_val)

                    val = "{0:0.1f}".format(solar_max["loadCurrent"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V55', data=put_body, headers=put_header, timeout=timeout_val)

                    val = "{0:0.1f}W".format(solar_max["batteryPower"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V60', data=put_body, headers=put_header, timeout=timeout_val)
                    
                    val = "{0:0.1f}W".format(solar_max["solarPower"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V61', data=put_body, headers=put_header, timeout=timeout_val)
                    
                    val = "{0:0.1f}W".format(solar_max["loadPower"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V62', data=put_body, headers=put_header, timeout=timeout_val)

                    val = returnTemperatureCF(solar_max["SolarMaxInsideTemperature"])
                    tval = "{0:0.1f} ".format(val) + returnTemperatureCFUnit()
                    put_body = json.dumps([tval])
                    r = requests.put(blynk_start_string+'/update/V76', data=put_body, headers=put_header, timeout=timeout_val)

                    val = "{0:0.1f}%".format(solar_max["SolarMaxInsideHumidity"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V77', data=put_body, headers=put_header, timeout=timeout_val)

                    val = "{0:0.1f}".format(solar_max["batteryCharge"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V56', data=put_body, headers=put_header, timeout=timeout_val)
            
                    val = "{0:0.1f}".format(solar_max["batteryCharge"]) 
                    put_body = json.dumps([val])
                    r = requests.put(blynk_start_string+'/update/V127', data=put_body, headers=put_header, timeout=timeout_val)
            
                    #MARKED
                    logging.info("SOLAR MAX UPDATED")
                except Exception as e:
                    logging.error(f"Could not update blynk with solar_max info") 
            
            # LEDs 
            if (barometricTrend):   #True is up, False is down
                r = requests.get(blynk_start_string+'/update/V42?color=%2300FF00', timeout=timeout_val) # Green
                if (blynk_info["debug_blynk"]):
                    logging.info(f"blynkAlarmUpdate:OTHER:r.status_code: {r.status_code}")
            else:
                r = requests.get(blynk_start_string+'/update/V42?color=%23FF0000', timeout=timeout_val) # red
                return 1
        except Exception as e:
            logging.error(f"exception in blynkStateUpdate", exc_info=True)
            return 0



    
