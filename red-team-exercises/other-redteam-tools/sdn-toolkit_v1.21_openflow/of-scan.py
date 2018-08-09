#!/usr/bin/env python

"""of-map.py: Dumps Openflow Flow Rules"""

__author__ = "Gregory Pickett"
__dated__ = "2/13/2016"
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
import requests
import json

# Networking objects needed
import socket
import ssl

controllerinventory = []
colltrolleroperations = []
controllergroups = ''
controlleroutput = {}
controllertype = 'N/A'
controllersecure = False
authtoken = ''

def deep_search(needles, haystack):

	# Borrowed from Stack Overflow (http://stackoverflow.com/questions/14048948/how-can-i-use-python-finding-particular-json-value-by-key)

	found = {}
	if type(needles) != type([]):
		needles = [needles]

	if type(haystack) == type(dict()):
		for needle in needles:
			if needle in haystack.keys():
				found[needle] = haystack[needle]
			elif len(haystack.keys()) > 0:
				for key in haystack.keys():
					result = deep_search(needle, haystack[key])
					if result:
						for k, v in result.items():
							found[k] = v
	elif type(haystack) == type([]):
		for node in haystack:
			result = deep_search(needles, node)
			if result:
				for k, v in result.items():
					found[k] = v
	return found

def ParseConfig(section, filename):

	global controllerinventory
	global colltrolleroperations
	global controllergroups
	global controlleroutput
	started = False

	# Open configuration file
	with open(filename) as f:
		# Read configuration file line by line
		for line in f:
			# If comment, skip it
			if line[0] == '#':
				pass
			# If still in the section, continue parsing
			elif started:
				# If not the end of the section, continue parsing
				# Strip ending to ensure that the parsing is clean
				line = line.strip(' \t\n\r')
				if line != '':
					if section == '[Controllers]':
						entries = line.split(',')
						controller = {}
						# Don't include the quotes ([1:-1])
						controller["id"] = entries[0][1:-1]
						controller["name"] = entries[1][1:-1]
						controller["port"] = entries[2]
						controller["method"] = entries[3][1:-1]
						controller["path"] = entries[4][1:-1]
						controller["format"] = entries[5][1:-1]
						controller["headers"] = entries[6][1:-1]
						controller["body"] = entries[7][1:-1]
						controller["success"] = entries[8][1:-1]
						controllerinventory.append(controller)
					elif section == '[Operations]':
						entries = line.split(',')
						if entries[0][1:-1] == controllertype:
							operation = {}
							# Don't include the quotes ([1:-1])							
							operation["operation"] = entries[1][1:-1]
							operation["method"] = entries[2][1:-1]
							operation["path"] = entries[3][1:-1]
							operation["template"] = entries[4][1:-1]
							colltrolleroperations.append(operation)
					elif section == '[Groups]':
						entries = line.split(',')
						if entries[0][1:-1] == controllertype:
							controllergroups  = entries[1]
					elif section == '[Flows]':
						entries = line.split(',')
						if entries[0][1:-1] == controllertype:
							# Don't include the quotes ([1:-1])
							controlleroutput["switch"] = entries[1][1:-1]
							controlleroutput["inputPort"] = entries[2][1:-1]
							controlleroutput["actions"] = entries[3][1:-1]
							controlleroutput["dataLayerVirtualLan"] = entries[4][1:-1]
							controlleroutput["networkSource"] = entries[5][1:-1]
							controlleroutput["networkSourceMaskLen"] = entries[6][1:-1]
							controlleroutput["transportSource"] = entries[7][1:-1]
							controlleroutput["networkDestination"] = entries[8][1:-1]
							controlleroutput["networkDestinationMaskLen"] = entries[9][1:-1]
							controlleroutput["transportDestination"] = entries[10][1:-1]
				# If reached the end of the section, return
				else:
					return
			# If not started, keep looking for section
			# If this is the beginning of the section, start parsing
			elif line.strip(' \t\n\r') == section:
				started = True

def AutoDetectController(server, port, user, password):

	global controllertype
	global controllersecure
	global authtoken
	global arguments

	# If needed, set Authentication header value
	auth = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')

	# Try all controllers
	for controller in controllerinventory:
		try:
			# Set the required headers
			if controller['format'] == 'json':
				if controller['headers'] == 'Content-type/Accept/Authorization':
					headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Basic ' + auth,}
				else:
					headers = {'Content-type': 'application/json', 'Accept': 'application/json',}
			elif controller['format'] == 'xml':
				if controller['headers'] == 'Content-type/Accept/Authorization':
					headers = {'Content-type': 'application/xml', 'Accept': 'application/xml', 'Authorization': 'Basic ' + auth,}
				else:
					headers = {'Content-type': 'application/xml', 'Accept': 'application/xml',}
			# Load the body message
			if controller['format'] == 'json':
				if controller['body'] == '':
					body = ''
				else:
					# Get template name
					operationalmessage = controller['body']
					# Open template
					template = open('templates/' + operationalmessage).read()
					# Replace User and Password
					template = template.replace('<USER>', user)
					template = template.replace('<PASSWORD>', password)
					# Load JSON into JSON Object
					body = template
			elif controller['format'] == 'xml':
				if controller['body'] == '':
					body = ''
				else:
					# Get template name
					operationalmessage = controller['body']
					# Open template
					template = open('templates/' + operationalmessage).read()
					# Replace User and Password
					template = template.replace('<USER>', user)
					template = template.replace('<PASSWORD>', password)
					# Assign XML to Body
					body = template

			# Set port for attempt only
			if port == None:
				# If no port, use the default
				destport = controller['port']
			else:
				destport = port

			path = 'http://' + server + ':' + str(destport) + controller['path']
			if controller['method'] == 'GET':
				response = requests.get(path, headers=headers)
			elif controller['method'] == 'POST':
				response = requests.post(path, body, headers=headers)
			elif controller['method'] == 'PUT':
				response = requests.put(path, body, headers=headers)
			elif controller['method'] == 'DELETE':
				response = requests.delete(path, headers=headers)
			ret = (response.status_code, response.headers._store['content-type'], response.text)

			# Confirm response and content-type
			if ret[0] == 200 and ret[1][1].find(controller["format"]) != -1:
				# Load any response
				valid = ret[2]
				message = controller['success']
				# If there is an application layer message that indicates success, look for it
				if message != '':
					# Look for message
					if valid.find(message) != -1:
						# Record token
						body = json.loads(ret[2])
						search = deep_search([controller["success"]], body)
						authtoken = str(search[controller["success"]])
						# Passthrough port that was successful
						arguments.port = destport
						# Since it passed final check, set the controller type
						controllertype = controller['id']
						result = 'Success!'
						return result
					else:
						# Passthrough port that was successful
						arguments.port = destport
						# While the password is bad, you still know the controller type
						controllertype = controller['id']
						# Record bad password
						result = 'Bad Credentials!'
						return result
				# If there is no application layer message that indicates success, return
				else:
					# Passthrough port that was successful
					arguments.port = destport
					# Since it passed final check, set the controller type
					controllertype = controller['id']
					result = 'Success!'
					return result
			# If unauthorized
			elif ret[0] == 401:
				# Passthrough port that was successful
				arguments.port = destport
				# While the password is bad, you still know the controller type
				controllertype = controller['id']
				# Record bad password
				result = 'Bad Credentials!'
				return result

		except:
			# Record connection error, but continue to other controllers on other ports
			result = 'Connection Error!'

	# Try all controllers (HTTPS)
	for controller in controllerinventory:
		try:
			# Set the required headers
			if controller['format'] == 'json':
				if controller['headers'] == 'Content-type/Accept/Authorization':
					headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Basic ' + auth,}
				else:
					headers = {'Content-type': 'application/json', 'Accept': 'application/json',}
			elif controller['format'] == 'xml':
				if controller['headers'] == 'Content-type/Accept/Authorization':
					headers = {'Content-type': 'application/xml', 'Accept': 'application/xml', 'Authorization': 'Basic ' + auth,}
				else:
					headers = {'Content-type': 'application/xml', 'Accept': 'application/xml',}
			# Load the body message
			if controller['format'] == 'json':
				if controller['body']  == '':
					body = ''
				else:
					# Get template name
					operationalmessage = controller['body']
					# Open template
					template = open('templates/' + operationalmessage).read()
					# Replace User and Password
					template = template.replace('<USER>', user)
					template = template.replace('<PASSWORD>', password)
					# Load JSON into JSON Object
					body = template
			elif controller['format'] == 'xml':
				if controller['body'] == '':
					body = ''
				else:
					# Get template name
					operationalmessage = controller['body']
					# Open template
					template = open('templates/' + operationalmessage).read()
					# Replace User and Password
					template = template.replace('<USER>', user)
					template = template.replace('<PASSWORD>', password)
					# Assign XML to Body
					body = template

			# Set port for attempt only
			if port == None:
				# If no port, use the default
				destport = controller['port']
			else:
				if port == 80:
					# If gave standard HTTP port, use standard HTTPS port
					destport = 443
				else:
					# Otherwise, use what you gave
					destport = port

			path = 'https://' + server + ':' + str(destport) + controller['path']
			if controller['method'] == 'GET':
				response = requests.get(path, headers=headers, verify=False)
			elif controller['method'] == 'POST':
				response = requests.post(path, body, headers=headers, verify=False)
			elif controller['method'] == 'PUT':
				response = requests.put(path, body, headers=headers, verify=False)
			elif controller['method'] == 'DELETE':
				response = requests.delete(path, headers=headers, verify=False)
			ret = (response.status_code, response.headers._store['content-type'], response.text)

			# Confirm response and content-type
			if ret[0] == 200 and ret[1][1].find(controller["format"]) != -1:
				# Load any response
				valid = ret[2]
				message = controller['success']
				# If there is an application layer message that indicates success, look for it
				if message != '':
					# Look for message
					if valid.find(message) != -1:
						# Record token
						body = json.loads(ret[2])
						search = deep_search([controller["success"]], body)
						authtoken = str(search[controller["success"]])
						# Passthrough port that was successful
						arguments.port = destport			
						# Indicate that the controller is secure
						controllersecure = True
						# Since it passed final check, set the controller type
						controllertype = controller['id']
						result = 'Success!'
						return result
					else:
						# Passthrough port that was successful
						arguments.port = destport
						# Indicate that the controller is secure
						controllersecure = True
						# While the password is bad, you still know the controller type
						controllertype = controller['id']
						# Record bad password
						result = 'Bad Credentials!'
						return result
				# If there is no application layer message that indicates success, return
				else:
					# Passthrough port that was successful
					arguments.port = destport
					# Indicate that the controller is secure
					controllersecure = True
					# Since it passed final check, set the controller type
					controllertype = controller['id']
					result = 'Success!'
					return result
			# If unauthorized
			elif ret[0] == 401:
				# Passthrough port that was successful
				arguments.port = destport
				# Indicate that the controller is secure
				controllersecure = True
				# While the password is bad, you still know the controller type
				controllertype = controller['id']
				# Record bad password
				result = 'Bad Credentials!'
				return result

		except:
			# Record connection error, but continue to other controllers on other ports
			result = 'Connection Error!'

	# If it makes it here, the controller is unknown
	if result != 'Connection Error!':
		result = 'Unknown Controller or Bad Credentials'
	return result

def LookupController():

	for controller in controllerinventory:
		if controller["id"] == controllertype:
			return controller

class StaticFlowPusher(object):

	# Borrowed from Openflow Hub (http://www.openflowhub.org/pages/viewinfo.action?pageId=3244807)

	def __init__(self, server, port, user, password):
		self.server = server
		self.port = port
		self.user = user
		self.password = password

	def get(self, method, path):
		ret = self.rest_call(method, path, {})
		try:
			result = json.loads(ret[2])
		except:
			result = None
		return result

	def set(self, method, path, data):
		ret = self.rest_call(method, path, data)
		return ret[0] == 200

	def remove(self, method, path, data):
		ret = self.rest_call(method, path, data)
		return ret[0] == 200

	def rest_call(self, method, path, data):

		# Grab controller properties
		controller = LookupController()

		# If needed, set Authentication header value
		auth = base64.encodestring('%s:%s' % (self.user, self.password)).replace('\n', '')

		# Set the required headers
		if controller['format'] == 'json':
			if controller['headers'] == 'Content-type/Accept/Authorization':
				headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Basic ' + auth,}
			elif controller['headers'] == 'Content-type/Accept/Login':
				headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': authtoken,}
			else:
				headers = {'Content-type': 'application/json', 'Accept': 'application/json',}
		elif controller['format'] == 'xml':
			if controller['headers'] == 'Content-type/Accept/Authorization':
				headers = {'Content-type': 'application/xml', 'Accept': 'application/xml', 'Authorization': 'Basic ' + auth,}
			elif controller['headers'] == 'Content-type/Accept/Login':
				headers = {'Content-type': 'application/xml', 'Accept': 'application/xml', 'X-Auth-Token': authtoken,}
			else:
				headers = {'Content-type': 'application/xml', 'Accept': 'application/xml',}
		try:

			body = data
			proxies = {'http': self.server + ':' + str(self.port), 'https': self.server + ':' + str(self.port)}
			if method == 'GET':
				response = requests.get(path, headers=headers, proxies=proxies, verify=False)
			elif method == 'POST':
				response = requests.post(path, body, headers=headers, proxies=proxies, verify=False)
			elif method == 'PUT':
				response = requests.put(path, body, headers=headers, proxies=proxies, verify=False)
			elif method == 'DELETE':
				response = requests.delete(path, headers=headers, proxies=proxies, verify=False)
			ret = (response.status_code, response.reason, response.text)

		except:
			ret = ('', '', {})
		return ret

def ScanController():

	id = 0

	for operation in colltrolleroperations:
		# Set variables
		flowname = "flow-" + time.strftime("%Y-%m%d-") + time.strftime("%H%M%S")
		switch='1'
		sourceaddress='10.0.0.1'
		destinationaddress='10.0.0.1'
		destinationport='0'
		actions=''
		priority='32768'
		# Start path
		if not controllersecure:
			path = 'http://' + arguments.controller + ':' + str(arguments.port) + operation["path"]
		else:
			path = 'https://' + arguments.controller + ':' + str(arguments.port) + operation["path"]
		# Modify for object references
		path = path.replace('<SWITCH>', switch)
		path = path.replace('<FLOWNAME>', flowname)
		# Load template
		if operation['template'] !='':
			message = open('templates/' + operation['template']).read()
			# Replace variables in template
			# If flow needs unique ID, add it
			if message.find('<#>') != -1:
				id=id+1
				message = message.replace('<#>', id)
				path = path.replace('<#>', id)
			message = message.replace('<SWITCH>', switch)
			message = message.replace('<FLOWNAME>', flowname)
			message = message.replace('<NETWORKSOURCE>', sourceaddress)
			message = message.replace('<NETWORKDESTINATION>', destinationaddress)
			message = message.replace('<DESTINATIONPORT>', destinationport)
			message = message.replace('<ACTIONS>', actions)
			message = message.replace('<PRIORITY>', priority)
		else:
			message = ''
		# Send according to method
		if operation["method"]=='GET':
			result = accessor.get(operation["method"], path)
		elif operation["method"]=='POST' or operation["method"]=='PUT':
			result = accessor.set(operation["method"], path, message)
		elif operation["method"]=='DELETE':
			result = accessor.remove(operation["method"], path, message)

	return 'Scanned!'
		
if __name__ == "__main__":

	# Process command-line arguments
	argParser = argparse.ArgumentParser(description='Scan Controller API')
	argParser.add_argument('-v', '--version', action='version', version='%(prog)s is at version 1.1.0')
	argParser.add_argument('-p', '--port', type=int, help='API port')
	argParser.add_argument('-u', '--user', default='admin', type=str, help='User')
	argParser.add_argument('-pw', '--password', default='admin', type=str, help='Password')
	argParser.add_argument('-pa', '--proxyadd', type=str, help='Proxy address')
	argParser.add_argument('-pp', '--proxyport', type=int, help='Proxy port')
	argParser.add_argument('-a', '--autodetectonly', action='store_true', default=False, help='Autodetect Only')
	argParser.add_argument('controller', type=str, help='Controller')
	arguments = argParser.parse_args()

	# Load controllers
	ParseConfig("[Controllers]", "config.ini")	
	# Detect controller
	result = AutoDetectController(arguments.controller, arguments.port, arguments.user, arguments.password)
	if not arguments.autodetectonly:
		if result == 'Success!':
			ParseConfig('[Operations]', 'config.ini')
			accessor = StaticFlowPusher(arguments.proxyadd, arguments.proxyport, arguments.user, arguments.password)
			ScanController()
			print 'Scan Complete!'
		else:
			print result
	else:
		print 'Autodetect Only'
		print 'Controller is ' + controllertype