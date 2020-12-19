import serial, json, time, argparse
import paho.mqtt.client as mqtt
from termcolor import colored

parser = argparse.ArgumentParser()
parser.add_argument("--mqttuser")
parser.add_argument("--collectorid")
parser.add_argument("--serialid")
args = parser.parse_args()

mqttuser = args.mqttuser
collectorid = args.collectorid
serialid = args.serialid

def log(status,message,color):
    print("[ " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +" ][ " + colored(status,color) + " ]: " + message)

log("SYSTEM","Starting",'blue')
s232 = serial.Serial(serialid, 9600, timeout=1)
s232.flushInput()
data = {"OperatingHoursCounter":"", 
        "State":0,
        "SolarCollectorsVoltage":0,
        "SolarCollectorsAmpere":0,
        "SolarCollectorsWatts":0,
        "NetworkPowerVoltage":0,
        "NetworkPowerAmpere":0,
        "NetworkPowerWatts":0,
        "InverterTemperature":0 }
client = mqtt.Client()
client.username_pw_set(mqttuser, "{{{MQTT_PASSWORD}}}")
client.connect("10.10.10.10", 11883, 60)
client.loop_start()
TFCounter = 0
while True:
    line = str(s232.readline()).replace("'","").split()
    if ( len(line) == 11 ):
        TFCounter = 0
        log( "LOGGER", str(line), "green")
        data['OperatingHoursCounter'] = line[1]
        data['State'] = int(line[2])
        data['SolarCollectorsVoltage'] = float(line[3])
        data['SolarCollectorsAmpere'] = float(line[4])
        data['SolarCollectorsWatts'] = float(line[5])
        data['NetworkPowerVoltage'] = float(line[6])
        data['NetworkPowerAmpere'] = float(line[7])
        data['NetworkPowerWatts'] = float(line[8])
        data['InverterTemperature'] = float(line[9]) 
        client.publish("anna/Systems/SolarCollectors/" + collectorid, json.dumps(data), 0, False)
        s232.flushInput()
    elif ( TFCounter >= 10 ):
        data['OperatingHoursCounter'] = "N/A"
        data['State'] = 0
        data['SolarCollectorsVoltage'] = 0
        data['SolarCollectorsAmpere'] = 0
        data['SolarCollectorsWatts'] = 0
        data['NetworkPowerVoltage'] = 0
        data['NetworkPowerAmpere'] = 0
        data['NetworkPowerWatts'] = 0
        data['InverterTemperature'] = 0
        time.sleep(10)
        client.publish("anna/Systems/SolarCollectors/" + collectorid, json.dumps(data), 0, False)
    else:
        log("RETRY ", str(TFCounter) ,"red")
        TFCounter += 1
        time.sleep(1)
s232.close()