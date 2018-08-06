#!/usr/bin/python

import os
from mininet.net import Containernet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')


net = Containernet(controller=RemoteController)
#controllerIP = 'os.getenv('CONTROLLER_IP')
info('*** Adding controller\n')
net.addController( 'c0', controller=RemoteController, ip='os.getenv(CONTROLLER_IP)', port=6653 )
info('*** Adding docker containers\n')
d1 = net.addDocker('d1', ip='10.0.0.1', dimage="acksec/dc26", environment={"Password": "test"})
d2 = net.addDocker('d2', ip='10.0.0.2', dimage="acksec/dc26")
#d2 = net.addDocker('d2', ip='10.0.0.2', did='8ef9aa514cf0')
info('*** Adding switches\n')
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
info('*** Creating links\n')
net.addLink(d1, s1)
net.addLink(s1, s2, cls=TCLink, delay='100ms', bw=1)
net.addLink(s2, d2)
info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.ping([d1, d2])
info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()
