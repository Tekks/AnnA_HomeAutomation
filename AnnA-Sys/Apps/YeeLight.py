#!/usr/local/bin/python

import time, os
import datetime
import paho.mqtt.client as mqtt
from termcolor import colored
import json
from yeelight import Bulb


def log(status,message,color):
  print("[ " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +" ][ " + colored(status,color) + " ]: " + message)


os.system('clear') 
log("SYSTEM","Starting",'blue')
log("SYSTEM","Setting DataProvider",'blue')


def on_connect(client, userdata, flags, rc):
    client.subscribe('anna/Systems/YeeLights')
    log("SYSTEM","MQTT Connected",'blue')


def mqttQuery(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    bulb = Bulb(str(data["device"].replace('[', '').replace(']', '')))
    hsv = int(float(data["colorCode"].split(",")[0]))
    sat = int(float(data["colorCode"].split(",")[1]))
    val = int(float(data["colorCode"].split(",")[2]))

    if (val == 0):
        bulb.turn_off()
    else:
        bulb.turn_on()
        bulb.set_hsv(hsv, sat, val)
    
    log("MQTTTX",str(str(data["device"].replace('[', '').replace(']', '')) + " >> " + data["colorCode"] ),'green')


try:
    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = mqttQuery
    client.username_pw_set("anna-sys-yeelight", "{{{MQTT_PASSWORD}}}")
    client.connect("10.10.10.10", 11883, 60)
    client.loop_forever()
except KeyboardInterrupt:
    pass
finally:
    print("Exit")