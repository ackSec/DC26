#!/bin/bash
sudo docker rm -f mn.honeynet
sudo docker rm -f mn.attacker
sudo docker rm -f mn.victim
sudo mn -c
