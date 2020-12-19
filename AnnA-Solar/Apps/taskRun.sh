#!/bin/bash
if screen -list | grep -q "PowerInverter01"; then 
    echo "PowerInverter01 RUNNING" 
else 
    echo "PowerInverter01 STOPPED" 
    /usr/bin/screen -dmS PowerInverter01 python3 /home/data/Apps/powerInverter.py --mqttuser anna-solar01 --collectorid s01 --serialid /dev/ttyUSB0
fi

if screen -list | grep -q "PowerInverter02"; then 
    echo "PowerInverter02 RUNNING" 
else 
    echo "PowerInverter02 STOPPED" 
    /usr/bin/screen -dmS PowerInverter02 python3 /home/data/Apps/powerInverter.py --mqttuser anna-solar02 --collectorid s02 --serialid /dev/ttyUSB1
fi