#!/bin/bash

sudo snort -A unsock -l /tmp -c /opt/etc/snort.conf -i victim-eth1 &
sleep 8
sed -i 's/controllerAddress/'"$CONTROLLER_IP"'/g' securityAppliance.py
python securityAppliance.py
