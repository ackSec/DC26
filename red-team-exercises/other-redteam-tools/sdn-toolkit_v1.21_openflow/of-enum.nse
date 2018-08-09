description = [[
Enumerates Openflow participants.
]]

---
--@output
-- 6633/tcp   open     openflow
-- |_ of-enum: Switch running version 1 version of Openflow
-- 6653/tcp   open     openflow
-- |_ of-enum: Controller running version 1 version of Openflow

author = "Gregory Pickett"
license = "Same as Nmap--See http://nmap.org/book/man-legal.html"
categories = {"default", "discovery", "safe"}

local nmap = require "nmap"
local string = require "string"
local shortport = require "shortport"
local bin = require "bin"

portrule = shortport.portnumber({6633, 6653}, "tcp")

action = function(host, port)

        local participant = ""

		OFP_VERSION_1_0_0 = 0x01
		
		OFPT_HELLO = 0
		OFPT_FEATURES_REQUEST = 5
		
		OFP_HEADER_FORMAT = ">CCSL"
		OFP_HEADER_LENGTH = 8
		
        local client_openflow = nmap.new_socket()

        local catch = function()
                client_openflow:close()
        end

        local try = nmap.new_try(catch)

        try(client_openflow:connect(host.ip, port.number))
		
		messagetype = OFPT_HELLO
		length = OFP_HEADER_LENGTH
		xid = 0
		header = bin.pack(OFP_HEADER_FORMAT, OFP_VERSION_1_0_0, messagetype, length, xid)		
        try(client_openflow:send(header))

		data = try(client_openflow:receive_bytes(16))
		last, version, msg_type, msg_length, xid = bin.unpack(OFP_HEADER_FORMAT, string.sub(data,1,8))

		if string.len(data) == 8 then
		
			port.version.name = "openflow"
			nmap.set_port_version(host, port)
			participant = "Switch running version " .. version .. " of Openflow"
		
		elseif string.len(data) == 16 then
		
			last, version, msg_type, msg_length, xid = bin.unpack(OFP_HEADER_FORMAT, string.sub(data,9,16))

			if msg_type == OFPT_FEATURES_REQUEST then

				port.version.name = "openflow"
				nmap.set_port_version(host, port)
				participant = "Controller running version " .. version .. " of Openflow"
				
			end
		
		end

        try(client_openflow:close())

        return participant
end