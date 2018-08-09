#!/usr/bin/env python

"""of-check.py: Checks for Openflow-based service"""

__author__ = "Gregory Pickett"
__dated__ = "3/16/2014"
__copyright__ = "Copyright 2014, SDN Toolkit"

__license__ = "GNU General Public License version 3.0 (GPLv3)"
__version__ = "1.0.0"
__maintainer__ = "Gregory Pickett"
__email__ = "gregory.pickett@hellfiresecurity.com"
__twitter__ = "@shogun7273"
__status__ = "Production"

# Socket object needed
import socket

# Import fileinput to load addresses
import fileinput

# Import Argparse for command-line arguments
import argparse

# Header parsing object needed
import struct

# The format of the header on all OpenFlow packets.
OFP_HEADER_FORMAT = '!BBHL'
OFP_HEADER_LENGTH = 8

# The version code for the OpenFlow Protocol version 1.0.0.
OFP_VERSION_1_0_0 = 0x01

# OpenFlow message types.
# Immutable messages.
OFPT_HELLO = 0 # Symmetric message.
OFPT_ERROR = 1 # Symmetric message.
OFPT_ECHO_REQUEST = 2 # Symmetric message.
OFPT_ECHO_REPLY = 3 # Symmetric message.
OFPT_VENDOR = 4 # Symmetric message.
# Switch configuration messages.
OFPT_FEATURES_REQUEST = 5 # Controller/switch message.
OFPT_FEATURES_REPLY = 6 # Controller/switch message.
OFPT_GET_CONFIG_REQUEST = 7 # Controller/switch message.
OFPT_GET_CONFIG_REPLY = 8 # Controller/switch message.
OFPT_SET_CONFIG = 9 # Controller/switch message.
# Asynchronous messages.
OFPT_PACKET_IN = 10 # Async message.
OFPT_FLOW_REMOVED = 11 # Async message.
OFPT_PORT_STATUS = 12 # Async message.
# Controller command messages.
OFPT_PACKET_OUT = 13 # Controller/switch message.
OFPT_FLOW_MOD = 14 # Controller/switch message.
OFPT_PORT_MOD = 15 # Controller/switch message.
# Statistics messages.
OFPT_STATS_REQUEST = 16 # Controller/switch message.
OFPT_STATS_REPLY = 17 # Controller/switch message.
# Barrier messages.
OFPT_BARRIER_REQUEST = 18 # Controller/switch message.
OFPT_BARRIER_REPLY = 19 # Controller/switch message.
# Queue Configuration messages.
OFPT_QUEUE_GET_CONFIG_REQUEST = 20 # Controller/switch message.
OFPT_QUEUE_GET_CONFIG_REPLY = 21 # Controller/switch message.

# Process command-line arguments
argParser = argparse.ArgumentParser(description='Checks for Openflow-based service')
argParser.add_argument('-v','--version', action='version', version='%(prog)s is at version 1.0.0')
argParser.add_argument('targets', type=str, help='Text file containing the addresses to check')
argParser.add_argument('-p','--port', default=6633,type=int, help='Openflow port')
arguments = argParser.parse_args()

if arguments.targets != None:

	#
	for ip in fileinput.input([arguments.targets]):
		# Check for Openflow service on TCP port 6633

		#
		try:
			client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client_socket.connect((ip, arguments.port))	

			# Build Hello
			type = OFPT_HELLO
			length = OFP_HEADER_LENGTH
			xid = 0
			header = struct.pack(OFP_HEADER_FORMAT, OFP_VERSION_1_0_0, type, length, xid)
			client_socket.send(header)

			# Listen for response ...
			data = client_socket.recv(512)

			# Next, Check to make sure data was returned before processing
			if len(data) !=0:

				#
				version, msg_type, msg_length, xid = struct.unpack(OFP_HEADER_FORMAT, data[:8])

				#
				if msg_type == OFPT_HELLO:
					print('Openflow service (Version: %i) found at %s' % (version,ip))

			client_socket.close()

		except socket.error:
			pass

	print('Finished checks!')