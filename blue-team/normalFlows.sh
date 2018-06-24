#!/bin/bash

token=`curl -sk -H 'Content-Type:application/json' -d'{"login":{"user":"sdn","password":"skyline","domain":"sdn"}}' https://192.168.1.38:8443/sdn/v2.0/auth | python -mjson.tool | grep "token" | tr -d [:space:] | tr -d "\"," | cut -d ":" -f 2`;

echo "$token" > /tmp/token;
echo token 

#curl -sK -H "X-Auth-Token:`cat /tmp/token`" -H "Content-Type:application/json" #https://192.168.1.38:8443/sdn/v2.0/of/datapaths/cc:4e:24:c6:67:14:00:00/flows  | python -mjson.tool
#SW1
curl -ski -X POST \
     -H "X-Auth-Token:`cat /tmp/token`" \
     -H "Content-Type:application/json" \
     -d '{
	"flow": {
		"cookie": "0x0",
		"table_id": 0,
		"priority": 60000,
		"idle_timeout": 60,
		"hard_timeout": 60,
		"match": [
			{"in_port":1},
			{"ipv4_src": "10.0.0.1"},
			{"ipv4_dst": "10.0.0.2"},
			{"eth_type": "ipv4"}
		],
		"actions": [{"output": 2}]
		}
}' https://192.168.1.38:8443/sdn/v2.0/of/datapaths/cc:4e:24:c6:67:14:00:00/flows
	
curl -ski -X POST \
     -H "X-Auth-Token:`cat /tmp/token`" \
     -H "Content-Type:application/json" \
     -d '{"flow": {
		"cookie": "0x0",
		"table_id": 0,
		"priority": 60000,
		"idle_timeout": 60,
		"hard_timeout": 60,
		"match": [
			{"in_port":2},
			{"ipv4_src": "10.0.0.2"},
			{"ipv4_dst": "10.0.0.1"},
			{"eth_type": "ipv4"}
		],
		"actions": [{"output": 1}]
		}
}' https://192.168.1.38:8443/sdn/v2.0/of/datapaths/cc:4e:24:c6:67:14:00:00/flows

curl -ski -X POST \
     -H "X-Auth-Token:`cat /tmp/token`" \
     -H "Content-Type:application/json" \
     -d '{
	"flow": {
		"cookie": "0x0",
		"table_id": 0,
		"priority": 60000,
		"idle_timeout": 60,
		"hard_timeout": 60,
		"match": [
			 {"eth_type": "arp"}
		],
		"actions": [
			    {"output": 1},
			    {"output": 2},
			    {"output": 3}
		]
			
		}
	}' https://192.168.1.38:8443/sdn/v2.0/of/datapaths/cc:4e:24:c6:67:14:00:00/flows


#SW2
curl -ski -X POST \
     -H "X-Auth-Token:`cat /tmp/token`" \
     -H "Content-Type:application/json" \
     -d '{
	"flow": {
		"cookie": "0x0",
		"table_id": 0,
		"priority": 60000,
		"idle_timeout": 60,
		"hard_timeout": 60,
		"match": [
			{"in_port":1},
			{"ipv4_src": "10.0.0.2"},
			{"ipv4_dst": "10.0.0.1"},
			{"eth_type": "ipv4"}
		],
		"actions": [{"output": 2}]
		}
}' https://192.168.1.38:8443/sdn/v2.0/of/datapaths/cc:4e:24:c6:62:d0:00:00/flows
	
curl -ski -X POST \
     -H "X-Auth-Token:`cat /tmp/token`" \
     -H "Content-Type:application/json" \
     -d '{"flow": {
		"cookie": "0x0",
		"table_id": 0,
		"priority": 60000,
		"idle_timeout": 60,
		"hard_timeout": 60,
		"match": [
			{"in_port":2},
			{"ipv4_src": "10.0.0.1"},
			{"ipv4_dst": "10.0.0.2"},
			{"eth_type": "ipv4"}
		],
		"actions": [{"output": 1}]
		}
}' https://192.168.1.38:8443/sdn/v2.0/of/datapaths/cc:4e:24:c6:62:d0:00:00/flows

curl -ski -X POST \
     -H "X-Auth-Token:`cat /tmp/token`" \
     -H "Content-Type:application/json" \
     -d '{
	"flow": {
		"cookie": "0x0",
		"table_id": 0,
		"priority": 60000,
		"idle_timeout": 60,
		"hard_timeout": 60,
		"match": [
			 {"eth_type": "arp"}
		],
		"actions": [
			    {"output": 1},
			    {"output": 2},
			    {"output": 3}
		]
			
		}
	}' https://192.168.1.38:8443/sdn/v2.0/of/datapaths/cc:4e:24:c6:62:d0:00:00/flows


#SW3

#STP loop killer
curl -ski -X POST \
     -H "X-Auth-Token:`cat /tmp/token`" \
     -H "Content-Type:application/json" \
     -d '{
	"flow": {
		"cookie": "0x0",
		"table_id": 0,
		"priority": 60000,
		"idle_timeout": 60,
		"hard_timeout": 60,
		"match": [
			 {"in_port": 3}
		],
		"actions": []
		}
	}' https://192.168.1.38:8443/sdn/v2.0/of/datapaths/cc:4e:24:c6:68:4c:00:00/flows

#drop honey
curl -ski -X POST \
     -H "X-Auth-Token:`cat /tmp/token`" \
     -H "Content-Type:application/json" \
     -d '{
	"flow": {
		"cookie": "0xbad",
		"table_id": 0,
		"priority": 60000,
		"idle_timeout": 60,
		"hard_timeout": 60,
		"match": [
			 {"in_port": 1}
		],
		"actions": []
		}
	}' https://192.168.1.38:8443/sdn/v2.0/of/datapaths/cc:4e:24:c6:68:4c:00:00/flows



