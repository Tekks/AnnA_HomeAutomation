#!/usr/local/bin/python

import RPi.GPIO as GPIO
import time, os
import datetime
import paho.mqtt.client as mqtt
from termcolor import colored
import astral
from astral.sun import sun

detectionPin = 7
switchPin = 8
movementePin = 12
locked = False
systemMode = ""

GPIO.setmode(GPIO.BOARD)
GPIO.setup(switchPin, GPIO.OUT)
GPIO.setup(movementePin, GPIO.IN)
GPIO.output(switchPin, GPIO.LOW)

def log(status,message,color):
  print("[ " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +" ][ " + colored(status,color) + " ]: " + message)

def is_time_between(begin_time, end_time, check_time=None):
    check_time = check_time or datetime.datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:
        return check_time >= begin_time or check_time <= end_time

os.system('clear') 
log("System","Starting",'blue')
log("System","Setting DataProvider",'blue')

def on_connect(client, userdata, flags, rc):
    client.subscribe('anna/Groundfloor/Floor/StairLights/cmd')
    log("System","MQTT Connected",'blue')

def rc_time (detectionPin):
    count = 0 
    GPIO.setup(detectionPin, GPIO.OUT)
    GPIO.output(detectionPin, GPIO.LOW)
    time.sleep(0.1)
    GPIO.setup(detectionPin, GPIO.IN)
    while (GPIO.input(detectionPin) == GPIO.LOW and count < 5000):
        count += 1
    return count

def switch(channel):
    if (systemMode == "2" or systemMode == 2):
        city = astral.LocationInfo(name="Oedheim", region="Germany", timezone="Europe/Berlin", latitude=49.150002, longitude=9.216600)
        s = sun(city.observer, date=datetime.date.today(), tzinfo=city.timezone)
        currentTime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2)))
        if ( s["sunrise"] > currentTime or s["sunset"] < currentTime ):
            log("LIGHT","Triggered",'green')
            GPIO.output(switchPin, GPIO.HIGH)
            time.sleep(30)
            GPIO.output(switchPin, GPIO.LOW)
        else:
            GPIO.output(switchPin, GPIO.LOW)
    if (systemMode == "1" or systemMode == 1):
        GPIO.output(switchPin, GPIO.HIGH)
    if (systemMode == "0" or systemMode == 0):
        GPIO.output(switchPin, GPIO.LOW)

def mqttQuery(client, userdata, msg):
    global systemMode
    systemMode = msg.payload.decode()
    if (systemMode == "0" or systemMode == 0):
        log("MQTT","Mode OFF",'yellow')
        GPIO.output(switchPin, GPIO.LOW)
    if (systemMode == "1" or systemMode == 1):
        log("MQTT","Mode ON",'yellow')
        GPIO.output(switchPin, GPIO.HIGH)
    if (systemMode == "2" or systemMode == 2):
        log("MQTT","Mode AUTO",'yellow')
        GPIO.output(switchPin, GPIO.LOW)

GPIO.add_event_detect(movementePin, GPIO.RISING, callback=switch)

try:
    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = mqttQuery
    client.username_pw_set("anna-sys-floorlight", "{{{MQTT_PASSWORD}}}")
    client.connect("10.10.10.10", 11883, 60)
    client.loop_forever()
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()