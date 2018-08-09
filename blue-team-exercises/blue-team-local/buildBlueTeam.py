#!/usr/bin/python

import os
import httplib
import json
import sys
from mininet.net import Containernet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')

class StaticEntryPusher(object):

    def __init__(self, server):
        self.server = server

    def get(self, data):
        ret = self.rest_call({}, 'GET')
        return json.loads(ret[2])

    def set(self, data):
        ret = self.rest_call(data, 'POST')
        return ret[0] == 200

    def remove(self, objtype, data):
        ret = self.rest_call(data, 'DELETE')
        return ret[0] == 200

    def str_to_class(str):
        return getattr(sys.modules[__name__], str)

    def rest_call(self, data, action):
        path = '/wm/staticentrypusher/json'
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            }
        body = json.dumps(data)
        conn = httplib.HTTPConnection(self.server, 8080)
        conn.request(action, path, body, headers)
        response = conn.getresponse()
        ret = (response.status, response.reason, response.read())
        print ret
        conn.close()
        return ret

net = Containernet(controller=RemoteController)
controllerIP = repr(os.environ.get('CONTROLLER_IP'))
pusher = StaticEntryPusher(controllerIP)

flow1 = {
    'switch':"00:00:00:00:00:00:00:01",
    "name":"flow_mod_1",
    "cookie":"0",
    "table_id": "0",
    "priority":"32768",
    "idle_timeout": "0",
    "hard_timeout": "0",
    "match": "in_port:1",
    "match": "ipv4_src:10.0.0.1",
    "match": "ipv4_dst:10.0.0.2",
    "match":"eth_type:ipv4",
    "active":"true",
    "actions":"output=2"
}

flow2 = {
    'switch':"00:00:00:00:00:00:00:01",
    "name":"flow_mod_2",
    "cookie":"0",
    "table_id": "0",
    "priority":"32768",
    "idle_timeout": "0",
    "hard_timeout": "0",
    "match": "in_port:2",
    "match": "ipv4_src:10.0.0.2",
    "match": "ipv4_dst:10.0.0.1",
    "match":"eth_type:ipv4",
    "active":"true",
    "actions":"output=1"
}

flow3 = {
    'switch':"00:00:00:00:00:00:00:01",
    "name":"flow_mod_3",
    "cookie":"0",
    "table_id": "0",
    "priority":"32768",
    "idle_timeout": "0",
    "hard_timeout": "0",
    "match": "eth_type:arp",
    "actions": "output=1",
    "actions": "output=2",
    "actions": "output=3",
    "active":"true"
}

#SW2

flow4 = {
    'switch':"00:00:00:00:00:00:00:02",
    "name":"flow_mod_4",
    "cookie":"0",
    "table_id": "0",
    "priority":"32768",
    "idle_timeout": "0",
    "hard_timeout": "0",
    "match": "in_port:1",
    "match": "ipv4_src:10.0.0.2",
    "mat   ch": "ipv4_dst:10.0.0.1",
    "match":"eth_type:ipv4",
    "active":"true",
    "actions":"output=2"
}

flow5 = {
    'switch':"00:00:00:00:00:00:00:02",
    "name":"flow_mod_5",
    "cookie":"0",
    "table_id": "0",
    "priority":"32768",
    "idle_timeout": "0",
    "hard_timeout": "0",
    "match": "in_port:2",
    "match": "ipv4_src:10.0.0.1",
    "match": "ipv4_dst:10.0.0.2",
    "match":"eth_type:ipv4",
    "active":"true",
    "actions":"output=1"
}

flow6 = {
    'switch':"00:00:00:00:00:00:00:02",
    "name":"flow_mod_6",
    "cookie":"0",
    "table_id": "0",
    "priority":"32768",
    "idle_timeout": "0",
    "hard_timeout": "0",
    "match": "eth_type:arp",
    "actions": "output=1",
    "actions": "output=2",
    "actions": "output=3",
    "active":"true"
}

#drop honey - not sure if this is needed.  Confirm with Jon.

flow8 = {
'switch':"00:00:00:00:00:00:00:03",
"name":"flow_mod_8",
"cookie":"0xbad",
"table_id": "0",
"priority":"32768",
"idle_timeout": "0",
"hard_timeout": "0",
"match": "in_port:1",
"action": ""

}


info('*** Adding controller at ' + controllerIP + '\n')

net.addController( 'c0', controller=RemoteController, ip=controllerIP, port=6653 )

info('*** Adding docker containers\n')

h1 = net.addDocker('attacker', ip='10.0.0.1', dimage="acksec/dc26", environment={"CONTROLLER_IP": 'controllerIP'}, working_dir="/root")
h2 = net.addDocker('victim', ip='10.0.0.2', dimage="acksec/snort", environment={"CONTROLLER_IP": 'controllerIP'}, working_dir="/opt")
h3 = net.addDocker('honeynet', ip='10.0.0.10', dimage="acksec/honeynet", environment={"CONTROLLER_IP": 'controllerIP'})

info('*** Adding switches\n')
s1 = net.addSwitch ('s1')
s2 = net.addSwitch ('s2')
s3 = net.addSwitch ('s3')

info('*** Creating links\n')
net.addLink(s1, s2, port1=2, port2=2)
net.addLink(s2, s3, port1=3, port2=3)
net.addLink(s3, s1, port1=2, port2=3)
net.addLink(h1, s2, port1=1, port2=1)
net.addLink(h2, s1, port1=1, port2=1)
net.addLink(h3, s3, port1=1, port2=1)

info('*** Starting network\n')
net.start()
#info('*** Testing connectivity\n')
#net.ping([h1, h2])
info('*** Pushing flows\n')
pusher.set(flow1)
pusher.set(flow2)
pusher.set(flow3)
pusher.set(flow4)
pusher.set(flow5)
pusher.set(flow6)
pusher.set(flow8)

info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()
