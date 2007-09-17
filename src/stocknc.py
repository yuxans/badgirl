# grabs stock quotes
# -*- coding:gbk -*-

# Copyright (C) 2004, 2005, 2006, 2007 by FKtPp, moo
# Copyright (c) 2002 Brett Kelly
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

import re
import sys
import urllib
import httplib
import HTMLParser
import sina_finance
from irclib import Event 
from moobot_module import MooBotModule

handler_list = ["stockQuote", "sinaFinance"]

class stockQuote(MooBotModule):

	ss = re.compile('^60\d{4}')
	sz = re.compile('^00\d{4}')

	def __init__(self):
		self.regex="^(em|stockquote) .+"

	def handler(self, **args):
		target = self.return_to_sender(args)
		requested_code = args["text"].split()[2]
		quote_method = args["text"].split()[1]

		quote = self.eastmoney(requested_code,
                                       self.long_short(target))

		return Event("privmsg", "", target, [quote])

	def long_short(self, target):
		default_short = True
		if not re.compile("^#.*").match(target):
			default_short = False
		return default_short

	def eastmoney(self, symbol, short_style):
		err_msg =  "Please use formal STOCK ID to query, exp. 600000 or 000001. Or you can view this link http://quote.eastmoney.com/q.asp?StockCode=%s" % symbol

		if not (self.ss.match(symbol) or self.sz.match(symbol)):
			return err_msg

		# construct and send the query
		params = urllib.urlencode({"StockCode": symbol.encode("gbk")})
		headers = {"Content-type": "application/x-www-form-urlencoded",
		"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0)",
		"Accept-Encoding": ""}
		em_con = httplib.HTTPConnection('quote2.eastmoney.com', 80)
		em_con.request("POST", "/q.asp", params, headers)
		response = em_con.getresponse()
		if response.status != 200:
			return response.reason
		else:
			err_re = re.compile(".*您输入的股票代码错误!.*".decode('gbk','replace'))
			html = response.read().decode("gbk", "replace")
			if err_re.search(html):
				return err_msg
			else:
				p = myp()
				p.feed(html)
				return short_style \
				    and self.output_short(p.get_result()) \
				    or self.output_long(p.get_result())

	def output_long(self, data_list):
		__newline = "\r\n | "
		__data_length = 25
		result = " ,------( %s )" % data_list[0]
		result += __newline
		i = 1
		while i < __data_length - 1:
			column = i % 4
			if column == 1:
				result += data_list[i].ljust(6)
			elif column == 2:
				result += data_list[i].rjust(8)
				result += "     "
			elif column == 3:
				result += data_list[i].ljust(6)
			else:
				result += data_list[i].rjust(8)
				result += __newline
			i += 1
		result +=  data_list[__data_length - 1].rjust(8)
		result += "\r\n `------"
		return result

	def output_short(self, data_list):
		result = data_list[0]
		result += "：%s".decode('gbk','replace') % data_list[2]
		if '-' in data_list[6]:
			result += "↓%s(%s)".decode('gbk','replace')
		else:
			result += "↑%s(%s)".decode('gbk','replace')
		result = result % (data_list[6], data_list[10])
		return result

# Without this, the HTMLParser won't accept Chinese attribute values
HTMLParser.attrfind=re.compile(
		r'\s*([a-zA-Z_][-.:a-zA-Z_0-9]*)(\s*=\s*'
		r'(\'[^\']*\'|"[^"]*"|[^ <>]*))?')

class myp(HTMLParser.HTMLParser):
	"Html Parser for eastmoney quick stockquote"
	
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.ignore_data = True
		self.data_list = []

	def handle_starttag(self, tag, attrs):
		tag = tag.lower()
		if tag == "script":
			self.ignore_data = True

	def handle_data(self, data):
		__data_length = 25
		emptyre = re.compile("^\s*\r\n")
		if  not self.ignore_data:
			if len(self.data_list) >= __data_length:
				self.ignore_data = True
			else:
				if not emptyre.match(data):
					data = data.replace("&nbsp;", " ")
					self.data_list.append(data)

	def handle_endtag(self, tag):
		tag = tag.lower()
		if tag == "script":
			self.ignore_data = False

	def get_result(self):
		return self.data_list

class sinaFinance(MooBotModule):
	def __init__(self):
		self.regex="^sina .+"
		self.sf = sina_finance.SearchEngine()

	def handler(self, **args):
		target = self.return_to_sender(args, 'nick')

		o = self.sf.search(args['text'].split()[2:])

		x = ''
		for i in o:
			x = '\n'.join((x, i.__str__()))

# 		print x

		return Event("notice", "", target, [x.strip() or "Sorry we can't find that :("])
