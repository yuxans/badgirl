#!/usr/bin/env python
# -*- coding:gbk -*-

# Copyright (C) 2005 by FKtPp
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

import re, httplib, HTMLParser
#from moobot_module import MooBotModule

# Without this, the HTMLParser won't accept Chinese attribute values
HTMLParser.attrfind=re.compile(
               r'\s*([a-zA-Z_][-.:a-zA-Z_0-9]*)(\s*=\s*'
               r'(\'[^\']*\'|"[^"]*"|[^ <>]*))?')

class WeatherCNParser(HTMLParser.HTMLParser):
	"""A customized HTMLParser to parse the weathercn weather forecast pages

	It parse the forecast page and result a list of result string suitable for
	the MooBot output function. REMEMBER TO IGNORE HTMLParser.HTMLParseError
	SO THAT YOU CAN PROCESS THAT MALFORMED PAGE
	"""

	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.ruler = 0
		self.city = ""
		self.we = []
		self.temp = ""
		self.wind = ""
		self.daterange =""
		self.result_list = []

	def handle_starttag(self, tag, attrs):
		if self.ruler < 120:
			pass
		elif self.ruler > 171:
			pass
		else:
			if tag == "strong":
				self.ruler += 1
			if tag not in ["table", "td", "img"]:
				pass
			else:
				for n, v in attrs:
					if n == "width" and tag == "table":
						if v == "189":
							self.ruler = 130
						elif v == "294":
							self.ruler = 160
					elif n == "width" and tag == "td":
						if v == "182":
							self.ruler = 140
					elif n == "class" and tag == "td":
						if v == "eng":
							self.ruler = 150
					elif n == "src" and tag == "img":
						if v == "image/1.gif":
							self.ruler = 170
					elif n == "alt" and tag == "img":
							self.we.append(v)

	def handle_endtag(self, tag):
		if self.ruler > 171:
			pass
		else:
			if tag == "strong":
				self.ruler += 2
			elif tag == "td":
				self.ruler += 1

	def handle_data(self, data):
		if self.ruler < 24:
			pass
		elif self.ruler > 171:
			pass
		else:
			if data == "CAL();":
				self.ruler = 120
			elif self.ruler == 131:
				self.city = data.strip('{}')
			elif self.ruler == 150:
				self.temp = data
			elif self.ruler == 161:
				self.daterange = data
			elif self.ruler == 171:
				self.wind = data
#		print self.ruler
#		print data.encode("gbk")

	def o(self):
		self.we = u'转'.join(self.we)
		self.result_list.append(self.city)
		self.result_list.append(self.daterange)
		self.result_list.append(self.we)
		self.result_list.append(self.wind)
		self.temp = "".join((u'气温：', self.temp))
		self.result_list.append(self.temp)
		return self.result_list

if __name__ == "__main__":
	p = WeatherCNParser()
	f = file("weather.html", "r")
	try:
		p.feed(f.read().decode("gbk"))
	except HTMLParser.HTMLParseError:
		pass
	print " | ".join(p.o()).encode("gbk")

# vim:ts=4:sw=4:tw=80

