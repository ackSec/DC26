#!/usr/bin/env/python

###############################
# This is a very static proof of concept
# of how a SDN can dynamically respond to an attack.
# This pushes predefined flows to predefined switches, but with some tweaking
# this can detect threats on the network and dynamically create flows to respond
#
#
###############################

import httplib
import json
import signal
import os
import sys
import dpkt
import socket
import subprocess
from snortunsock import snort_listener


def mac_addr(address):
    return ':'.join('%02x' % ord(b) for b in address)


def ip_to_str(address):
    return socket.inet_ntop(socket.AF_INET, address)


class StaticFlowPusher(object):

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

    def rest_call(self, data, action):
        path = '/wm/staticflowpusher/json'
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


controllerIP = repr(os.environ.get('CONTROLLER_IP'))
pusher = StaticFlowPusher("controllerAddress")


def main():
    for msg in snort_listener.start_recv("/tmp/snort_alert"):
        print('alertmsg: %s' % ''.join(msg.alertmsg))
        buf = msg.pkt

        # Unpack the Ethernet frame (mac src/dst, ethertype)
        eth = dpkt.ethernet.Ethernet(buf)
        print 'Ethernet Frame: ', mac_addr(eth.src), mac_addr(eth.dst), eth.type

        if eth.type != dpkt.ethernet.ETH_TYPE_IP:
            print 'Non IP Packet type not supported %s\n' % eth.data.__class__.__name__

        # Now unpack the data within the Ethernet frame (the IP packet)
        # Pulling out src, dst, length, fragment info, TTL, and Protocol
        ip = eth.data

        # Pull out fragment information (flags and offset all packed into off field, so use bitmasks)
        do_not_fragment = bool(ip.off & dpkt.ip.IP_DF)
        more_fragments = bool(ip.off & dpkt.ip.IP_MF)
        fragment_offset = ip.off & dpkt.ip.IP_OFFMASK

        # Print out the info
        print("Attack detected")
        print 'IP: %s -> %s   (len=%d ttl=%d DF=%d MF=%d offset=%d)\n' % \
              (ip_to_str(ip.src), ip_to_str(ip.dst), ip.len, ip.ttl,
               do_not_fragment, more_fragments, fragment_offset)

        #print('alertmsg: %s' % ''.join(msg.alertmsg))
        attacker = ip_to_str(ip.src)
        victim = ip_to_str(ip.dst)
        honeynet = "10.0.0.10"
        print("Generating Flows for SDN Controller based on rule triggered")
        # Clear Existing flows
        #subprocess.call(['curl http://controllerAddress:8080/wm/staticentrypusher/clear/all/json'])
        pusher.remove('/wm/staticflowpusher/json', {"name": "flow-mod-1"})
        # traffic flow from attacker host (10.0.0.1) to victim host (10.0.0.2)
        flow200 = {
            'switch': "00:00:00:00:00:00:00:01",
            "name": "flow_mod_200",
            "cookie": "0",
            "priority": "32768",
            "in_port":"1",
            "ipv4_src": + attacker,
            "ipv4_dst": + victim,
            "eth_type":"0x0800",
            "active":"true",
            "instruction_apply_actions": "set_field=ipv4_dst->" + honeynet + ", output=3"
        }

        flow210 = {
            'switch':"00:00:00:00:00:00:00:01",
            "name":"flow_mod_210",
            "cookie":"0",
            "priority":"32768",
            "in_port":"1",
            "ip_proto":"0x01",
            "eth_type":"0x0800",
            "active":"true",
            "instruction_apply_actions": "set_field=ipv4_dst->" + honeynet + ", output=3"
        }

        flow220 = {
            'switch':"00:00:00:00:00:00:00:01",
            "name":"flow_mod_220",
            "cookie":"0",
            "priority":"32768",
            "in_port":"1",
            "active":"true",
            "instruction_apply_actions": "set_field=ipv4_dst->" + honeynet + ", output=3"
        }
        print("Flow 2 Generated")
        pusher.set(flow200)
        pusher.set(flow210)
        pusher.set(flow220)
        print("Flow 2 Sent")



        # SW3
        # traffic flow from "victim" honeynet host (10.0.0.10) to attacker host (10.0.0.1)

        flow100 = {
            'switch': "00:00:00:00:00:00:00:03",
            "name": "flow_mod_100",
            "cookie": "0",
            "priority": "32768",
            "in_port":"1",
            "ipv4_src": + victim,
            "ipv4_dst": + attacker,
            "eth_type":"0x0800",
            "active":"true",
            "instruction_apply_actions": "set_field=ipv4_src->" + victim + ", output=2"

        }
        flow110 = {
            'switch':"00:00:00:00:00:00:00:03",
            "name":"flow_mod_110",
            "cookie":"0",
            "priority":"32768",
            "in_port":"1",
            "ip_proto":"0x01",
            "eth_type":"0x0800",
            "active":"true",
            "instruction_apply_actions": "set_field=ipv4_src->" + victim + ", output=2"
        }

        flow120 = {
            'switch':"00:00:00:00:00:00:00:03",
            "name":"flow_mod_120",
            "cookie":"0",
            "priority":"32768",
            "in_port":"1",
            "active":"true",
            "instruction_apply_actions": "set_field=ipv4_src->" + victim + ", output=2"
        }

        print("Flow 1 Generated")
        pusher.set(flow100)
        pusher.set(flow110)
        pusher.set(flow120)
        print("Flow 1 Sent")

        # SW1
        # traffic from honeynet (10.0.0.10) going back to the attacker host (10.0.0.1)
        flow300 = {
            'switch': "00:00:00:00:00:00:00:01",
            "name": "flow_mod_300",
            "cookie": "0",
            "priority": "32768",
            "in_port":"3",
            "ipv4_src": + victim,
            "ipv4_dst": + attacker,
            "eth_type":"0x0800",
            "active":"true",
            "actions":"output=1"
        }

        flow310 = {
            'switch':"00:00:00:00:00:00:00:01",
            "name":"flow_mod_310",
            "cookie":"0",
            "priority":"32768",
            "in_port":"3",
            "ip_proto":"0x01",
            "eth_type":"0x0800",
            "active":"true",
            "actions":"output=1"
        }

        flow320 = {
            'switch':"00:00:00:00:00:00:00:01",
            "name":"flow_mod_320",
            "cookie":"0",
            "priority":"32768",
            "in_port":"3",
            "active":"true",
            "actions":"output=1"
        }
        print("Flow 3 Generated")
        pusher.set(flow300)
        pusher.set(flow310)
        pusher.set(flow320)
        print("Flow 3 Sent")
        break


if __name__ == '__main__':
    main()
