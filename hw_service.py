#! python
# -*- coding: utf-8 -*-

"""
The Bullotron is a automated Bubble-Machine

This File represents the Hardware-driving part.
This Code is licenced under the Apache License 2.0
"""

# Built-in/Generic Imports
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



