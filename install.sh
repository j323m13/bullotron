#!/bin/bash
# Made for Raspberry Pi with Raspian

#install packages
sudo apt update
sudo apt install python3 python3-pip pigpio redis
#start redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

#install python libs
pip3 install -r requirements.txt
