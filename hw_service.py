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
# […]

# Libs
from statemachine import StateMachine, State # State Machine
from gpiozero import PWMOutputDevice 

# Own modules
import pindefinitions as pin #Pins on the PCB

__author__ = 'MajorTwip'
__copyright__ = 'Copyright 2021, Bullotron'
__license__ = 'Apache 2.0'
__version__ = '0.1'
__maintainer__ = 'MajorTwip'
__email__ = 'majortwip@gmail.com'
__status__ = 'Draft'


class BullotronHW(StateMachine):
    init_hw = State('InitHW', initial=True)
    sens_fill = State('Sensing Level')
    closed = State('Lid closing')
    open_to_blow = State('Lid opening for blowing')
    blowing = State('Blowing')
    open_full = State('Fully opening')
    open_setting =State('Opening to dynamic angle') 

    init = init_hw.to(closed)
    close = sens_fill.to(closed) | open_to_blow.to(closed) | open_full.to(closed) | open_setting.to(closed) 
    sense = closed.to(sens_fill)
    blow_cycle = closed.to(open_to_blow) | open_to_blow.to(blowing) | blowing.to(closed)
    fill = closed.to(open_full)
    set_angle = closed.to(open_setting)

    def on_init(self):
        logging.info("Initialize Hardware")
        logging.debug("shut off fan")
        logging.debug("close lid")

    def on_enter_closed(self):
        logging.info("closed")
        logging.debug("enable RC-receiver")
        logging.debug("waiting for: RC, Buttonpress for start, order to fill, setup")
        sleep(4)
        self.blow_cycle()

    def on_exit_closed(self):
        logging.debug("disable RC-receiver")


    def on_close(self):
        logging.info("Closing")
        logging.debug("shut off fan")
        logging.debug("close lid")

    def on_enter_open_to_blow(self):
        logging.info("Opening to blow")
        logging.debug("Set lid to")
        sleep(2)
        logging.debug("trigger blow")
        self.blow_cycle()

    def on_enter_blowing(self):
        logging.info("Blowing")
        logging.debug("Set fan to")
        logging.debug("Wait for")
        sleep(2)
        self.blow_cycle()


    def on_exit_blowing(self):
        logging.debug("stop fan")



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

