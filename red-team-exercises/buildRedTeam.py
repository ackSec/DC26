#!/usr/bin/python

import os
import sys
from mininet.net import Containernet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')


controllerIP = repr(os.environ.get('CONTROLLER_IP'))

net = Containernet(controller=RemoteController)
info('*** Adding controller\n')
net.addController( 'c0', controller=RemoteController, ip='controllerIP', port=6653 )
info('*** Adding docker containers\n')
h1 = net.addDocker('attacker1', ip='10.0.0.1', dimage="acksec/dc26", environment={"CONTROLLER_IP": 'controllerIP'}, working_dir="/root")
h2 = net.addDocker('attacker2', ip='10.0.0.2', dimage="acksec/dc26", environment={"CONTROLLER_IP": 'controllerIP'}, working_dir="/root")

info('*** Adding switches\n')
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
info('*** Creating links\n')
net.addLink(d1, s1)
net.addLink(s1, s2, cls=TCLink, delay='5ms', bw=1)
net.addLink(s2, d2)
info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.ping([d1, d2])
info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()
