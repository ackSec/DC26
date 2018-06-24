#!/usr/bin/env/python
import socket
import sys
import hpsdnclient as hp
from hpsdnclient.datatypes import Match, Action, Flow


auth = hp.XAuthToken(server='192.168.1.38', user="sdn", password="skyline")
api= hp.Api(controller='192.168.1.38', auth=auth)
#datapaths = api.get_datapaths()
#print(datapaths)

#detail = api.get_datapath_detail('0000005056a63a80')
#print(detail)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('30.0.0.2', 10010)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)
print >>sys.stderr, 'connected'

while True:
    data = sock.recv(14)
    if data:
        print("Generating Flow for SDN Controller based on rule triggered")
        
        ####Flow 1####
        match = Match(eth_type="ipv4", in_port=1, ipv4_src="10.0.0.2", ipv4_dst="10.0.0.1")
        action = Action(output=23)
        flow = Flow(priority=30000, match=match, actions=action, hard_timeout=30)
        print(flow)
        print("Flow 1 Generated")
        api.add_flows("00:00:00:50:56:a6:3a:80", flow)
        print("Flow 1 Sent")
        
        ####Flow 2####
        match = Match(eth_type="ipv4", in_port=23, ipv4_src="10.0.0.1", ipv4_dst="10.0.0.2")
        action = Action(output=1)
        flow = Flow(priority=30000, match=match, actions=action, hard_timeout=30)
        print(flow)
        print("Flow 2 Generated")
        api.add_flows("00:00:00:50:56:a6:3a:80", flow)
        print("Flow 2 Sent")
        
        ####Flow 3####
        match = Match(eth_type="ipv4", in_port=24, ipv4_src="10.0.0.1", ipv4_dst="10.0.0.2")
        flow = Flow(priority=30000, match=match, hard_timeout=30)
        print(flow)
        print("Flow 3 Generated")
        api.add_flows("00:00:00:50:56:a6:3a:80", flow)
        print("Flow 3 Sent")
        
        ####Honeynet Flow 1####
        match = Match(eth_type="ipv4", in_port=1, ipv4_src="10.0.0.1", ipv4_dst="10.0.0.2")
        action = Action(output=23)
        flow = Flow(priority=30000, match=match, actions=action, hard_timeout=30)
        print(flow)
        print("Honeynet 1 Generated")
        api.add_flows("00:00:00:50:56:a6:3a:80", flow)
        print("Honeynet 1 Sent")
        
        ####Honeynet Flow 2####
        match = Match(eth_type="ipv4", in_port=23, ipv4_src="10.0.0.2", ipv4_dst="10.0.0.1")
        action = Action(output=1)
        flow = Flow(priority=30000, match=match, actions=action, hard_timeout=30)
        print(flow)
        print("Honeynet 2 Generated")
        api.add_flows("00:00:00:50:56:a6:3a:80", flow)
        print("Honeynet 2 Sent")
        
        ####Honeynet Flow 3####
        match = Match(eth_type="ipv4", in_port=24, ipv4_src="10.0.0.2")
        flow = Flow(priority=30000, match=match, hard_timeout=30)
        print(flow)
        print("Honeynet 2 Generated")
        api.add_flows("00:00:00:50:56:a6:3a:80", flow)
        print("Honeynet 2 Sent")
        
        break
    else:
        break




