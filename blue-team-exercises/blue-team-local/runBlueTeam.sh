#!/bin/bash
sed -i 's/controllerAddress/'"$CONTROLLER_IP"'/g' buildBlueTeam.py
sudo -E python buildBlueTeam.py
