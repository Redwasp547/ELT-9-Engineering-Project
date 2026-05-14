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

display.fill(0) # clears display
display.text("Connecting to Hub", 0, 10) # display text starting at x=0, y=10
display.show()

############################################################
##################### OTHER SETUP STUFF ####################
############################################################

V_in = 3.3 #[volts]
R1 = 10000 #[ohms]

start_flag = False

i = 0

screen = 0

userSelect = 1

password = (1, 2, 3, 4)
passwordLength = 4
wait = False

r = ()

newPass = True

repeat = 0

timer = 0

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
#wlan = network.WLAN(network.STA_IF)                         # <<< DO NOT MODIFY >>>
#wlan.active(True)                                           # <<< DO NOT MODIFY >>>
#wlan.config(pm = 0xa11140) # disable Wi-Fi low power mode   # <<< DO NOT MODIFY >>>
#wlan.connect(SSID, PASSWORD)                                # <<< DO NOT MODIFY >>>

print("Attempting to connect to Wi-Fi")
#while not wlan.isconnected():                               # <<< DO NOT MODIFY >>>
#    pass                                                    # <<< DO NOT MODIFY >>>

sleep(2)  # Extra delay for stability                       # <<< DO NOT MODIFY >>>
print("Connected to Wi-Fi!")



# Connect to MQTT broker with reconnect support         # <<< DO NOT MODIFY >>>
#client = MQTTClient(f"client_{SENSOR_ID}", MQTT_BROKER) # <<< DO NOT MODIFY >>>
#client.DEBUG = True                                     # <<< DO NOT MODIFY >>>

# Try to connect to MQTT broker                         # <<< DO NOT MODIFY >>>
#try:                                                    # <<< DO NOT MODIFY >>>
#    client.connect()                                    # <<< DO NOT MODIFY >>>
#    print("Connected to MQTT broker!")
#except Exception as e:                                  # <<< DO NOT MODIFY >>>
#    print("Failed to connect to MQTT broker:", e)

print("enter password")
while start_flag == False:
    display.fill(0) # clears display
    display.text("Enter Password", 0, 10) # display text starting at x=0, y=10
    display.show()
    
    x_joystick = x_joystick_pin.read_u16()
    y_joystick = y_joystick_pin.read_u16()
    
    if len(r) == passwordLength and r == password:
        start_flag = True
        display.fill(0) # clears display
        display.text("Correct password", 0, 10) # display text starting at x=0, y=10
        display.show()
        sleep(1)
    elif len(r) == passwordLength and r != password:
        r = ()
        print("incorrect")
        display.fill(0) # clears display
        display.text("Wrong password", 0, 10)
        display.text("Please wait 15 secs", 0, 20)# display text starting at x=0, y=10
        display.show()
        sleep(0)
    
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
    sleep(.1)
        


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
    
    if userSelect == 1 and screen == 0 and wait == False:
        display.fill(0) # clears display
        display.text("-> Display Temp", 0, 10)
        display.text("   Change Pass", 0, 20)
        display.text("   Lock Screen", 0, 30)# display text starting at x=0, y=10
        display.show()
        if z_joystick == True:
            screen = 1
            wait = True
    if userSelect == 0 and screen == 0 and wait == False:
        display.fill(0) # clears display
        display.text("   Display Temp", 0, 10)
        display.text("-> Change Pass", 0, 20)
        display.text("   Lock Screen", 0, 30)# display text starting at x=0, y=10
        display.show()
        if z_joystick == True:
            screen = 2
            wait = True
    if userSelect == -1 and screen == 0 and wait == False:
        display.fill(0) # clears display
        display.text("   Display Temp", 0, 10)
        display.text("   Change Pass", 0, 20)
        display.text("-> Lock Screen", 0, 30)# display text starting at x=0, y=10
        display.show()
        if z_joystick == True:
            screen = 3
            wait = True
    if userSelect == 1 and screen == 1 and wait == False:
        display.fill(0) # clears display
        display.text(str(TempC), 0, 10)
        display.text("-> Go Back", 0, 20)# display text starting at x=0, y=10
        display.show()
        if z_joystick == True:
            screen = 0
            wait = True
    if userSelect == 0 and screen == 2:
        r = ()
        start_flag = False
        while start_flag == False:
            display.fill(0) # clears display
            display.text("Enter old", 0, 10)
            display.text("password", 0, 20)
            display.show()
    
            x_joystick = x_joystick_pin.read_u16()
            y_joystick = y_joystick_pin.read_u16()
    
            if len(r) == passwordLength and r == password:
                start_flag = True
                display.fill(0) # clears display
                display.text("Correct password", 0, 10) # display text starting at x=0, y=10
                display.show()
                sleep(1)
            elif len(r) == passwordLength and r != password:
                r = ()
                print("incorrect")
                display.fill(0) # clears display
                display.text("Wrong password", 0, 10)
                display.text("Please wait 15 secs", 0, 20)# display text starting at x=0, y=10
                display.show()
                sleep(15)
    
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
            sleep(.1)
        password = ()
        display.fill(0) # clears display
        display.text("Enter new", 0, 10)
        display.text("password", 0, 20)
        display.show()
        
        while len(password) < passwordLength:
            x_joystick = x_joystick_pin.read_u16()
            y_joystick = y_joystick_pin.read_u16()
            z_joystick = z_joystick_pin.is_pressed
            print("in while loop")
            if newPass == False:
                if x_joystick > 60000:
                    password += (1,)

                    newPass = True
                    print("1")
                elif y_joystick < 3000:
                    password += (2,)

                    newPass = True
                    print("2")
                elif y_joystick >  60000:
                    password += (3,)

                    newPass = True
                    print("3")
                elif x_joystick < 3000:
                    password += (4,)

                    newPass = True
                    print("4")
                elif y_joystick > 60000 and x_joystick > 60000:
                    password += (5,)

                    newPass = True
                    print("5")
                elif y_joystick > 60000 and x_joystick < 3000:
                    password += (6,)

                    newPass = True
                    print("6")
                elif y_joystick < 3000 and x_joystick > 60000:
                    password += (7,)

                    newPass = True
                    print("7")
                elif y_joystick < 3000 and x_joystick < 30000:
                    password += (8,)

                    newPass = True
                    print("8")
            if newPass:
                if x_joystick < 38000 and y_joystick < 38000 and x_joystick > 28000 and y_joystick > 28000:            
                    newPass = False
            print(password)
            sleep(.1)
        screen = 0
    if screen == 3:
        r = ()
        start_flag = False
#		if repeat >= 10000:
#            try:                                                                       # <<< DO NOT MODIFY >>>
#                client.publish(TOPIC, message_json, retain=True) # Send MQTT payload   # <<< DO NOT MODIFY >>>
#                print(f"Published: {message_json}") # Print MQTT payload to the Shell
#            except Exception as e:                                                     # <<< DO NOT MODIFY >>>
#                print("Publish failed:",e)
#            repeat = 0
        print("screen3")
        while start_flag == False:
            display.fill(0) # clears display
            display.text("Enter password", 0, 10)
            display.show()

            x_joystick = x_joystick_pin.read_u16()
            y_joystick = y_joystick_pin.read_u16()

            if len(r) == passwordLength and r == password:
                start_flag = True
                display.fill(0) # clears display
                display.text("Correct password", 0, 10) # display text starting at x=0, y=10
                display.show()
                sleep(1)
            elif len(r) == passwordLength and r != password:
                r = ()
                print("incorrect")
                display.fill(0) # clears display
                display.text("Wrong password", 0, 10)
                display.text("Please wait 15 secs", 0, 20)# display text starting at x=0, y=10
                display.show()
                sleep(15)

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
#			repeat += 1
            sleep(.1)
        sleep(1)
        screen = 0


    if wait == False: 
        if y_joystick > 60000 and userSelect != -1:
            userSelect -= 1
            wait = True
        elif y_joystick < 3000 and userSelect != 1:
            userSelect += 1
            wait = True
    elif wait:
        if x_joystick < 38000 and y_joystick < 38000 and x_joystick > 28000 and y_joystick > 28000 and z_joystick == False:
            wait = False
    

    # Create and send MQTT payload                               # <<< DO NOT MODIFY >>>
#    message_data = {                                             # <<< DO NOT MODIFY >>>
#        "sensorID": SENSOR_ID,                                   # <<< DO NOT MODIFY >>>
#        "temperatureReading": temperature_sensor_reading         # <<< DO NOT MODIFY >>>
#    }                                                            # <<< DO NOT MODIFY >>>
#    message_json = json.dumps(message_data)  # Convert to JSON   # <<< DO NOT MODIFY >>>
    
    # Try to publish message to MQTT broker                                    # <<< DO NOT MODIFY >>>
    if repeat == 100:
#        try:                                                                       # <<< DO NOT MODIFY >>>
#            client.publish(TOPIC, message_json, retain=True) # Send MQTT payload   # <<< DO NOT MODIFY >>>
#            print(f"Published: {message_json}") # Print MQTT payload to the Shell
#        except Exception as e:                                                     # <<< DO NOT MODIFY >>>
#            print("Publish failed:",e)
        repeat = 0
    repeat += 1

    if timer >= 10000:
        timer = 0
        r = ()
        while start_flag == False:
            display.fill(0) # clears display
            display.text("Enter Password", 0, 10) # display text starting at x=0, y=10
            display.show()
            adc_value = thermistor.read_u16()
            x_joystick = x_joystick_pin.read_u16()
            y_joystick = y_joystick_pin.read_u16()
            V_out = (V_in / 65535) * adc_value #[volts]
            Rt = (V_out * R1) / (V_in - V_out) #[ohms] thermistor resistance
            TempK = 1 / (A + (B * log(Rt)) + (C * pow(log(Rt), 3)))
            TempC = TempK - 273.15 #[Celsius]
            print(TempC)
    
            if len(r) == passwordLength and r == password:
                start_flag = True
                display.fill(0) # clears display
                display.text("Correct password", 0, 10) # display text starting at x=0, y=10
                display.show()
                sleep(1)
            elif len(r) == passwordLength and r != password:
                r = ()
                print("incorrect")
                display.fill(0) # clears display
                display.text("Wrong password", 0, 10)
                display.text("Please wait 15 secs", 0, 20)# display text starting at x=0, y=10
                display.show()
                sleep(15)
    
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

            
    timer += 1
    
    
    sleep(.1) # Send MQTT payload every 10 seconds


