#!/usr/bin/python
#Topology with three switches, victim host, attacker host, and the controller

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
setLogLevel('info')

info('*** Adding controller\n')
self.addController( 'c0', controller=RemoteController, ip='172.31.2.32', port=6653 )

info('*** Adding hosts\n')
h1 = self.addHost ('h1')
h2 = self.addHost ('h2')

info ('***Adding switches\n')
s1 = self.addSwitch ('s1')
s2 = self.addSwitch ('s2')
s3 = self.addSwitch ('s3')

info ('***Adding links\n')
self.addLink(s1, s2, port1=2, port2=2, cls=TCLink, delay='100ms', bw=1)
self.addLink(s2, s1, port1=2, port2=2, cls=TCLink, delay='100ms', bw=1)
self.addLink(s2, s3, port1=3, port2=3, cls=TCLink, delay='100ms', bw=1)
self.addLink(s3, s2, port1=3, port2=3, cls=TCLink, delay='100ms', bw=1)
self.addLink(s3, s1, port1=2, port2=3, cls=TCLink, delay='100ms', bw=1)
self.addLink(s1, s3, port1=3, port2=2, cls=TCLink, delay='100ms', bw=1)
self.addLink(h1, s1, port1=1, port2=1, cls=TCLink, delay='100ms', bw=1)
self.addLink(s1, h1, port1=1, port2=1, cls=TCLink, delay='100ms', bw=1)
self.addLink(h2, s2, port1=1, port2=1, cls=TCLink, delay='100ms', bw=1)
self.addLink(s2, h2, port1=1, port2=1, cls=TCLink, delay='100ms', bw=1)

info('*** Starting network\n')
net.start()
print "Dumping host connections"
dumpNodeConnections (net.hosts)

info('*** Testing connectivity\n')
print "Testing network connectivity"
net.pingALL()

info('*** Running CLI\n')
CLI(net)

info('*** Stopping network')
net.stop()
