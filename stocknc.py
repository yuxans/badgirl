# grabs stock quotes
# -*- coding:gbk -*-

# Copyright (c) 2002 Brett Kelly
# Copyright (C) 2004 by FKtPp
# Copyright (C) 2005 by baa
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
import httplib, urllib
import urllib2, string, sys
from irclib import Event 
from HTMLParser2 import HTMLParser
from moobot_module import MooBotModule

handler_list = ["stockQuote"]

class stockQuote(MooBotModule):

	ss = re.compile('^600\d{3}')
	sz = re.compile('^000\d{3}')

	def __init__(self):
		self.regex="^(em|stockquote) .+"

	def handler(self, **args):
		target = self.return_to_sender(args)
		requested_code = args["text"].split()[2]
		quote_method = args["text"].split()[1]
		
		if quote_method == "stockquote":
			quote = self.quote_cn_yahoo(requested_code)
		else:
			quote = self.eastmoney(requested_code, \
					       self.long_short(target))
		return Event("privmsg", "", target, [quote])

	def long_short(self, target):
		default_short = True
		if not re.compile("^#.*").match(target):
			default_short = False
		return default_short

	def quote_cn_yahoo(self, symbol):
		if self.ss.match(symbol):
			mode = '&m=c'
		elif self.sz.match(symbol):
			mode = '&m=z'
		else:
			return "Please use formal STOCK ID to query, exp. 600000 or 000001"

		newsymbol = symbol.encode("gbk").upper()
		base = 'http://cn.finance.yahoo.com/d/quotes.csv?s='
		tail = '&f=nsl1d1t1c1ohgv&e=.csv' 
		url = base+symbol+mode+tail 
		try:    
			quote = urllib2.urlopen(url).read()
		except Exception, e:
			self.debug(e)
			sys.exit()
		splitquote = quote.decode("gbk", "replace").split(',')
		if splitquote[1] != "0.00":    
			result = "The current price of %s(%s) is %s" % \
			    (splitquote[0].strip('"').rstrip(), \
			     (splitquote[1])[1:-4], \
			     splitquote[2])
		else:
			result = "Sorry, I couldn't find that one"

		return result

	def eastmoney(self, symbol, short_style):
		err_msg =  "Please use formal STOCK ID to query, exp. 600000 or 000001. Or you can view this link http://quote.eastmoney.com/q.asp?StockCode=%s" % symbol

		if not (self.ss.match(symbol) or self.sz.match(symbol)):
			return err_msg

		# construct and send the query
		params = urllib.urlencode({"StockCode": symbol.encode("gbk")})
		headers = {"Content-type": "application/x-www-form-urlencoded",
		"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0)",
		"Accept-Encoding": ""}
		em_con = httplib.HTTPConnection('quote.eastmoney.com', 80)
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

class myp(HTMLParser):
	"Html Parser for eastmoney quick stockquote"
	
	def __init__(self):
		HTMLParser.__init__(self)
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
