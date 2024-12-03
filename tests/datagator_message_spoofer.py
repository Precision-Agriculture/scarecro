import time 
import logging 
import json 
import paho.mqtt.client as paho
from paho import mqtt
from datetime import datetime, timedelta, tzinfo
from datetime import timezone
from datetime import date
import pytz
from dateutil import tz 
import random 


def publish(client, topic, message):
    """
    publish the message on the topic 
    """
    qos = 1 
    return_val = False
    try:
        msgpub = client.publish(topic, json.dumps(message), qos=qos)
        print(f'MSGPUB RC: {msgpub.rc} on topic {topic}')
        if msgpub.rc != paho.MQTT_ERR_SUCCESS:
            print(f'Could not publish message {message} on topic {topic}')
            return_val = False
        else:
            return_val = True

    except Exception as e:
        print(f'Could not publish message {self.client_id}: {e}')
        return_val = False
    return return_val


def spoof_message(sensor):
    topic = False
    message = False  
    if sensor == "atlas_ezo_ph":
        topic = "atlas_ezo_ph/pH/normal/08:3A:F2:31:9B:D0"
        message = {
            "MAC": "08:3A:F2:31:9B:D0", 
            "PH": round(random.uniform(1, 3.5), 2)
            }
    elif sensor == "atlas_gravity_ph":
        topic = "atlas_gravity_ph"
        message = {
            "MAC": "24:4C:AB:08:20:E8", 
            "PH": round(random.uniform(1, 3.5), 2),
            "PH_RAW": round(random.uniform(0, 2.2), 2),
            }
    elif sensor == "datagator_ota": 
        topic = "datagator/ota_status/08:3A:F2:31:9B:D0" 
        message_1 = {
            "STATUS_MSG": "version", 
            "SERVER_FW_VERSION": "v0.3.4", 
            "DEVICE_FW_VERSION": "v0.3.3"
            }
        message_2 = {
            "STATUS_MSG": random.choice(["started", "finished"])
            }
        message = random.choice([message_1, message_2])
    elif sensor == "datagator_tlm":
        topic = "datagator/tlm/40:22:D8:66:91:F0"
        message = { 
            "MAC": "40:22:D8:66:91:F0", 
            "FIRMWARE_VERSION": "V0.4.1", 
            "RSSI": random.randint(-50, -10), 
            "BSSID": "B8:27:EB:B4:EC:CD", 
            "BATT_VOLTAGE": -1, 
            "BATT_PERCENTAGE": -1
            }
    elif sensor == "kkm_k6p":
        topic = "kkm_k6p/00"
        message = {
            "MAC": "bc:57:29:02:9e:f5", 
            "HUMIDITY": round(random.uniform(10, 70), 2), 
            "TEMP": round(random.uniform(20, 90), 2), 
            "BATT_VOLTAGE": 5134, 
            "SENSOR_NAME": "KBPro_372391", 
            "GATOR_MAC": "E0:5A:1B:18:41:A0"
        }
    elif sensor == "meter_teros10":
        depth_list = ["shallow", "middle", "deep"]
        depth_num = random.choice([0, 1, 2])
        depth = depth_list[depth_num]
        depth_topic = f"{depth_num}_{depth}"
        topic = f"meter_teros10/{depth_topic}/08:3A:F2:31:9B:D0"
        message = {
            "MAC": "08:3A:F2:31:9B:D0",
            "DEPTH": f"{depth}",
            "VMC_RAW": round(random.uniform(0, 0.5), 2),
            "VWC": round(random.uniform(0, 2), 2),
        }

    elif sensor == "mij_02_lms":
        sensor_num = random.choice([1, 2, 3])
        topic = f"mij_02_lms/{sensor_num}_dendrometer/08:3A:F2:31:9B:D0"
        message = {
            "MAC": "08:3A:F2:31:9B:D0", 
            "mij_02_lms_RAW":round(random.uniform(0, 0.5), 2), 
            "UM":round(random.uniform(50, 80), 2)
            }
    
    return topic, message 


sensor_list = [
    "atlas_ezo_ph", 
    "atlas_gravity_ph",
    "datagator_ota",
    "datagator_tlm",
    "kkm_k6p",
    "meter_teros10",
    "mij_02_lms"
]
active_sensors = [
    #"atlas_ezo_ph", 
    #"atlas_gravity_ph",
    #"datagator_ota",
    #"datagator_tlm",
    #"kkm_k6p",
    "meter_teros10",
    #"mij_02_lms"
]
mqtt_url = "127.0.0.1"
mqtt_port = 1883 
message_type = []
#If this is true, just print messages, don't send via MQTT
just_print = False 
#In seconds 
message_rate = 10
if not just_print:
    client = paho.Client(client_id="datagator_spoofer")
    client.connect(mqtt_url, port=mqtt_port)
    client.loop_start()

try:
    while True:
        for sensor in active_sensors:
            topic, message = spoof_message(sensor)
            print(f"Sending {topic}: {message}")
            if not just_print:
                try:
                    publish(client, topic, message)
                except Exception as e:
                    print(f"Couldn't send message {e}")
        print("-------------")
        time.sleep(message_rate)


except KeyboardInterrupt:
    print("Finish")
    if not just_print:
        client.loop_stop()
        client.disconnect()

#To listen - run this in terminal 
#mosquitto_sub -v -h broker_ip -p 1883 -t '#'
#The purpose of this file is to act as a test datagator
#Sensor spoofer. 
#Essentially, it will spoof messages to a local mqtt server 
#Hosted by a gateway or middle agent 

