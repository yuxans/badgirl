#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (C) 2007 by FKtPp
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#


import re, httplib
from irclib import Event
from moobot_module import MooBotModule

handler_list = ['chunzhen',]

class chunzhen(MooBotModule):
	"""Get geographic location infomation of specific IP address from web.

	Query the infomation from http://www.cz88.net/ server, and pasre,
	print the result.
	"""
    
	def __init__(self):
		"""
		>>> import re, geoip
		>>> a = geoip.chunzhen()
		>>> r = re.compile(a.regex)
		>>> r.match('geoip ') and True or False
		False
		>>> r.match('geoip a') and True or False
		False
		>>> r.match('geoip a.') and True or False
		False
		>>> r.match('geoip a.b') and True or False
		False
		>>> r.match('geoip 1') and True or False
		False
		>>> r.match('geoip 1.') and True or False
		False
		>>> r.match('geoip 1.0') and True or False
		True
		>>> r.match('geoip 1.1') and True or False
		True
		>>> r.match('geoip 1.1.0') and True or False
		True
		>>> r.match('geoip 1.1.1') and True or False
		True
		>>> r.match('geoip 1.1.1.1') and True or False
		True
		>>> r.match('geoip 1.0.0.1') and True or False
		True
		>>> r.match('geoip 1.1.1.1.1') and True or False
		False
		>>> r.match('geoip 255.1.1.1') and True or False
		False
		>>> r.match('geoip 1.255.1.1') and True or False
		False
		>>> r.match('geoip 1.1.255.1') and True or False
		False
		>>> r.match('geoip 1.1.1.255') and True or False
		False
		>>> r.match('geoip 1.1.1.0') and True or False
		False
		>>> r.match('geoip 0.1.1.1') and True or False
		False
		>>> r.match('geoip 1.1.1.a') and True or False
		False
		>>> 
		"""
		# ipv4 pattern initialization
		num0_254 = '(?:25[0-4]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]?|0)'
		num1_254 = '(?:25[0-4]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]?)'
		ipv4part = '(?:%s(?:\.%s){1,2}(?:\.%s)?)' % (num1_254,
		                                             num0_254,
		                                             num1_254)

		self.regex='^geoip\s+%s$' % (ipv4part)

	def handler(self, **args):
		query_str = args["text"].split()
		query_str = query_str[2].strip()
		target = self.return_to_sender(args)
		result = Event('privmsg', '', target, [ ''.join((query_str, ': ', self.query(query_str)))])

		return result

	rAddr = re.compile('id="InputIPAddrMessage">(.*?)</span')
	rTags = re.compile("<[^>]*>")
	def query(self, ip):
		ip = self.fixipv4(ip)
		getParams = "ip=" + ip

		headers = {
			'User-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
			'Referer': 'http://www.cz88.net/'
		}
		request = httplib.HTTPConnection('www.cz88.net', 80)
		request.timeout = 5.1
		request.request("GET", "/ip/default.aspx?ip=%s" % ip, '', headers)
		response = request.getresponse()
		if response.status != 200:
			return "error %s" % response.status

		response = response.read().decode("gbk")

		match = self.rAddr.search(response)
		if not match:
			return "not found"
		address = match.group(1)
		return self.rTags.sub("", address).strip()

	def fixipv4(self, ipv4string):
		"""fill the 3, 4 part of a particalarly typed ip address.

		fill '.0.1' if it has only two parts, fill '.1' if it has
		three parts, do nothing if it has all the four parts.

		>>> import geoip
		>>> a = geoip.chunzhen()
		>>> a.fixipv4('192.168')
		'192.168.0.1'
		>>> a.fixipv4('192.168.2')
		'192.168.2.1'
		>>> a.fixipv4('192.168.2.22')
		'192.168.2.22'
		>>> 
		"""

		parts = ipv4string.split('.')
		
		l = len(parts)

		if l == 2:
			parts.extend(['0','1'])
		elif l == 3:
			parts.extend(['1'])
		elif l == 4:
			pass
		else:
			# IP Error, length must be 2, 3, 4 or regexp must be wrong
			assert False
		
		return '.'.join(parts)

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()
