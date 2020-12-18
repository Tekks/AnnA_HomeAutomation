#!/usr/local/bin/python

import RPi.GPIO as GPIO
import time, os
import datetime
import paho.mqtt.client as mqtt
from termcolor import colored
import json
from rpi_rf import RFDevice


def log(status,message,color):
  print("[ " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +" ][ " + colored(status,color) + " ]: " + message)


os.system('clear') 
log("System","Starting",'blue')
log("System","Setting DataProvider",'blue')


def on_connect(client, userdata, flags, rc):
    client.subscribe('anna/Systems/433mhz')
    log("System","MQTT Connected",'blue')


def mqttQuery(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    log("MQTTTX",str(data["device"]) + " -- " + str(data["code"]) ,'green')
    rfdevice = RFDevice(17)
    rfdevice.enable_tx()
    rfdevice.tx_repeat = 10
    rfdevice.tx_code(int(data["code"]), 1, 320, 24)
    rfdevice.cleanup()


try:
    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = mqttQuery
    client.username_pw_set("anna-sys-443", "{{{MQTT_PASSWORD}}}")
    client.connect("10.10.10.10", 11883, 60)
    client.loop_forever()
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()