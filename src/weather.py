#!/usr/bin/env python
# -*- coding:gb2312 -*-

# Copyright (C) 2005, 2006, 2007 by FKtPp
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

import re, HTMLParser
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
		self.city_re = re.compile(u'\{.*\}')
		self.city = ""
		self.we = []
		self.temp = ""
		self.temp_re = re.compile(u'^\d+℃')
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
						if v == "294":
							self.ruler = 160
					elif n == "src" and tag == "img":
						if v == "image/1.gif":
							self.ruler = 170
					elif n == "alt" and tag == "img":
							self.we.append(v)
							self.ruler = 150

	def handle_endtag(self, tag):
		if self.ruler > 171:
			pass
		else:
			if tag == "strong":
				self.ruler += 2
			elif tag == "td":
				self.ruler += 1

	def handle_data(self, data):
		if self.ruler > 171:
			pass
		else:
			if self.ruler < 120 and data == "CAL();":
				self.ruler = 120
			elif self.ruler < 130 and self.city_re.match(data):
				self.city = data.strip('{}')
				self.ruler = 130
			elif self.ruler >= 150 and self.temp_re.match(data):
				self.temp = data
			elif self.ruler == 161:
				self.daterange = data
			elif self.ruler == 171:
				self.wind = data
#		print self.ruler
#		print data.encode("gbk")

	def o(self):
		if self.we:
			self.we = u'转'.join(self.we)
			self.result_list.append(self.city)
			self.result_list.append(self.daterange)
			self.result_list.append(self.we)
			self.result_list.append(self.wind)
			self.temp = "".join((u'气温：', self.temp))
			self.result_list.append(self.temp)
		else:
			self.result_list.append(u'无')
			self.result_list.append(self.city)
			self.result_list.append(u'预报信息')
		return self.result_list


class WeatherCNCITYParser(HTMLParser.HTMLParser):
	"""A customized HTMLParser to parse the weathercn weather citylist pages

	It parse the citylist page and result a list of (city, url) turples to be
	used to fetch weather forecast page. REMEMBER TO IGNORE HTMLParser.HTMLParseError
	SO THAT YOU CAN PROCESS THAT MALFORMED PAGE
	"""

	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.satisfy = 0
		self.city = ""
		self.url = ""
		self.result_list = []

	def handle_starttag(self, tag, attrs):
		if tag not in ["a", "span"]:
			pass
		else:
			tmpurl = ""

			for n, v in attrs:
				if n == "class" and v == "font_sl":
					if tag == "a":
						self.satisfy = 1
					else:
						self.satisfy += 1
				elif n == "href":
					tmpurl = v

			if tmpurl.strip() and self.satisfy == 1:
				self.url = tmpurl

	def handle_endtag(self, tag):
		if tag not in ["a", "span", "td"]:
			pass
		else:
			if self.satisfy == 3 and tag == "span":
				self.satisfy += 1
			elif self.satisfy == 4 and tag == "a":
				self.satisfy += 1
			elif self.satisfy == 6 and tag == "td":
				self.satisfy = 0
				self.result_list.append((self.city , self.url))
			else:
				pass

	def handle_data(self, data):
		if self.satisfy == 2:
			self.city = data
			self.satisfy += 1
		elif self.satisfy == 5:
			self.city = "".join((self.city, data))
			self.satisfy += 1
		else:
			pass

	def o(self):
		return self.result_list

if __name__ == "__main__":
	p = WeatherCNParser()
	f = file("test.html", "r")
	try:
		p.feed(f.read().decode("gbk"))
	except HTMLParser.HTMLParseError:
		pass
	for c in p.o():
		print ''.join((c, '<>'))

# 	pc = WeatherCNCITYParser()
# 	f = file("test.html", "r")
# 	try:
# 		pc.feed(f.read().decode("gbk"))
# 	except HTMLParser.HTMLParseError:
# 		pass
# 	for c, u in pc.o():
# 		print c
# 		print u


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

