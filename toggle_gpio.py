# tested using pip package Adafruit-GPIO
# sudo pip install Adafruit-GPIO
# examples: https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

import time
led_pin=40
led_high = True

GPIO.setmode(GPIO.BOARD)# Configure the pin counting system to board-style
                        # In this mode it's the pin of the IDC cable
#GPIO.setmode(GPIO.BCM) # Configure the pin counting to internal IO number
GPIO.setup(led_pin,GPIO.OUT)# Configure the GPIO as an output

for i in range(10):
        time.sleep(1) #sleep time in seconds
        led_high = not led_high # Toggle the pin state
        GPIO.output(led_pin, led_high) # Set the pin to high or low

        if led_high: print "Lights on!" 
        else: print "Lights off!"

# Unset the GPIO modes and clean up a bit
GPIO.cleanup(led_pin)
