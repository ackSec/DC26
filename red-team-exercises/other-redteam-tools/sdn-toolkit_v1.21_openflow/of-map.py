#!/usr/bin/env python

"""of-map.py: Dumps Openflow Flow Rules"""

__author__ = "Gregory Pickett"
__dated__ = "6/14/2014"
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

# Networking objects needed
import socket

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

def StaticFlowParserFloodlight(data):

	flowtable[:] = []

	# extract the data for each flow
	for row in data:
		for key, value in data[row].iteritems():
			flow = {}
			flow["switch"] = row
			flow["inputPort"] = value["match"]["inputPort"]
			if value["actions"] is not None:
				for action in value["actions"]:
					if "actions" in flow:
						flow["actions"] = flow["actions"] + ',' + action["type"] + ':' + str(action["port"])
					else:
						flow["actions"] = action["type"] + ':' + str(action["port"])
			else:
				flow["actions"] = "DROP"
			flow["dataLayerVirtualLan"] = value["match"]["dataLayerVirtualLan"]
			flow["networkSource"] = value["match"]["networkSource"]
			flow["networkSourceMaskLen"] = value["match"]["networkSourceMaskLen"]
			flow["transportSource"] = value["match"]["transportSource"]
			flow["networkDestination"] = value["match"]["networkDestination"]
			flow["networkDestinationMaskLen"] =value["match"]["networkDestinationMaskLen"]
			flow["transportDestination"] = value["match"]["transportDestination"]
			flowtable.append(flow)

	return flowtable

def StaticFlowParserOpendaylight(data):

	flowtable[:] = []

	# extract the data for each flow
	for row in data['flowConfig']:
		flow = {}
		flow["switch"] = row["node"]["id"]
		flow["inputPort"] = row["ingressPort"] if "ingressPort" in row else 0
		for action in row["actions"]:
			item = action.split('=')
			if len(item) == 2:
				if "actions" in flow:
					flow["actions"] = flow["actions"] + ',' + item[0] + ':' + str(item[1])
				else:
					flow["actions"] = item[0] + ':' + str(item[1])
			else:
				if "actions" in flow:
					flow["actions"] = flow["actions"] + ',' + item[0]
				else:
					flow["actions"] = item[0]
		flow["dataLayerVirtualLan"] = row["vlanId"] if "vlanId" in row else '-1'
		flow["networkSource"] = row["nwSrc"][:len(row["nwSrc"])-3] if "nwSrc" in row else '0.0.0.0'
		flow["networkSourceMaskLen"] = int(row["nwSrc"][len(row["nwSrc"])-2:]) if "nwSrc" in row else 0
		flow["transportSource"] = row["tpSrc"] if "tpSrc" in row else 0
		flow["networkDestination"] = row["nwDst"][:len(row["nwDst"])-3] if "nwDst" in row else '0.0.0.0'
		flow["networkDestinationMaskLen"] = int(row["nwDst"][len(row["nwDst"])-2:]) if "nwDst" in row else 0
		flow["transportDestination"] = row["tpDst"] if "tpDst" in row else 0
		flowtable.append(flow)

	return flowtable

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

def ListTargets(flowtable,targettitles):

	targettable = []

	filtered = [dictio for dictio in flowtable if dictio['networkDestinationMaskLen'] == 32]
	for row in filtered:
		target = {}
		target["networkDestination"] = row["networkDestination"]
		target["dataLayerVirtualLan"] = row["dataLayerVirtualLan"]
		# Check for duplicates before adding
		if target not in targettable:
			targettable.append(target)
	PrintTable(targettable, targettitles)
	result = 'Listed targets'

	return result

def ListServices(flowtable,servicetitles):

	servicetable = []

	filtered = [dictio for dictio in flowtable if dictio['transportDestination'] != 0]
	for row in filtered:
		service = {}
		service["transportDestination"] = row["transportDestination"]
		service["networkDestination"] = row["networkDestination"]
		if service not in servicetable:
			servicetable.append(service)
	PrintTable(servicetable, servicetitles)
	result = 'Listed services'

	return result

def ListACLs(flowtable,acltitles):

	acltable = []

	filtered = [dictio for dictio in flowtable if dictio['actions'] == "DROP"]
	for row in filtered:
		acl = {}
		acl["networkSource"] = row["networkSource"]
		acl["networkSourceMaskLen"] = row["networkSourceMaskLen"]
		acl["networkDestination"] = row["networkDestination"]
		acl["networkDestinationMaskLen"] = row["networkDestinationMaskLen"]
		acl["transportDestination"] = row["transportDestination"]
		acl["actions"] = row["actions"]
		if acl not in acltable:
			acltable.append(acl)
	PrintTable(acltable, acltitles)
	result = 'Listed ACLs'

	return result

def IdentifySensors(flowtable,sensortitles):

	sensortable = []

	# Filter for multiple action flows
	filtered = [dictio for dictio in flowtable if ',' in dictio['actions']]
	for row in filtered:
		# For all multiple action flows, check if there is more than one output (mirroring?)
		actions = row["actions"].split(',')
		outputs = [elem for elem in actions if 'OUTPUT' in elem]
		if len(outputs) > 1:
			# Assuming the first out is the intended destination, only consider those after the original destination port
			for x in xrange(1, len(outputs)):
				mirror = outputs[x].split(':')
				sensor = {}
				sensor["switch"] = row["switch"]
				sensor["inputPort"] = mirror[1]
				if sensor not in sensortable:
					sensortable.append(sensor)
	PrintTable(sensortable, sensortitles)
	result = 'Identified sensors'

	return result

def IdentifyAttackerSwitch(flowtable):

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect((arguments.controller,arguments.port))
	attackerip = s.getsockname()[0]
	s.close()

	result = ''
	filtered = [dictio for dictio in flowtable if dictio['networkSource'] == attackerip]
	for row in filtered:
		result = row["switch"]
	if result == '':
		result == 'Error! Unable to identify attacker switch'

	return result

def DisplayHelp():

	print "\r"
	print " ----------------------------------------------------------------------------"
	print " | Map Network      | Retrieve all the flows from the connected controller  |"
	print " | List Flows       | Show all flows on the controller network              |"
	print " | List Targets     | Show all available targets on the controller network  |"
	print " | List Services    | Show all available services on the controller network |"
	print " | List ACLs        | Show all denied flows on the controller network       |"
	print " | Identify Sensors | Identify any sensors on the controller network        |"
	print " | Dump Flows       | Save all the flows from the connected controller      |"
	print " ----------------------------------------------------------------------------"
	print " * Currently supports Floodlight and Opendaylight Northbound APIs            "
	print "\r"
	result = 'Displayed help'

	return result

# Global variables
flowtable = []
attackerswitch = ''
message = ''

flowtitles = [('switch', 'Switch'), ('inputPort', 'Input Port'), ('actions', 'Action'), ('dataLayerVirtualLan', 'VLAN'), ('networkSource', 'Src Address'), ('networkSourceMaskLen', 'Src Mask'), ('transportSource', 'Src Port'), ('networkDestination', 'Dst Address'), ('networkDestinationMaskLen', 'Dst Mask'), ('transportDestination', 'Dst Port')]
targettitles = [('networkDestination', 'Target Address'), ('dataLayerVirtualLan', 'VLAN')]
servicetitles = [('transportDestination', 'Target Service'), ('networkDestination', 'Target Address')]
acltitles = [('networkSource', 'Src Address'), ('networkSourceMaskLen', 'Src Mask'), ('networkDestination', 'Dst Address'), ('networkDestinationMaskLen', 'Dst Mask'), ('transportDestination', 'Dst Port'), ('actions', 'Actions')]
sensortitles = [('switch', 'Switch'), ('inputPort', 'Input Port')]


# Main
if __name__ == '__main__':

	# Process command-line arguments
	argParser = argparse.ArgumentParser(description='Dumps Openflow Flow Rules')
	argParser.add_argument('-v', '--version', action='version', version='%(prog)s is at version 1.0.0')
	argParser.add_argument('-p', '--port', default=8080, type=int, help='Openflow port')
	argParser.add_argument('-u', '--user', default='admin', type=str, help='Opendaylight user')
	argParser.add_argument('-pw', '--password', default='admin', type=str, help='Opendaylight password')
	argParser.add_argument('controller', type=str, help='Openflow controller')
	arguments = argParser.parse_args()

	# Detect controller
	controllertype = AutoDetectController(arguments.controller, arguments.port, arguments.user, arguments.password)

	# Define mapping object
	if controllertype == 'Floodlight':
		mapper = StaticFlowPusherFloodlight(arguments.controller,arguments.port)
	elif controllertype == 'Opendaylight':
		mapper = StaticFlowPusherOpendaylight(arguments.controller, arguments.port, arguments.user, arguments.password)
	else:
		message = controllertype

	# Command-loop and menu processing
	menu = {}
	menu['1']="Map Network"
	menu['2']="List Flows"
	menu['3']="List Targets"
	menu['4']="List Services"
	menu['5']="List ACLs"
	menu['6']="Identify Sensors"
	menu['7']="Dump Flows"
	menu['8']="Help"
	menu['9']="Exit"
	while True:
		options=menu.keys()
		options.sort()
		for entry in options:
			print entry + '.', menu[entry]

		# Show dashboard
		print "\r"
		print "Controller: " + arguments.controller + ":" + str(arguments.port)
		print "Switch: " + attackerswitch
		print "Last: " + message
		print "\r"

		# Menu selection
		selection=raw_input("Please Select: ")
		if selection == '1':
			if controllertype != 'Unknown Controller or Bad Credentials':
				data = mapper.get()
				if data is not None:
					# Submit the data to the proper handler
					if controllertype == 'Floodlight':
						flowtable = StaticFlowParserFloodlight(data)
					elif controllertype == 'Opendaylight':
						flowtable = StaticFlowParserOpendaylight(data)
					attackerswitch = IdentifyAttackerSwitch(flowtable)
					message = "Network mapped"
				else:
					message = "Connection Error!"
			else:
				# Reset the message just in case something else was attempted beforehand
				message = controllertype
		elif selection == '2':
			if flowtable:
				PrintTable(flowtable,flowtitles)
				message = "Listed flows"
			else:
				message = "No Map!  Please map the network first."
			print "\r"
		elif selection == '3':
			if flowtable:
				message = ListTargets(flowtable,targettitles)
			else:
				message = "No Map!  Please map the network first."
		elif selection == '4':
			if flowtable:
				message = ListServices(flowtable,servicetitles)
			else:
				message = "No Map!  Please map the network first."
		elif selection == '5':
			if flowtable:
				message = ListACLs(flowtable,acltitles)
			else:
				message = "No Map!  Please map the network first."
		elif selection == '6':
			if flowtable:
				message = IdentifySensors(flowtable,sensortitles)
			else:
				message = "No Map!  Please map the network first."
		elif selection == '7':
			if flowtable:
				filename = "flows-" + time.strftime("%Y-%m-%d") + "-" + time.strftime("%H%M%S") + ".txt"
				message = DumpTable(flowtable,flowtitles, filename)
			else:
				message = "No Map!  Please map the network first."
		elif selection == '8':
				message = DisplayHelp()
		elif selection == '9':
			break
		else:
			message = "Unknown Option Selected!"