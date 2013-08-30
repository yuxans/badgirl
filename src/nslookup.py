#!/usr/bin/env python

# Copyright (c) 2002 Vincent Foley
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

import socket

def isValidateIp(ip):
	try:
		socket.inet_pton(socket.AF_INET, ip)
		return True
	except socket.error:
		pass
	
	try:
		socket.inet_pton(socket.AF_INET6, ip)
		return True
	except socket.error:
		pass
	
	return False

from moobot_module import MooBotModule
""" nslookup.py - resolves a host name or ip """
handler_list = ["nslookup"]

class nslookup(MooBotModule):
	def __init__(self):
		self.regex="^(?:d?nslookup|dns) .+"

	def handler(self, **args):
		"""Does domain name lookups or reverse lookups on IPs"""
		import socket, re

		query = args["text"].split()[2]

		if isValidateIp(query):
			result = socket.getfqdn(query)
			if result == query:
				result = "FQDN not found"
		else:
			try:
				result = ""
				for addressInfo in socket.getaddrinfo(query, 0, 0, 0, socket.SOL_TCP):
					result = result + " " + addressInfo[4][0]
				result = result.strip()
			except Exception, e:
				result = "Host lookup error: " + str(e)


		target = self.return_to_sender(args)
#		target = args["channel"]
#		if args["type"] == "privmsg":
#			from irclib import nm_to_n
#			target = nm_to_n(args["source"])


		from irclib import Event
		result = Event("privmsg", "", target, [ query + ": " + result ])
		return result
