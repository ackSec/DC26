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
		"priority": 65000,
		"idle_timeout": 0,
		"hard_timeout": 60,
		"match": [
			{"eth_type":"arp"}
		],
		"actions": [
			{"output": "controller"}
		]			
		}
}' https://192.168.1.38:8443/sdn/v2.0/of/datapaths/cc:4e:24:c6:67:14:00:00/flows
