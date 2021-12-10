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

__author__ = 'j323m13'
__copyright__ = 'Copyright 2021, Bullotron'
__license__ = 'Apache 2.0'
__version__ = '0.1'
__maintainer__ = 'j323m13'
__email__ = 'jeremie.equey@students.ffhs.ch'
__status__ = 'Draft'

# Global Elements
R = redis.Redis()
BTN1 = Button(pin.SW1)
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
#button1.direction = digitalio.Direction.INPUT
#button1.pull = digitalio.Pull.UP

button2 = digitalio.DigitalInOut(board.D20)
#button2.direction = digitalio.Direction.INPUT
#button2.pull = digitalio.Pull.UP


# Initialise the lcd class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows)

# Initialise default values:
interface = "" 
ip_address = ""
url = ""
externalIP_tmp = ""
externalIP = ""
view = 0
value = 0


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
    sleep(1)

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
    
    sleep(1)
    

# display fan speed
def display_fan_speed(speed):
    lcd_line_1 = "Fan speed: \n"
    lcd_line_2 = str(speed)+"%"
    lcd.message = lcd_line_1 + lcd_line_2
    sleep(1)

# display soap level
def display_soap_level(level):
    lcd_line_1 = "Soap level: \n"
    lcd_line_2 = str(level)+"%"
    lcd.message = lcd_line_1 + lcd_line_2
    sleep(1)

def redis_get(key):
    #TODO

def redis_set(key,value):
    #TODO

# wipe LCD screen before we start
lcd.clear()

#set default values
#before we start the main loop - detect active network device and ip address
sleep(2)
interface = find_interface()
ip_address = parse_ip() 
view = 2
speed = 50
level = 50


while True:
    if button1.value:
        if view ==4:
            view =1
        else:
            view = view+1
        print(view)
        print("next menu :"+str(view))
        lcd.clear()
        sleep(.25)
    if button2.value:
        if value == 100:
            value = 0
        else:
            value = value + 10
        print("update value: "+str(value))
        lcd.clear()
        sleep(.25)

    if view==1:
        display_date_time_cpu_temp_load()
    if view==2:
        display_private_external_ip()
    if view==3:
        R.get()
        display_soap_level(level)
    if view==4:
        display_fan_speed(value)

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
    

