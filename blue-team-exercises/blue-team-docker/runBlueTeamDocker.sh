#!/bin/bash

sudo snort -A unsock -l /tmp -c /opt/etc/snort.conf -i eth0 &
sleep 8
sed -i '/controllerIP/'"$CONTROLLER_IP"'/g' securityAppliance.py
sudo -E securityAppliance.py
