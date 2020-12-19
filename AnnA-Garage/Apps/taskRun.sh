#!/bin/bash
if screen -list | grep -q "Garage"; then 
    echo "Garage RUNNING" 
else 
    echo "Garage STOPPED -> STARTED" 
    /usr/bin/screen -dmS Garage python3 /home/data/Apps/GISR.py
fi