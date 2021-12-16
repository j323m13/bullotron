#! python
# -*- coding: utf-8 -*-

"""
The Bullotron is a automated Bubble-Machine

This File represents the Display-driving part.
This Code is licenced under the Apache License 2.0
"""

# Built-in/Generic Imports
import logging
from argparse import ArgumentParser
from time import sleep
import os
import sys
from subprocess import Popen, PIPE
from time import sleep
from datetime import datetime
import requests
import os
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
from RPi import GPIO

# Libs
from statemachine import StateMachine, State # State Machine
from gpiozero import Button
import redis

# Own modules
import pindefinitions as pin #Pins on the PCB
import redis_key_names as rediskey

__author__ = 'j323m13'
__copyright__ = 'Copyright 2021, Bullotron'
__license__ = 'Apache 2.0'
__version__ = '0.1'
__maintainer__ = 'j323m13'
__email__ = 'jeremie.equey@students.ffhs.ch'
__status__ = 'prod'

## Global Elements
R = redis.Redis()

# Modify this if you have a different sized character LCD
lcd_columns = 16
lcd_rows = 2

# compatible with all versions of RPI as of Jan. 2019
# v1 - v3B+
lcd_rs = digitalio.DigitalInOut(board.D4)
lcd_en = digitalio.DigitalInOut(board.D17)
lcd_d4 = digitalio.DigitalInOut(board.D18)
lcd_d5 = digitalio.DigitalInOut(board.D22)
lcd_d6 = digitalio.DigitalInOut(board.D23)
lcd_d7 = digitalio.DigitalInOut(board.D24)


button1 = digitalio.DigitalInOut(board.D16)
button2 = digitalio.DigitalInOut(board.D20)

# Initialise the lcd class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows)

# Initialise default values:
interface = "" 
ip_address = ""
url = ""
externalIP_tmp = ""
externalIP = ""
value = 0

# welcome message
def display_welcome():
    lcd_line_1 = "Welcome. I'am \n"
    lcd_line_2 = "Bullotron :-)"
    lcd.message = lcd_line_1 + lcd_line_2 
    sleep(0.25)

# looking for an active Ethernet or WiFi device
def find_interface():
    find_device = "ip addr show"
    interface_parse = run_cmd(find_device)
    for line in interface_parse.splitlines():
        if "state UP" in line:
            dev_name = line.split(':')[1]
    return dev_name

# find an active IP on the first LIVE network device
def parse_ip():
    find_ip = "ip addr show %s" % interface
    find_ip = "ip addr show %s" % interface
    ip_parse = run_cmd(find_ip)
    for line in ip_parse.splitlines():
        if "inet " in line:
            ip = line.split(' ')[5]
            ip = ip.split('/')[0]
    return ip


# run unix shell command, return as ASCII
def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode('ascii')

# get CPU temp
def get_CPU_temperature():
    res = os.popen("vcgencmd measure_temp").readline()
    return(res.replace("temp=","").replace("'C\n",""))

# get CPU load
def get_CPU_load():
    return str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip())

# get date and time
def get_date_and_time():
    date_time = datetime.now().strftime('%b %d  %H:%M:%S\n')
    return date_time

# display date time and cpu temperature and load
def display_date_time_cpu_temp_load():
    # date and time
    lcd_line_1 = get_date_and_time()
        
    #cpu temp and CPU load
    lcd_line_2  = "CPU:"+get_CPU_temperature()+"C "+get_CPU_load()+"%\n"
    
    # combine both lines into one update to the display
    lcd.message = lcd_line_1 + lcd_line_2
    sleep(0.25)

#get external IP
def get_external_IP(url):
    #check external IP
    externalIP = run_cmd(url)
    return externalIP

# display private and external ip 
def display_private_external_ip():
    url = "curl https://ip.me/"
    externalIP = get_external_IP(url)
    #set ip results for displaying
    lcd_line_1 = "IP "+externalIP[1:]
    lcd_line_2 = "IP "+ip_address

    # combine both lines into one update to the display
    lcd.message = lcd_line_1 + lcd_line_2
    
    sleep(0.25)
    

# display fan speed
def display_fan_speed(key):
    lcd_line_1 = "Fan speed: \n"
    fan_speed_redis = redis_get(key).decode('utf-8')
    fan_speed_redis_tmp = float(fan_speed_redis)*float(100)
    lcd_line_2 = str(int(fan_speed_redis_tmp))+" %"
    lcd.message = lcd_line_1 + lcd_line_2
    sleep(0.25)

# set blow time
def display_fan_blow_time(key):
    lcd_line_1 = "blow time: \n"
    blow_time = redis_get(key).decode('utf-8')
    lcd_line_2 = str(blow_time)+" sec."
    lcd.message = lcd_line_1 + lcd_line_2
    sleep(0.25)

# display soap level
def display_soap_level(key):
    lcd_line_1 = "Soap level: \n"
    soap_level_tmp = R.get(key).decode('utf-8')
    soap_level = int(soap_level_tmp)
    lcd_line_2 = str(soap_level)
    lcd.message = lcd_line_1 + lcd_line_2
    sleep(0.25)

# shutdown mi boi
def shutdown_bullotron(key,value):
    if(value == int(redis_get(key))):
        answer_shutdown_txt = "no"
    else:
        answer_shutdown_txt = "yes"
    lcd_line_1 = "shutdown?\n"
    lcd_line_2 = str(answer_shutdown_txt)
    lcd.message = lcd_line_1 + lcd_line_2
    sleep(0.25)
    if(answer_shutdown_txt == "yes"):
        lcd.clear()
        lcd_line_1 = "Goodbye \n"
        lcd_line_2 = "me go sleep"
        lcd.message = lcd_line_1 + lcd_line_2
        sleep(3)
        shutdown_order = "sudo shutdown now"
        lcd.clear()
        run_cmd(shutdown_order)

def get_lid_open(key):
    print(str(key))
    lcd_line_1 = "lid's opened for \n"
    lid_open_time = R.get(key).decode('utf-8')
    lcd_line_2 = str(lid_open_time)+" sec."
    print(lcd_line_2)
    lcd.message = lcd_line_1 + lcd_line_2
    sleep(0.25)

def redis_get(key):
    print(R.get(str(key)))
    return R.get(str(key))
    

def redis_set(key,value):
    print("key: "+str(key))
    print("value: "+str(value))
    R.set(str(key),str(value))
    print(R.get(str(key)))
    print("update value: "+str(value))

# wipe LCD screen before we start
lcd.clear()

#set default values
#before we start the main loop - detect active network device and ip address
interface = find_interface()
ip_address = parse_ip() 
#start view
view = 0
limit_view = 7
#debug: set value to test system without hardware
#R.set(rediskey.liquid_level,"100")
#R.set(rediskey.blowforce,"0.50")
#R.set(rediskey.blowtime,"5")
#R.set(rediskey.lid_open,"5")
#R.set(rediskey.shutdown,"0")


while True:
    if button1.value:
        if view ==limit_view:
            view =1
        else:
            view = view+1
        print(view)
        print("next menu :"+str(view))
        lcd.clear()
        sleep(.25)
    if button2.value:
        if(view==1 or view ==2 or view ==3):
            pass
        else:
            if(view==4):
                value_end = 1.0
                increment = 0.1
                value = redis_get(key)
            if(view==5 or view==6):
                value_end = 15
                increment = 5
                value = redis_get(key)
            if(view==7):
                value_end = 100
                increment = 10
                value = redis_get(key)
            if (value == value_end or float(value) > value_end-increment):
                value = 0
                redis_set(key,value)
                #redis_get(key)
            if(view==4):
                print("increment "+str(increment))
                value = float(value) + increment
                redis_set(key,value)
                #redis_get(key)
            else:
                print("increment "+str(increment))
                value = int(value) + increment
                redis_set(key,value)
                #redis_get(key)
        
        lcd.clear()
        sleep(.1)

    if view==0:
        print("Welcome view")
        display_welcome()
    if view==1:
        print("cpu and temp view")
        display_date_time_cpu_temp_load()
    if view==2:
        print("ips view")
        display_private_external_ip()
    if view==3:
        print("soapy view")
        display_soap_level(rediskey.liquid_level)
    if view==4:
        print("blow force view")
        key=rediskey.blowforce
        display_fan_speed(key)
    if view==5:
        print("blow time?")
        key=rediskey.blowtime
        display_fan_blow_time(key)
    if view==6:
        print("lid open time?")
        key=rediskey.lid_open
        get_lid_open(key)
    if view==7:
        key=rediskey.shutdown
        print("Shutdown")
        value = 0
        shutdown_bullotron(key,value)

    sleep(.25)



if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()
    

