#!/usr/bin/env/python
import httplib
import json
import signal
from snortunsock import snort_listener

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

flow1 = {
    'switch':"00:00:00:00:00:00:00:01",
    "name":"flow_mod_1",
    "cookie":"0",
    "priority":"32768",
    "in_port":"1",
    "active":"true",
    "actions":"output=flood"
    }

flow2 = {
    'switch':"00:00:00:00:00:00:00:01",
    "name":"flow_mod_2",
    "cookie":"0",
    "priority":"32768",
    "in_port":"2",
    "active":"true",
    "actions":"output=flood"
    }

pusher.set(flow1)
pusher.set(flow2)

for msg in snort_listener.start_recv("/tmp/snort_alert"):
    #print('alertmsg: %s' % ''.join(msg.alertmsg))
    print("Attack detected")
    print("Generating Flow for SDN Controller based on rule triggered")
    pusher.set(flow1)
    print("Flow 1 Generated")
    print("Flow 1 Sent")
    pusher.set(flow2)
    print("Flow 2 Generated")
    print("Flow 2 Sent")


'''
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
'''
