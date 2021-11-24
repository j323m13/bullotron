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
    sense = close.to(sens_fill)
    blow_cycle = closed.to(open_to_blow) | open_to_blow.to(blowing) | blowing.to(closed)
    fill = closed.to(open_full)
    set_angle = closed.to(open_setting)

    def on_on_debt(self):
        print('Document on hold.')

        
bullotron = BullotronHW()