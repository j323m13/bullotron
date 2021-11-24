#!/bin/bash
# Made for Raspberry Pi with Raspian

#install packages
sudo apt update
sudo apt install python3 pip3 pigpio redis

#start redis
systemctl start redis
systemctl enable redis

#install python libs
pip3 install -r requirements.txt
