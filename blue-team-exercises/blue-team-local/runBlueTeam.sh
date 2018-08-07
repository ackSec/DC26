#!/bin/bash
sed -i 's/controllerIP/'"$CONTROLLER_IP"'/g' buildBlueTeam.py
sudo -E python buildBlueTeam.py
