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



def main():
    # set loglevel from CLI
    parser = ArgumentParser()
    parser.add_argument("-d", "--debug", help="Increase output verbosity", action="store_const", const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()
    logging.basicConfig(level=args.debug)
    logging.debug("DEBUG set")
    
    #juste pour montrer la simplicité de REDIS
    
    while True:
      R.set("somekey", BTN1.is_pressed)
      sleep(1)

if __name__ == '__main__':
    main()
