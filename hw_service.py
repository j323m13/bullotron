#! python
# -*- coding: utf-8 -*-

"""
The Bullotron is a automated Bubble-Machine

This File represents the Hardware-driving part.
This Code is licenced under the Apache License 2.0
"""

# Built-in/Generic Imports
import logging
from argparse import ArgumentParser
from time import sleep
import os
import sys



# Libs
from statemachine import StateMachine, State # State Machine
from gpiozero import Device, PWMOutputDevice, Button, DigitalOutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory
Device.pin_factory = PiGPIOFactory() #Use PiGPIO
import redis

# Own modules
import pindefinitions as pin #Pins on the PCB

__author__ = 'MajorTwip'
__copyright__ = 'Copyright 2021, Bullotron'
__license__ = 'Apache 2.0'
__version__ = '0.1'
__maintainer__ = 'MajorTwip'
__email__ = 'majortwip@gmail.com'
__status__ = 'Draft'

# Global Elements
R = redis.Redis()


FAN = PWMOutputDevice(pin.OUT1)
BTN = Button(pin.SW1,False)
RC = Button(pin.IN1)
RC_EN = DigitalOutputDevice(pin.OUT2,False)
LEVELSENS = Button(pin.IN2)

class InvertedServo(PWMOutputDevice):
    target = 0

    def set(self, level:int):
        if 0<=level<=1000:
            logging.debug("set servo to level " + str(level) + " : " + str(0.075+(level/10000)))
            self.target = level
            self.value = 0.025+(level/10000)
        else:
            logging.warning("servo-level must be between 0 and 1000")

    def fade(self,level:int):
        while not level == self.target:
            if level > self.target:
                self.target +=1
            else:
                self.target -=1
            self.set(self.target)
            sleep(0.003)

SERVO = InvertedServo(pin.SERVO,active_high=False,frequency=50)

class BullotronHW(StateMachine):
    init_hw = State('InitHW', initial=True)
    sens_fill = State('Sensing Level')
    closed = State('Lid closing')
    open_to_blow = State('Lid opening for blowing')
    blowing = State('Blowing')
    open_full = State('Fully opening')
    open_setting =State('Opening to dynamic angle') 

    init = init_hw.to(init_hw)
    close = sens_fill.to(closed) | open_to_blow.to(closed) | open_full.to(closed) | open_setting.to(closed) | blowing.to(closed)
    sense = closed.to(sens_fill) | init_hw.to(sens_fill)
    blow_cycle = closed.to(open_to_blow)
    blow = open_to_blow.to(blowing) 
    fill = closed.to(open_full)
    set_angle = closed.to(open_setting)

    def on_enter_init_hw(self):
        logging.info("Initialize Hardware")
        logging.debug("shut off fan")
        FAN.off()
        logging.debug("close lid")
        SERVO.set(int(R.get("lid_closed") or 0))
        self.sense()

    def on_enter_sens_fill(self):
        logging.info("Sensing Level")
        logging.debug("opening")      
        angle = int(R.get("lid_closed") or 0)
        stop = int(R.get("blowlevel") or 800)
        while (LEVELSENS.is_pressed and (angle < stop)):
            angle=angle+1
            SERVO.fade(angle)
            
        R.set("liquidlevel",angle)
        logging.info("sensed level:  " + str(angle))
        self.close()

    def on_enter_closed(self):
        logging.info("closed")
        logging.debug("enable RC-receiver")
        RC_EN.on()
        logging.debug("waiting for: RC, Buttonpress for start, order to fill, setup")
        while True:
            if RC.is_pressed:
                logging.debug("RC pressed")
                self.blow_cycle()
                break
            if BTN.is_pressed:
                logging.debug("BTN pressed")
                self.blow_cycle()
                break
            #TODO fill order
            if int(R.get("lid_setuplevel") or -1) > 0:
                self.set_angle()
                break
            sleep(0.1)


    def on_exit_closed(self):
        logging.debug("disable RC-receiver")
        RC_EN.off()

    def on_close(self):
        logging.info("Closing")
        logging.debug("shut off fan")
        FAN.off()
        logging.debug("close lid")
        SERVO.fade(int(R.get("lid_closed") or 1))

    def on_enter_open_to_blow(self):
        logging.info("Opening to blow")
        logging.debug("Set lid to")
        SERVO.fade(int(R.get("lid_blowlevel") or 800))
        logging.debug("trigger blow")
        self.blow()

    def on_enter_blowing(self):
        logging.info("Blowing")
        logging.debug("Set fan to " + str((R.get("blowforce") or "1")))
        FAN.value = (float(R.get("blowforce") or 1))
        logging.debug("Wait for")
        sleep(int(R.get("blowtime") or 5))
        self.close()

    def on_exit_blowing(self):
        logging.debug("stop fan")
        FAN.off()

    def on_enter_open_setting(self):
        logging.info("Set lid to ordered value")
        level = int(R.get("lid_setuplevel") or -1)
        while level > 0:
            SERVO.fade(level)
            sleep(0.1)
            level = int(R.get("lid_setuplevel") or -1)
        self.close()

def main():
    # set loglevel from CLI
    parser = ArgumentParser()
    parser.add_argument("-d", "--debug", help="Increase output verbosity", action="store_const", const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()
    logging.basicConfig(level=args.debug)
    logging.debug("DEBUG set")

    logging.info("Setting up hardware modes")
    #TODO

    logging.info("connecting to redis")
    #TODO

    logging.info("Initialize the FSM")
    bullotron = BullotronHW()
    bullotron.init()


if __name__ == '__main__':
    main()

