#!/bin/bash
if screen -list | grep -q "FloorLight"; then 
    echo "FloorLight RUNNING" 
else 
    echo "FloorLight STOPPED -> STARTED" 
    /usr/bin/screen -dmS FloorLight python3 /home/data/Apps/FloorLight.py
fi

if screen -list | grep -q "433mhz"; then 
    echo "433mhz RUNNING" 
else 
    echo "433mhz STOPPED -> STARTED" 
    /usr/bin/screen -dmS 433mhz python3 /home/data/Apps/433mhz.py
fi

if screen -list | grep -q "YeeLight"; then 
    echo "YeeLight RUNNING" 
else 
    echo "YeeLight STOPPED -> STARTED" 
    /usr/bin/screen -dmS YeeLight python3 /home/data/Apps/YeeLight.py
fi