#!/bin/bash

sudo snort -A unsock -l /tmp -c /opt/etc/snort.conf -i victim-eth1 &
sleep 3
sed -i 's/CTRLR/'$CONTROLLER_IP'/g' securityAppliance.py
sed -i 's/controllerAddress/'*ADD IP HERE*'/g' securityAppliance.py
python securityAppliance.py
