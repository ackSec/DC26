#!/bin/bash

sudo snort -A unsock -l /tmp -c /opt/etc/snort.conf -i eth0 &
sed -i 's/controllerIP/'"$CONTROLLER_IP"'/g'sed -i 's/controllerIP/'"$CONTROLLER_IP"'/g' buildBlueTeam.py
sudo -E python buildBlueTeam.py
