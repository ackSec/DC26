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

    def handler(signum, frame):
        print 'Got CTRL+C'
        exit (0)





signal.signal(signal.SIGINT, handler)


pusher = StaticFlowPusher('<insert_controller_ip')



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
                  (ip_to_str(ip.src), ip_to_str(ip.dst), ip.len, ip.ttl, do_not_fragment, more_fragments, fragment_offset)

        #print('alertmsg: %s' % ''.join(msg.alertmsg))
            attacker = ip_to_str(ip.src)
            victim = ip_to_str(ip.dst)
            honeynet = "10.0.0.10"
            print("Generating Flows for SDN Controller based on rule triggered")

            #SW2
            #traffic flow from victim host (10.0.0.2) to attacker host (10.0.0.1)

            flow1 {
                'switch':"00:00:00:00:00:00:00:02",
                "name":"flow_mod_1",
                "cookie":"0",
                "table_id": "0",
                "priority":"32768",
                "idle_timeout": "60",
                "hard_timeout": "60",
                "match": "in_port:2",
                "match": "ipv4_src:"+ victim,
                "match": "ipv4_dst:"+ attacker,
                "match":"eth_type:ipv4",
                "active":"true",
                "instruction_apply_actions": "set_field=ipv4_src->10.0.0.10, output=1"

            }
            print("Flow 1 Generated")
            pusher.set(flow1)
            print("Flow 1 Sent")
            # traffic flow from attacker host (10.0.0.1) to victim host (10.0.0.2)
            flow2 = {
                'switch':"00:00:00:00:00:00:00:02,
                "name":"flow_mod_2",
                "cookie":"0",
                "table_id": "0",
                "priority":"32768",
                "idle_timeout": "60",
                "hard_timeout": "60",
                "match": "in_port:1",
                "match": "ipv4_src:" + attacker,
                "match": "ipv4_dst:" + victim,
                "match":"eth_type:ipv4",
                "active":"true",
                "instruction_apply_actions": "set_field=ipv4_dst->" + victim + ", output=2"
            }
            print("Flow 2 Generated")
            pusher.set(flow2)
            print("Flow 2 Sent")
            #SW3
            #traffic from honeynet (10.0.0.10) going through SW3 and back to the attacker host (10.0.0.1)
            flow3 = {
                'switch':"00:00:00:00:00:00:00:03",
                "name":"flow_mod_3",
                "cookie":"0",
                "table_id": "0",
                "priority":"32768",
                "idle_timeout": "60",
                "hard_timeout": "60",
                "match": "in_port:3",
                "match": "ipv4_src:" + honeynet,
                "match": "ipv4_dst:" + attacker,
                "match":"eth_type:ipv4",
                "active":"true",
                "instruction_apply_actions": "set_field=ipv4_src->" + victim + ", output=1"
            }
            print("Flow 3 Generated")
            pusher.set(flow2)
            print("Flow 3 Sent")


if __name__ == '__main__':
    main()
