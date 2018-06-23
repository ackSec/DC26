from mininet.topo import Topo
from mininet.util import irange
from mininet.net import Containernet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')

class DatacenterBasicTopo( Topo ):
    "Datacenter topology with 4 hosts per rack, 4 racks, and a root switch"
    self = Containernet(controller=RemoteController)
    info('*** Adding controller\n')
    self.addController( 'c0', controller=RemoteController, ip='172.31.2.32', port=6653 )

    def build( self ):
        self.racks = []
        rootSwitch = self.addSwitch( 's1' )
        for i in irange( 1, 2 ):
            rack = self.buildRack( i )
            self.racks.append( rack )
            for switch in rack:
                self.addLink( rootSwitch, switch )

    def buildRack( self, loc ):
        "Build a rack of hosts with a top-of-rack switch"

        dpid = ( loc * 16 ) + 1
        switch = self.addSwitch( 's1r%s' % loc, dpid='%x' % dpid )

        for n in irange( 1, 5 ):
            #host = self.addHost( 'h%sr%s' % ( n, loc ) )
            host = self.addDocker('h%sr%s' % ( n, loc ), dimage="ubuntu:trusty")
            self.addLink( switch, host )

        # Return list of top-of-rack switches for this rack
        return [switch]

# Allows the file to be imported using `mn --custom <filename> --topo faucet`
topos = {
    'faucet': DatacenterBasicTopo
}
