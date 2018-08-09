#!/usr/bin/env python

"""of-access.py: Adds Openflow Flow Rules"""

__author__ = "Gregory Pickett"
__dated__ = "6/18/2014"
__copyright__ = "Copyright 2014, SDN Toolkit"

__license__ = "GNU General Public License version 3.0 (GPLv3)"
__version__ = "1.0.0"
__maintainer__ = "Gregory Pickett"
__email__ = "gregory.pickett@hellfiresecurity.com"
__twitter__ = "@shogun7273"
__status__ = "Production"

# Command-line parsing objects needed
import argparse
import base64

# Date and time objects needed
import time

# Openflow objects needed
import httplib
import json

# Print data in table format
def PrintTable(data, title_row):

	# Borrowed from Philipp Keller (http://howto.pui.ch/post/37471158914/python-print-list-of-dicts-as-ascii-table)

	"""
	data: list of dicts,
	title_row: e.g. [('name', 'Programming Language'), ('type', 'Language Type')]
	"""
	max_widths = {}
	data_copy = [dict(title_row)] + list(data)
	for col in data_copy[0].keys():
		max_widths[col] = max([len(str(row[col])) for row in data_copy])
	cols_order = [tup[0] for tup in title_row]

	def custom_just(col, value):
		if type(value) == int:
			return str(value).rjust(max_widths[col])
		else:
			return value.ljust(max_widths[col])

	# Print top border
	print '\r'
	underline = "-+-".join(['-' * max_widths[col] for col in cols_order])
	print '+-%s-+' % underline
	# Print body of table
	for row in data_copy:
		row_str = " | ".join([custom_just(col, row[col]) for col in cols_order])
		print "| %s |" % row_str
		if data_copy.index(row) == 0:
			underline = "-+-".join(['-' * max_widths[col] for col in cols_order])
			print '+-%s-+' % underline
	# Print bottom border
	underline = "-+-".join(['-' * max_widths[col] for col in cols_order])
	print '+-%s-+' % underline
	print '\r'

# Dump data in table format
def DumpTable(data, title_row, filename):

	# Adapted from Philipp Keller (http://howto.pui.ch/post/37471158914/python-print-list-of-dicts-as-ascii-table)

	"""
	data: list of dicts,
	title_row: e.g. [('name', 'Programming Language'), ('type', 'Language Type')]
	"""
	max_widths = {}
	data_copy = [dict(title_row)] + list(data)
	for col in data_copy[0].keys():
		max_widths[col] = max([len(str(row[col])) for row in data_copy])
	cols_order = [tup[0] for tup in title_row]

	def custom_just(col, value):
		if type(value) == int:
			return str(value).rjust(max_widths[col])
		else:
			return value.ljust(max_widths[col])

	try:
		file = open(filename, "w")

		# Print top border
		underline = "-+-".join(['-' * max_widths[col] for col in cols_order])
		file.write('+-%s-+\n' % underline)
		# Print body of table
		for row in data_copy:
			row_str = " | ".join([custom_just(col, row[col]) for col in cols_order])
			file.write("| %s |\n" % row_str)
			if data_copy.index(row) == 0:
				underline = "-+-".join(['-' * max_widths[col] for col in cols_order])
				file.write('+-%s-+\n' % underline)
		# Print bottom border
		underline = "-+-".join(['-' * max_widths[col] for col in cols_order])
		file.write('+-%s-+\n' % underline)

		file.close()
		result = "Flows dumped"
	except:
		result = "I/O Error!"

	return result

def AutoDetectController(server, port, user, password):

	# Common elements of request
	action = 'GET'
	body = ''

	# Set path for Floodlight
	path = '/wm/staticflowentrypusher/list/all/json'

	# Format headers for Floodlight
	headers = {
		'Content-type': 'application/json',
		'Accept': 'application/json',
		}

	# Try for Floodlight
	try:
		conn = httplib.HTTPConnection(server, port)
		conn.request(action, path, body, headers)
		response = conn.getresponse()
		ret = (response.status, response.reason, response.read())
		conn.close()
		try:
			valid = json.loads(ret[2])
			result = 'Floodlight'
			return result
		except:
			pass
	except:
		result = 'Connection Error!'
		return result

	# Set path for Opendaylight
	path = '/controller/nb/v2/flowprogrammer/default'

	# Format headers for Opendaylight
	auth = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
	headers = {
		'Content-type': 'application/json',
		'Accept': 'application/json',
		'Authorization': 'Basic ' + auth,
		}

	# Try for Opendaylight
	try:
		conn = httplib.HTTPConnection(server, port)
		conn.request(action, path, body, headers)
		response = conn.getresponse()
		ret = (response.status, response.reason, response.read())
		conn.close()
		try:
			valid = json.loads(ret[2])
			result = 'Opendaylight'
			return result
		except:
			pass
	except:
		result = 'Connection Error!'
		return result

	# If it makes it here, the controller is unknown
	result = 'Unknown Controller or Bad Credentials'
	return result

class StaticFlowPusherFloodlight(object):

	# Borrowed from Openflow Hub (http://www.openflowhub.org/pages/viewinfo.action?pageId=3244807)

	def __init__(self, server, port):
		self.server = server
		self.port = port

	def get(self):
		path = '/wm/staticflowentrypusher/list/all/json'
		ret = self.rest_call({}, 'GET', path)
		try:
			result = json.loads(ret[2])
		except:
			result = None
		return result

	def set(self, data):
		path = '/wm/staticflowentrypusher/json'
		ret = self.rest_call(data, 'POST', path)
		return ret[0] == 200

	def remove(self, objtype, data, path):
		path = '/wm/staticflowentrypusher/json'
		ret = self.rest_call(data, 'DELETE', path)
		return ret[0] == 200

	def rest_call(self, data, action, path):
		headers = {
			'Content-type': 'application/json',
			'Accept': 'application/json',
			}
		body = json.dumps(data)
		try:
			conn = httplib.HTTPConnection(self.server, self.port)
			conn.request(action, path, body, headers)
			response = conn.getresponse()
			ret = (response.status, response.reason, response.read())
			conn.close()
		except:
			ret = ('', '', {})
		return ret

class StaticFlowPusherOpendaylight(object):

	# Borrowed from Openflow Hub (http://www.openflowhub.org/pages/viewinfo.action?pageId=3244807)

	def __init__(self, server, port, user, password):
		self.server = server
		self.port = port
		self.user = user
		self.password = password

	def get(self):
		path = '/controller/nb/v2/flowprogrammer/default'
		ret = self.rest_call({}, 'GET', path)
		try:
			result = json.loads(ret[2])
		except:
			result = None
		return result

	def set(self, data):
		path = '/controller/nb/v2/flowprogrammer/default/node/OF/' + data['node']['id'] + '/staticFlow/' + data['name']
		ret = self.rest_call(data, 'PUT', path)
		return ret[0] == 200

	def remove(self, objtype, data, path):
		path = '/controller/nb/v2/flowprogrammer/default/node/OF/' + data['node']['id'] + '/staticFlow/' + data['name']
		ret = self.rest_call(data, 'DELETE', path)
		return ret[0] == 200

	def rest_call(self, data, action, path):
		auth = base64.encodestring('%s:%s' % (self.user, self.password)).replace('\n', '')
		headers = {
			'Content-type': 'application/json',
			'Accept': 'application/json',
			'Authorization': 'Basic ' + auth,
			}
		body = json.dumps(data)
		try:
			conn = httplib.HTTPConnection(self.server, self.port)
			conn.request(action, path, body, headers)
			response = conn.getresponse()
			ret = (response.status, response.reason, response.read())
			conn.close()
		except:
			ret = ('', '', {})
		return ret

def DropTrafficFloodlight():

	flowname = "flow-" + time.strftime("%Y-%m%d-") + time.strftime("%H%M%S")
	dropflow = {
		'switch':'',
		'name':'',
		'cookie':'0',
		'priority':'32768',
		'ether-type':'0x800',
		'src-ip':'',
		'dst-ip':'',
		'active':'true',
		'actions':''
		}

	sourceaddress=raw_input("From: ")
	destinationaddress=raw_input("To: ")
	switch=raw_input("On switch: ")
	priority=raw_input("Priority[32768]: ")
	confirms=raw_input("Drop traffic from " + sourceaddress + " to " + destinationaddress + " [Yes]: ")
	if confirms.lower() == "yes" or confirms.lower() == "y":
		dropflow['switch'] = switch
		dropflow['name'] = flowname
		dropflow['src-ip'] = sourceaddress
		dropflow['dst-ip'] = destinationaddress
		if priority !="": dropflow['priority'] = priority
		result = accessor.set(dropflow)
	else:
		result = "Drop canceled"
	return result

def DropTrafficOpendaylight():

	flowname = "flow-" + time.strftime("%Y-%m%d-") + time.strftime("%H%M%S")
	dropflow = {
		'installInHw':'true',
		'name':'',
		'node':{
		'id':'',
		'type':'OF'
		},
		'cookie':'0',
		'priority':'32768',
		'etherType':'0x800',
		'nwSrc':'',
		'nwDst':'',
		'actions':['DROP']
	}

	sourceaddress=raw_input("From: ")
	destinationaddress=raw_input("To: ")
	switch=raw_input("On switch: ")
	priority=raw_input("Priority[32768]: ")	
	confirms=raw_input("Drop traffic from " + sourceaddress + " to " + destinationaddress + " [Yes]: ")
	if confirms.lower() == "yes" or confirms.lower() == "y":
		dropflow['node']['id'] = switch
		dropflow['name'] = flowname
		dropflow['nwSrc'] = sourceaddress + '/32'
		dropflow['nwDst'] = destinationaddress + '/32'
		if priority !="": dropflow['priority'] = priority
		result = accessor.set(dropflow)
	else:
		result = "Drop canceled"
	return result

def AllowTrafficFloodlight():

	flowname = "flow-" + time.strftime("%Y-%m%d-") + time.strftime("%H%M%S")
	allowflow = {
		'switch':'',
		'name':'',
		'cookie':'0',
		'priority':'32768',
		'ether-type':'0x800',
		'src-ip':'',
		'dst-ip':'',
		'active':'true',
		'actions':'OUTPUT=NORMAL'
		}

	sourceaddress=raw_input("From: ")
	destinationaddress=raw_input("To: ")
	switch=raw_input("On switch: ")
	priority=raw_input("Priority[32768]: ")	
	confirms=raw_input("Allow traffic from " + sourceaddress + " to " + destinationaddress + " [Yes]: ")
	if confirms.lower() == "yes" or confirms.lower() == "y":
		allowflow['switch'] = switch
		allowflow['name'] = flowname
		allowflow['src-ip'] = sourceaddress
		allowflow['dst-ip'] = destinationaddress
		if priority !="": allowflow['priority'] = priority
		result = accessor.set(allowflow)
	else:
		result = "Allow canceled"
	return result

def AllowTrafficOpendaylight():

	flowname = "flow-" + time.strftime("%Y-%m%d-") + time.strftime("%H%M%S")
	allowflow = {
		'installInHw':'true',
		'name':'',
		'node':{
		'id':'',
		'type':'OF'
		},
		'cookie':'0',
		'priority':'32768',
		'etherType':'0x800',
		'nwSrc':'',
		'nwDst':'',
		'actions':['HW_PATH']
	}

	sourceaddress=raw_input("From: ")
	destinationaddress=raw_input("To: ")
	switch=raw_input("On switch: ")
	priority=raw_input("Priority[32768]: ")	
	confirms=raw_input("Allow traffic from " + sourceaddress + " to " + destinationaddress + " [Yes]: ")
	if confirms.lower() == "yes" or confirms.lower() == "y":
		allowflow['node']['id'] = switch
		allowflow['name'] = flowname
		allowflow['nwSrc'] = sourceaddress + '/32'
		allowflow['nwDst'] = destinationaddress + '/32'
		if priority !="": allowflow['priority'] = priority
		result = accessor.set(allowflow)
	else:
		result = "Allow canceled"
	return result

def DirectEntryFloodlight():

	flowname = "flow-" + time.strftime("%Y-%m%d-") + time.strftime("%H%M%S")
	flow = {
		'switch':'',
		'name':'',
		'cookie':'0',
		'priority':'32768',
		'ether-type':'0x800',
		'vlan-id':'',
		'src-ip':'',
		'src-port':'',
		'dst-ip':'',
		'dst-port':'',
		'active':'true',
		'actions':''
		}

	switch=raw_input("Switch: ")
	vlan=raw_input("VLAN: ")
	sourceaddress=raw_input("From: ")
	sourceport=raw_input("Port: ")
	destinationaddress=raw_input("To: ")
	destinationport=raw_input("Port: ")
	actions=raw_input("Actions: ")
	priority=raw_input("Priority[32768]: ")	
	confirms=raw_input("Entry for traffic from " + sourceaddress + " to " + destinationaddress + " [Yes]: ")
	if confirms.lower() == "yes" or confirms.lower() == "y":
		flow['switch'] = switch
		flow['name'] = flowname
		flow['vlan-id'] = vlan
		flow['src-ip'] = sourceaddress
		flow['src-port'] = sourceport
		flow['dst-ip'] = destinationaddress
		flow['dst-port'] = destinationport
		flow['actions'] = actions
		if priority !="": flow['priority'] = priority
		result = accessor.set(flow)
	else:
		result = "Direct entry canceled"
	return result

def DirectEntryOpendaylight():

	flowname = "flow-" + time.strftime("%Y-%m%d-") + time.strftime("%H%M%S")
	flow = {
		'installInHw':'true',
		'name':'',
		'node':{
		'id':'',
		'type':'OF'
		},
		'cookie':'0',
		'priority':'32768',
		'etherType':'0x800',
		'actions':[]
	}

	switch=raw_input("Switch: ")
	vlan=raw_input("VLAN: ")
	sourceaddress=raw_input("From: ")
	sourceport=raw_input("Port: ")
	destinationaddress=raw_input("To: ")
	destinationport=raw_input("Port: ")
	actions=raw_input("Actions: ")
	priority=raw_input("Priority[32768]: ")	
	confirms=raw_input("Entry for traffic from " + sourceaddress + " to " + destinationaddress + " [Yes]: ")
	if confirms.lower() == "yes" or confirms.lower() == "y":
		flow['node']['id'] = switch
		flow['name'] = flowname
		flow["actions"].append(actions)
		# But only enter what is there because Opendaylight doesn't tolerate fields with empty values
		if vlan !="": flow['vlanId'] = vlan
		if sourceaddress !="": flow['nwSrc'] = sourceaddress + '/32'
		if sourceport !="": flow['tpSrc'] = sourceport
		if destinationaddress !="": flow['nwDst'] = destinationaddress + '/32'
		if destinationport !="": flow['tpDst'] = destinationport
		if priority !="": flow['priority'] = priority
		result = accessor.set(flow)
	else:
		result = "Direct entry canceled"
	return result

def HideFromSensorFloodlight(data):

	attackeraddress=raw_input("Hide: ")
	switch=raw_input("On switch: ")
	port=raw_input("From port: ")
	confirms=raw_input("Hide " + attackeraddress + " from sensor on port " + port + " of switch " + switch + " [Yes]: ")
	if confirms.lower() == "yes" or confirms.lower() == "y":

		# extract the data for each flow
		for row in data:
			for key, value in data[row].iteritems():
				# Find any flows involving the address of interest
				if value["match"]["networkSource"] == attackeraddress or value["match"]["networkDestination"] == attackeraddress:

					# Reflect the flow back to the controller minus any mirroring
					flow = {
						'switch':'',
						'name':'',
						'actions':'',
						'priority':'',
						'cookie':'0',
						'dst-mac':'',
						'src-mac':'',
						'ether-type':'',
						'vlan-id':'',
						'vlan-priority':'',
						'ingress-port':'',
						'dst-ip':'',
						'protocol':'',
						'src-ip':'',
						'tos-bits':'',
						'dst-port':'',
						'src-port':'',
						'active':'true',
					}
					flow["switch"] = row
					flow["name"] = key
					flow["priority"] = value["priority"]
					flow["cookie"] = value["cookie"]
					flow["dst-mac"] = value["match"]["dataLayerDestination"]
					flow["src-mac"] = value["match"]["dataLayerSource"]
					flow["ether-type"] = value["match"]["dataLayerType"]
					flow["vlan-id"] = value["match"]["dataLayerVirtualLan"]
					flow["vlan-priority"] = value["match"]["dataLayerVirtualLanPriorityCodePoint"]
					flow["ingress-port"] = value["match"]["inputPort"]
					flow["dst-ip"] = value["match"]["networkDestination"]
					flow["protocol"] = value["match"]["networkProtocol"]
					flow["src-ip"] = value["match"]["networkSource"]
					flow["tos-bits"] = value["match"]["networkTypeOfService"]
					flow["dst-port"] = value["match"]["transportDestination"]
					flow["src-port"] = value["match"]["transportSource"]
					if value["actions"] is not None:
						for action in value["actions"]:
							# Compile any non-mirroring actions for flow reflection
							if not (action["type"] == 'OUTPUT' and action["port"] == int(port)):
								if "actions" in flow:
									flow["actions"] = flow["actions"] + ',' + action["type"] + '=' + str(action["port"])
								else:
									flow["actions"] = action["type"] + '=' + str(action["port"])
					accessor.set(flow)
		result = attackeraddress + " was hidden from " + switch + " on port " + port
	else:
		result = "Hide canceled"
	return result

def HideFromSensorOpendaylight(data):

	attackeraddress=raw_input("Hide: ")
	switch=raw_input("On switch: ")
	port=raw_input("From port: ")
	confirms=raw_input("Hide " + attackeraddress + " from sensor on port " + port + " of switch " + switch + " [Yes]: ")
	if confirms.lower() == "yes" or confirms.lower() == "y":

		# extract the data for each flow
		for row in data['flowConfig']:
			# Find any flows involving the address of interest
            # But first protect the evaluation from the fact that Opendaylight doesn't keep fields with empty values
			if "nwSrc" not in row: row["nwSrc"] = '0.0.0.0/00'
			if "nwDst" not in row: row["nwDst"] = '0.0.0.0/00'
			if (row["nwSrc"] == attackeraddress + '/32') or (row["nwDst"] == attackeraddress + '/32'):

				# Reflect the flow back to the controller minus any mirroring
				flow = {
					'installInHw':'true',
					'name':'',
					'node':{
					'id':'',
					'type':'OF'
					},
					'cookie':'0',
					'actions':[]
				}
				flow["name"] = row["name"]
				flow["node"]["id"] = row["node"]["id"]
				flow["cookie"] = row["cookie"]
				for action in row["actions"]:
					# Compile any non-mirroring actions for flow reflection
					item = action.split('=')
					if len(item) == 2:
						if not (item[0] == 'OUTPUT' and item[1] == port):
							flow["actions"].append(action)
					else:
						flow["actions"].append(action)

				# But only reflect what is there because Opendaylight doesn't tolerate fields with empty values
				if "priority" in row: flow["priority"] = row["priority"]
				if "ingressPort" in row: flow["ingressPort"] = row["ingressPort"]
				if "dlDst" in row: flow["dlDst"] = row["dlDst"]
				if "dlSrc" in row: flow["dlSrc"] = row["dlSrc"]
				if "etherType" in row: flow["etherType"] = row["etherType"]
				if "vlanId" in row: flow["vlanId"] = row["vlanId"]
				if "vlanPriority" in row: flow["vlanPriority"] = row["vlanPriority"]
				if "protocol" in row: flow["protocol"] = row["protocol"]
				if "nwSrc" in row and row["nwSrc"] != '0.0.0.0/00': flow["nwSrc"] = row["nwSrc"]
				if "nwDst" in row and row["nwDst"] != '0.0.0.0/00': flow["nwDst"] = row["nwDst"]
				if "tosBits" in row: flow["tosBits"] = row["tosBits"]
				if "tpSrc" in row: flow["tpSrc"] = row["tpSrc"]
				if "tpDst" in row: flow["tpDst"] = row["tpDst"]

				accessor.set(flow)
		result = attackeraddress + " was hidden from " + switch + " on port " + port
	else:
		result = "Hide canceled"
	return result

def DisplayHelp():

	print "\r"
	print " -------------------------------------------------------------------"
	print " | Drop Traffic      | Cause traffic between hosts to be dropped   |"
	print " | Allow Traffic     | Cause traffic between hosts to be allowed   |"
	print " | Hide from Sensor  | Add a sensor blind spot                     |"
	print " | Direct Entry      | Write your own flow rules for a host        |"
	print " -------------------------------------------------------------------"
	print " * Currently supports Floodlight and Opendaylight Northbound APIs   "
	print "\r"
	result = 'Displayed help'

	return result

# Global variables
message = ''

# Main
if __name__ == '__main__':

	# Process command-line arguments
	argParser = argparse.ArgumentParser(description='Adds Openflow Flow Rules')
	argParser.add_argument('-v','--version', action='version', version='%(prog)s is at version 1.0.0')
	argParser.add_argument('-p','--port', default=8080,type=int, help='Openflow port')
	argParser.add_argument('-u', '--user', default='admin', type=str, help='Opendaylight user')
	argParser.add_argument('-pw', '--password', default='admin', type=str, help='Opendaylight password')
	argParser.add_argument('controller', type=str, help='Openflow controller')
	arguments = argParser.parse_args()

	# Detect controller
	controllertype = AutoDetectController(arguments.controller, arguments.port, arguments.user, arguments.password)

	# Define accessor object
	if controllertype == 'Floodlight':
		accessor = StaticFlowPusherFloodlight(arguments.controller,arguments.port)
	elif controllertype == 'Opendaylight':
		accessor = StaticFlowPusherOpendaylight(arguments.controller, arguments.port, arguments.user, arguments.password)
	else:
		message = controllertype

	# Command-loop and menu processing
	menu = {}
	menu['1']="Drop Traffic"
	menu['2']="Allow Traffic"
	menu['3']="Hide from Sensor"
	menu['4']="Direct Entry"
	menu['5']="Help"
	menu['6']="Exit"
	while True:
		options=menu.keys()
		options.sort()
		for entry in options:
			print entry + '.', menu[entry]

		# Show dashboard
		print "\r"
		print "Controller: " + arguments.controller + ":" + str(arguments.port)
		print "Last: " + str(message)
		print "\r"

		# Menu selection
		selection=raw_input("Please Select: ")
		if selection =='1':
			if controllertype != 'Unknown Controller or Bad Credentials':
				# Submit the request to the proper handler
				if controllertype == 'Floodlight':
					message = DropTrafficFloodlight()
				elif controllertype == 'Opendaylight':
					message = DropTrafficOpendaylight()
				# Put some whitespace between the prompts and the menu 
				print "\r"
			else:
				# Reset the message just in case something else was attempted beforehand
				message = controllertype
			print "\r" 
		elif selection == '2':
			if controllertype != 'Unknown Controller or Bad Credentials':
				# Submit the request to the proper handler
				if controllertype == 'Floodlight':
					message = AllowTrafficFloodlight()
				elif controllertype == 'Opendaylight':
					message = AllowTrafficOpendaylight()
				# Put some whitespace between the prompts and the menu 
				print "\r"					
			else:
				# Reset the message just in case something else was attempted beforehand
				message = controllertype
			print "\r"
		elif selection == '3':
			if controllertype != 'Unknown Controller or Bad Credentials':
				data = accessor.get()
				if data is not None:
					# Submit the request to the proper handler
					if controllertype == 'Floodlight':
						message = HideFromSensorFloodlight(data)
					elif controllertype == 'Opendaylight':
						message = HideFromSensorOpendaylight(data)
					# Put some whitespace between the prompts and the menu
					print "\r"
				else:
					message = "Connection Error!"
			else:
				# Reset the message just in case something else was attempted beforehand
				message = controllertype
			print "\r"
		elif selection == '4':
			if controllertype != 'Unknown Controller or Bad Credentials':
				# Submit the request to the proper handler
				if controllertype == 'Floodlight':
					message = DirectEntryFloodlight()
				elif controllertype == 'Opendaylight':
					message = DirectEntryOpendaylight()
				# Put some whitespace between the prompts and the menu 
				print "\r"					
			else:
				# Reset the message just in case something else was attempted beforehand
				message = controllertype
			print "\r"
		elif selection == '5':
			message = DisplayHelp()
		elif selection == '6':
			break
		else:
			message = "Unknown Option Selected!"