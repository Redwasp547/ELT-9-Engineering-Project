############################################################
#################### IMPORT LIBRARIES ######################
############################################################
from time import sleep                     # <<< DO NOT MODIFY >>>
sleep(5) # required for stability          # <<< DO NOT MODIFY >>>

# Imports for MQTT communication           # <<< DO NOT MODIFY >>>
import network                             # <<< DO NOT MODIFY >>>
import json                                # <<< DO NOT MODIFY >>>
from umqtt.robust import MQTTClient        # <<< DO NOT MODIFY >>>

from machine import ADC, Pin, I2C
from picozero import Button
from ssd1306 import SSD1306_I2C

from math import log

# Imports the library to make a random number. This is used to
#    create a psuedo temperature value to transmit for demo
#    purposes. You don't need this library for the project.
import random

############################################################
################# SPECIFY PINS AND OBJECTS #################
############################################################

thermistor = ADC(26)

y_joystick_pin = ADC(27)
x_joystick_pin = ADC(28)
z_joystick_pin = Button(22)

display_width = 128 # pixel x values = 0 to 127
display_height = 64 # pixel y values = 0 to 63
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000) # TX pin is Pin 0, RX pin is Pin 1
display = SSD1306_I2C(display_width, display_height, i2c)

############################################################
##################### OTHER SETUP STUFF ####################
############################################################

V_in = 3.3 #[volts]
R1 = 10000 #[ohms]

start_flag = False

password = (1, 2, 3, 4)
passwordLength = 4
wait = False

r = ()

#steinhart constants
A = 1.129e-3
B = 2.341e-4
C = 8.767e-8

# Wi-Fi and MQTT settings
SSID = "WilfongEngr301" # Raspberry Pi 4 Wi-Fi name                               # <<< DO NOT MODIFY >>>
PASSWORD = "BoilerUp" # Raspberry Pi 4 Wi-Fi password, WPA/WPA2 security          # <<< DO NOT MODIFY >>>
MQTT_BROKER = "10.42.0.1"  # Raspberry Pi 4's IP                                  # <<< DO NOT MODIFY >>>
TOPIC = "pico/data" # "pico/data" is just a label                                 # <<< DO NOT MODIFY >>>
                    # It helps organize messages, like folders in a file system.  # <<< DO NOT MODIFY >>>
                    # The TOPIC could be any string, but leave it as "pico/data"  # <<< DO NOT MODIFY >>>

SENSOR_ID = "Team08"  # !!!-- CHANGE THIS AS DIRECTED BY DR. WILFONG --!!!

# Connect to Wi-Fi                                          # <<< DO NOT MODIFY >>>
wlan = network.WLAN(network.STA_IF)                         # <<< DO NOT MODIFY >>>
wlan.active(True)                                           # <<< DO NOT MODIFY >>>
wlan.config(pm = 0xa11140) # disable Wi-Fi low power mode   # <<< DO NOT MODIFY >>>
wlan.connect(SSID, PASSWORD)                                # <<< DO NOT MODIFY >>>

print("Attempting to connect to Wi-Fi")
while not wlan.isconnected():                               # <<< DO NOT MODIFY >>>
    pass                                                    # <<< DO NOT MODIFY >>>

sleep(2)  # Extra delay for stability                       # <<< DO NOT MODIFY >>>
print("Connected to Wi-Fi!")



# Connect to MQTT broker with reconnect support         # <<< DO NOT MODIFY >>>
client = MQTTClient(f"client_{SENSOR_ID}", MQTT_BROKER) # <<< DO NOT MODIFY >>>
client.DEBUG = True                                     # <<< DO NOT MODIFY >>>

# Try to connect to MQTT broker                         # <<< DO NOT MODIFY >>>
try:                                                    # <<< DO NOT MODIFY >>>
    client.connect()                                    # <<< DO NOT MODIFY >>>
    print("Connected to MQTT broker!")
except Exception as e:                                  # <<< DO NOT MODIFY >>>
    print("Failed to connect to MQTT broker:", e)

while start_flag == False:
    x_joystick = x_joystick_pin.read_u16()
    y_joystick = y_joystick_pin.read_u16()
    if len(r) == passwordLength and r == password:
        start_flag = True
    elif len(r) == passwordLength and r != password:
        r = ()

    elif wait == False:
        if x_joystick > 60000:
            r += (1,)
            wait = True
        elif y_joystick < 3000:
            r += (2,)
            wait = True
        elif y_joystick >  60000:
            r += (3,)
            wait = True
        elif x_joystick < 3000:
            r += (4,)
            wait = True
        elif y_joystick > 60000 and x_joystick > 60000:
            r += (5,)
            wait = True
        elif y_joystick > 60000 and x_joystick < 3000:
            r += (6,)
            wait = True
        elif y_joystick < 3000 and x_joystick > 60000:
            r += (7,)
            wait = True
        elif y_joystick < 3000 and x_joystick < 30000:
            r += (8,)
            wait = True
    if wait:
        if x_joystick < 38000 and y_joystick < 38000 and x_joystick > 28000 and y_joystick > 28000:
            wait = False
        


############################################################
####################### INFINITE LOOP ######################
############################################################
while True: 
    # !!!-- Psuedo temperature sensor reading between 50 and 55 --!!!
    # !!!-- You must use this variable name: temperature_sensor_reading --!!!
    # !!!-- Currently, the temperature reading is just a random number for demo purposes --!!!
    adc_value = thermistor.read_u16() #0 to 65535
    x_joystick = x_joystick_pin.read_u16()
    y_joystick = y_joystick_pin.read_u16()
    z_joystick = z_joystick_pin.is_pressed
    V_out = (V_in / 65535) * adc_value #[volts]
    Rt = (V_out * R1) / (V_in - V_out) #[ohms] thermistor resistance
    TempK = 1 / (A + (B * log(Rt)) + (C * pow(log(Rt), 3)))
    TempC = TempK - 273.15 #[Celsius]

    temperature_sensor_reading = TempC
    
    # Create and send MQTT payload                               # <<< DO NOT MODIFY >>>
    message_data = {                                             # <<< DO NOT MODIFY >>>
        "sensorID": SENSOR_ID,                                   # <<< DO NOT MODIFY >>>
        "temperatureReading": temperature_sensor_reading         # <<< DO NOT MODIFY >>>
    }                                                            # <<< DO NOT MODIFY >>>
    message_json = json.dumps(message_data)  # Convert to JSON   # <<< DO NOT MODIFY >>>
    
    # Try to publish message to MQTT broker                                    # <<< DO NOT MODIFY >>>
    try:                                                                       # <<< DO NOT MODIFY >>>
        client.publish(TOPIC, message_json, retain=True) # Send MQTT payload   # <<< DO NOT MODIFY >>>
        print(f"Published: {message_json}") # Print MQTT payload to the Shell
    except Exception as e:                                                     # <<< DO NOT MODIFY >>>
        print("Publish failed:",e)
    
    sleep(2) # Send MQTT payload every 2 seconds