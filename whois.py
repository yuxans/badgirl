#!/usr/bin/env python

# Copyright (C) 2004 by FKtPp
# Copyright (C) 2004 by baa
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
""" whois.py - whois module for moobot"""
handler_list = ["whois"]

class whois(MooBotModule):
	def __init__(self):
		self.regex="^d?whois .+"

	def handler(self, **args):
		"""TODO. only query from Asia Pacific Network Infomation Center, need fix"""
		import socket, string, re

		HOST = 'whois.apnic.net'
		PORT = 43
		alldata = ''

		myquery = args["text"].split()
		myquery = myquery[2]

		if re.compile('\d{1,3}(\.\d{1,3}){0,3}').match(myquery):
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST, PORT))
			s.send(myquery+"\r\n")

			while 1:
				data = s.recv(1024)
				if not data: break
				alldata += data
			s.close()

			alldata = alldata.split("\n")

			data = ''
			dataelement = ''
			dones = {}
			pt = re.compile('^(inetnum|netname|country|descr):')

			for dataelement in alldata:
				m = pt.match(dataelement)
				if m:
					k = m.group(1)
					if not dones.has_key(k):
						dones[k] = 1
						data += "\r\n" + unicode(dataelement, 'hz').encode('gbk')
		else:
			data = "Sorry, I can only query IP ADDRESS for you."

		from irclib import Event
		target = self.return_to_sender(args)
		result = Event("privmsg", "", target, [ data ])
		return result

