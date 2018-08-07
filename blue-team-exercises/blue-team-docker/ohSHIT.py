#!/usr/bin/env/python

###############################
# The script to use if something breaks
###############################

import httplib
import json
import os
import sys


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
pusher = StaticFlowPusher(controllerIP)


def main():
        print("Attack detected")
        print("Generating Flows for SDN Controller based on rule triggered")
        print("Clearing Existing Flows")

        clear = {
            'switch': "all"
        }
        pusher.get(clear)
        print("Flows cleared")

        # SW2
        # traffic flow from victim host (10.0.0.2) to attacker host (10.0.0.1)
        flow1 = {
            'switch': "00:00:00:00:00:00:00:02",
            "name": "flow_mod_1",
            "cookie": "0",
            "table_id": "0",
            "priority": "32768",
            "idle_timeout": "60",
            "hard_timeout": "60",
            "match": "in_port:2",
            "match": "ipv4_src:10.0.0.2",
            "match": "ipv4_dst:10.0.0.1",
            "match": "eth_type:ipv4",
            "active": "true",
            "instruction_apply_actions": "set_field=ipv4_src->10.0.0.10, output=1"

        }
        print("Flow 1 Generated")
        pusher.set(flow1)
        print("Flow 1 Sent")
        # SW2
        # traffic flow from attacker host (10.0.0.1) to victim host (10.0.0.2)
        flow2 = {
            'switch': "00:00:00:00:00:00:00:02",
            "name": "flow_mod_2",
            "cookie": "0",
            "table_id": "0",
            "priority": "32768",
            "idle_timeout": "60",
            "hard_timeout": "60",
            "match": "in_port:1",
            "match": "ipv4_src:10.0.0.1",
            "match": "ipv4_dst:10.0.0.2",
            "match": "eth_type:ipv4",
            "active": "true",
            "instruction_apply_actions": "set_field=ipv4_dst->" + victim + ", output=2"
        }
        print("Flow 2 Generated")
        pusher.set(flow2)
        print("Flow 2 Sent")

        # SW3
        # traffic from honeynet (10.0.0.10) going through SW3 and back to the attacker host (10.0.0.1)
        flow3 = {
            'switch': "00:00:00:00:00:00:00:03",
            "name": "flow_mod_3",
            "cookie": "0",
            "table_id": "0",
            "priority": "32768",
            "idle_timeout": "60",
            "hard_timeout": "60",
            "match": "in_port:3",
            "match": "ipv4_src:10.0.0.10",
            "match": "ipv4_dst:10.0.0.1,
            "match": "eth_type:ipv4",
            "active": "true",
            "instruction_apply_actions": "set_field=ipv4_src->" + victim + ", output=1"
        }
        print("Flow 3 Generated")
        pusher.set(flow2)
        print("Flow 3 Sent")
        break


if __name__ == '__main__':
    main()
