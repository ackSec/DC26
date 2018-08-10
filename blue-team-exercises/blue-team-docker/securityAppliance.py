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
pusher = StaticFlowPusher(controllerAddress)


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
        attacker = ip.src
        victim = ip.dst
        honeynet = "10.0.0.10"
        print("Generating Flows for SDN Controller based on rule triggered")
        # Clear Existing flows
        #subprocess.call(['curl http://controllerAddress:8080/wm/staticentrypusher/clear/all/json'])
        #pusher.remove('/wm/staticflowpusher/json', {'switch':"00:00:00:00:00:00:00:01","name": "flow-mod-1"})
        subprocess.call([
            'curl',
            'http://controllerAddress:8080/wm/staticentrypusher/clear/all/json'
        ])


        flow1 = {
            'switch':"00:00:00:00:00:00:00:01",
            "name":"flow_mod_1",
            "cookie":"0",
            "priority":"32768",
            "in_port":"1",
            "ipv4_src":"10.0.0.1",
            "ipv4_dst":"10.0.0.2",
            "eth_type":"0x0800",
            "active":"true",
            "actions":"output=3"
        }

        flow11 = {
            'switch':"00:00:00:00:00:00:00:01",
            "name":"flow_mod_11",
            "cookie":"0",
            "priority":"32768",
            "in_port":"1",
            "ip_proto":"0x01",
        #    "ipv4_src":"10.0.0.1",
        #    "ipv4_dst":"10.0.0.2",
            "eth_type":"0x0800",
            "active":"true",
            "actions":"output=3"
        }

        flow12 = {
            'switch':"00:00:00:00:00:00:00:01",
            "name":"flow_mod_12",
            "cookie":"0",
            "priority":"32768",
            "in_port":"1",
            "active":"true",
            "actions":"output=3"
        }

        flow2 = {
            'switch':"00:00:00:00:00:00:00:01",
            "name":"flow_mod_2",
            "cookie":"0",
            "priority":"32768",
            "in_port":"3",
            "ipv4_src":"10.0.0.2",
            "ipv4_dst":"10.0.0.1",
            "eth_type":"0x0800",
            "active":"true",
            "actions":"output=1"
        }

        flow21 = {
            'switch':"00:00:00:00:00:00:00:01",
            "name":"flow_mod_21",
            "cookie":"0",
            "priority":"32768",
            "in_port":"3",
            "ip_proto":"0x01",
        #    "ipv4_src":"10.0.0.2",
        #    "ipv4_dst":"10.0.0.1",
            "eth_type":"0x0800",
            "active":"true",
            "actions":"output=1"
        }

        flow22 = {
            'switch':"00:00:00:00:00:00:00:01",
            "name":"flow_mod_22",
            "cookie":"0",
            "priority":"32768",
            "in_port":"3",
            "active":"true",
            "actions":"output=1"
        }

        #SW2

        flow3 = {
            'switch':"00:00:00:00:00:00:00:03",
            "name":"flow_mod_3",
            "cookie":"0",
            "priority":"32768",
            "in_port":"1",
            "ipv4_src":"10.0.0.2",
            "ipv4_dst":"10.0.0.1",
            "eth_type":"0x0800",
            "active":"true",
            "actions":"output=2"
        }

        flow31 = {
            'switch':"00:00:00:00:00:00:00:03",
            "name":"flow_mod_31",
            "cookie":"0",
            "priority":"32768",
            "in_port":"1",
            "ip_proto":"0x01",
        #    "ipv4_src":"10.0.0.2",
        #    "ipv4_dst":"10.0.0.1",
            "eth_type":"0x0800",
            "active":"true",
            "actions":"output=2"
        }

        flow32 = {
            'switch':"00:00:00:00:00:00:00:03",
            "name":"flow_mod_32",
            "cookie":"0",
            "priority":"32768",
            "in_port":"1",
            "active":"true",
            "actions":"output=2"
        }

        flow4 = {
            'switch':"00:00:00:00:00:00:00:03",
            "name":"flow_mod_4",
            "cookie":"0",
            "priority":"32768",
            "in_port":"2",
            "ipv4_src":"10.0.0.1",
            "ipv4_dst":"10.0.0.2",
            "eth_type":"0x0800",
            "active":"true",
            "actions":"output=1"
        }

        flow41 = {
            'switch':"00:00:00:00:00:00:00:03",
            "name":"flow_mod_41",
            "cookie":"0",
            "priority":"32768",
            "in_port":"2",
            "ip_proto":"0x01",
        #    "ipv4_src":"10.0.0.1",
        #    "ipv4_dst":"10.0.0.2",
            "eth_type":"0x0800",
            "active":"true",
            "actions":"output=1"
        }

        flow42 = {
            'switch':"00:00:00:00:00:00:00:03",
            "name":"flow_mod_42",
            "cookie":"0",
            "priority":"32768",
            "in_port":"2",
            "active":"true",
            "actions":"output=1"
        }





if __name__ == '__main__':
    main()
