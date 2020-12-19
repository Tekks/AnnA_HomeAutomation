import time
import json
import lcddriver
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from threading import Thread
from termcolor import colored
from time import localtime, strftime


# Loadig Basic GPIO and LCD State
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
lcd = lcddriver.lcd()
lcd.lcd_clear()


def log(status, message, color):
    print("[ " + strftime("%Y-%m-%d %H:%M:%S", localtime()) + " ][ " + colored(status, color) + " ]: " + message)

log("System", "Initialization System", 'blue')

# Predefined GPIO Vars
OUT_LED_R = 12
OUT_LED_L = 16
OUT_LED_W = 18
OUT_MOTOR = 22
IN_SENS_R = 7
IN_SENS_L = 11
IN_SENS_U = 13
IN_SENS_O = 15
IN_SWITCH = 21

# Inputs
GPIO.setup(IN_SENS_R, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)		# GP 0 Sens R
GPIO.setup(IN_SENS_L, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)		# GP 2 Sens L
GPIO.setup(IN_SENS_U, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)		# GP 3 Sens U
GPIO.setup(IN_SENS_O, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)		# GP 12 Sens O
GPIO.setup(IN_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)		# GP 13 Schalter ON OFF
# Outputs
GPIO.setup(OUT_LED_R, GPIO.OUT, initial=GPIO.HIGH)  # GP 1 LED R
GPIO.setup(OUT_LED_L, GPIO.OUT, initial=GPIO.HIGH)  # GP 4 LED L
GPIO.setup(OUT_LED_W, GPIO.OUT, initial=GPIO.HIGH)  # GP 5 LED O
GPIO.setup(OUT_MOTOR, GPIO.OUT, initial=GPIO.HIGH)  # GP 6 Motor


# Global Const Vars
gAbfrage = 0
state = "ONLINE"
strgAbfrage = "CLOSED"
client = ""

class Vars(object):
    def __init__(self):
        self._gState = None
        self._pState = None
        self._parkingRight = None
        self._parkingLeft = None
        self._sTime = time.time()

    @property
    def gState(self):
        return self._gState

    @property
    def parkingRight(self):
        return self._parkingRight

    @property
    def parkingLeft(self):
        return self._parkingLeft

    @property
    def pState(self):
        return self._pState

    @property
    def sTime(self):
        return self._sTime

    @gState.setter
    def gState(self, value):
        self._gState = value

    @parkingRight.setter
    def parkingRight(self, value):
        self._parkingRight = value
    
    @parkingLeft.setter
    def parkingLeft(self, value):
        self._parkingLeft = value

    @pState.setter
    def pState(self, value):
        self._pState = value

    @sTime.setter
    def sTime(self, value):
        self._sTime = value

vars = Vars()
vars.gState = "CLOSED"
vars.pState = "ONLINE "


log("System", "Initialization completed", "blue")


# GPIO Controls
def out(outputport, status):
    if status == 0:
        GPIO.output(outputport, GPIO.HIGH)
    else:
        GPIO.output(outputport, GPIO.LOW)


# LCD Screen
def lcdD():
    if vars.gState == 0:
        strgAbfrage = "CLOSED"
    elif vars.gState == 1:
        strgAbfrage = "OPENED"
    else:
        strgAbfrage = "RANDOM"
    lcd.lcd_display_string(" ==== ANNA-SYS ==== ", 1)
    lcd.lcd_display_string(" System: " + vars.pState, 2)
    lcd.lcd_display_string(" State:  " + strgAbfrage, 3)
    lcd.lcd_display_string(" Time:   " + strftime("%H:%M:%S", localtime()), 4)

# Garage Engine Control
def ledOpen(tDur, state):
    tEnd = time.time() + tDur
    while(time.time() < tEnd):
        out(OUT_LED_R, 1)
        out(OUT_LED_L, 1)
        time.sleep(1)
    out(OUT_LED_R, 0)
    out(OUT_LED_L, 0)

def isr_Garage_opened(IN_SENS_O):
    if (GPIO.input(IN_SENS_U) == False and GPIO.input(IN_SENS_O)):
        vars.gState = 1
        log("MSND", "OPENED", "red")
        client.publish("anna/garage/state", "open", 0, True)
    else:
        vars.gState = 2
        log("MSND", "RANDOM", "red")

def isr_Garage_closed(IN_SENS_U):
    if (GPIO.input(IN_SENS_U) and GPIO.input(IN_SENS_O) == False):
        vars.gState = 0
        log("MSND", "CLOSED", "red")
        client.publish("anna/garage/state", "closed", 0, True)
    else:
        vars.gState = 2
        log("MSND", "RANDOM", "red")


# Parking ISR
def isr_Garage_Right(IN_SNENS_R):
    time.sleep(1)
    if (GPIO.input(IN_SENS_R)):
        vars.parkingRight = True
        log("MPSR", "TAKEN", "red")
        client.publish("anna/garage/space/right/state", "taken", 0, True)
    else:
        vars.parkingRight = False
        log("MPSR", "FREE", "red")
        client.publish("anna/garage/space/right/state", "free", 0, True)

def isr_Garage_Left(IN_SNENS_L):
    time.sleep(1)
    if (GPIO.input(IN_SENS_L)):
        vars.parkingLeft = True
        log("MPSL", "TAKEN", "red")
        client.publish("anna/garage/space/left/state", "taken", 0, True)
    else:
        vars.parkingLeft = False
        log("MPSL", "FREE", "red")
        client.publish("anna/garage/space/left/state", "free", 0, True)


# MQTT Client and Query
def on_connect(client, userdata, flags, rc):
    client.subscribe('anna/garage/cmd')
    log("System", "Conected to Anna-OH1", 'green')
    time.sleep(0.5)
    check()


def onRecive(msg):
    payload = msg.payload.decode()
    check()
    if (payload == "1" or payload == "ON" ):
        log("MRCV", "OPENED", 'green')
        if (vars.gState == 0):
            log("DOIN", "Opening", 'cyan')
            client.publish("anna/garage/state", "random", 0, True)
            time.sleep(1.5)
            out(OUT_MOTOR, 1)
            time.sleep(0.5)
            out(OUT_MOTOR, 0)
            ledOpen(30, vars.gState)
    elif (payload == "0" or payload == "OFF"):
        log("MRCV", "CLOSE", 'green')
        if (vars.gState == 1):
            log("DOIN", "Closing", 'cyan')
            client.publish("anna/garage/state", "random", 0, True)
            time.sleep(1.5)
            out(OUT_MOTOR, 1)
            time.sleep(0.5)
            out(OUT_MOTOR, 0)
            ledOpen(30, vars.gState)


def mqttQuery(client, userdata, msg):
    Thread(target=onRecive, args=[msg]).start()


def check():
    if (GPIO.input(IN_SENS_U) and GPIO.input(IN_SENS_O) == False):
        vars.gState = 0
        log("MSND", "CLOSED", "red")
        client.publish("anna/garage/state", "closed", 0, True)
    elif (GPIO.input(IN_SENS_U) == False and GPIO.input(IN_SENS_O)):
        vars.gState = 1
        log("MSND", "OPENED", "red")
        client.publish("anna/garage/state", "open", 0, True)
    else:
        vars.gState = 2
        log("MSND", "RANDOM", "red")
        client.publish("anna/garage/state", "random", 0, True)
    
    isr_Garage_Right(IN_SENS_R)
    isr_Garage_Left(IN_SENS_L)

def isr_Failure():
    if (vars.parkingLeft != GPIO.input(IN_SENS_L)):
        isr_Garage_Left(IN_SENS_L)
    if (vars.parkingRight != GPIO.input(IN_SENS_R)):
        isr_Garage_Left(IN_SENS_R)


GPIO.add_event_detect(IN_SENS_O, GPIO.RISING, callback=isr_Garage_opened, bouncetime=800)
GPIO.add_event_detect(IN_SENS_U, GPIO.RISING, callback=isr_Garage_closed, bouncetime=800)
GPIO.add_event_detect(IN_SENS_R, GPIO.BOTH, callback=isr_Garage_Right, bouncetime=800)
GPIO.add_event_detect(IN_SENS_L, GPIO.BOTH, callback=isr_Garage_Left, bouncetime=800)


def main():
    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = mqttQuery

    client.username_pw_set("anna-garage", "{{{MQTT_PASSWORD}}}")
    client.connect("10.10.10.10", 11883, 60)

    client.loop_start()

    try:
        while 1:
            while GPIO.input(IN_SWITCH):
                vars.pState = "ONLINE "
                lcdD()
                isr_Failure()
                time.sleep(1)
            while (GPIO.input(IN_SWITCH) == False):
                vars.pState = "OFFLINE"
                lcdD() 
                isr_Failure()
                time.sleep(1)
    finally:
        log("System", "Clean Exit", "red")


# Main
if __name__ == "__main__":
    main()
