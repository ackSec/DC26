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
