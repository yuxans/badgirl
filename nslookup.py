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



from moobot_module import MooBotModule
""" nslookup.py - resolves a host name """
handler_list = ["nslookup"]

class nslookup(MooBotModule):
	def __init__(self):
		self.regex="^d?nslookup .+"

	def handler(self, **args):
		"""Does domain name lookups or reverse lookups on IPs"""
		import socket, re

		host = args["text"].split()
		host = host[2]

		if re.compile("\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}").match(host):
			hostname = socket.getfqdn(host)
			if hostname == host:
				hostname = "Host not found"
		else:
			try:
				hostname = socket.gethostbyname(host)
			except:
				hostname = "Host not found"

		target = self.return_to_sender(args)
#		target = args["channel"]
#		if args["type"] == "privmsg":
#			from irclib import nm_to_n
#			target = nm_to_n(args["source"])


		from irclib import Event
		result = Event("privmsg", "", target, [ hostname ])
		return result
