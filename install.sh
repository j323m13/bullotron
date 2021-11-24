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

mkdir /opt/bullotron
cp ./*.py /opt/bullotron/

cp ./*.service /etc/systemd/system/
sudo systemctl daemon-reload

sudo systemctl enable redis-server && sudo systemctl start redis-server
sudo systemctl enable bullotron-hw && sudo systemctl start bullotron-hw
sudo systemctl enable bullotron-display && sudo systemctl start bullotron-display
