# grabs stock quotes

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

from moobot_module import MooBotModule
import re
handler_list = ["stockQuote"]

class stockQuote(MooBotModule):

	ss = re.compile('^600\d{3}')
	sz = re.compile('^000\d{3}')

	def __init__(self):
		self.regex="^(em|stockquote) .+"

	def handler(self, **args):
		from irclib import Event 
		target = self.return_to_sender(args)
		requested_code = args["text"].split()[2]
		quote_method = args["text"].split()[1]
		
		if quote_method == "stockquote":
			quote = self.quote_cn_yahoo(requested_code)
		else:
			quote = self.eastmoney(requested_code)
		return Event("privmsg", "", target, [quote])

	def quote_cn_yahoo(self, symbol):
		import urllib2, string, sys

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
			result = "The current price of %s(%s) is %s" % (splitquote[0].strip('"').rstrip(), (splitquote[1])[1:-4] , splitquote[2])
		else:
			result = "Sorry, I couldn't find that one"

		return result

	def eastmoney(self, symbol):

		err_msg =  "Please use formal STOCK ID to query, exp. 600000 or 000001. Or you can view this link http://quote.eastmoney.com/q.asp?StockCode=%s" % symbol
		if not (self.ss.match(symbol) or self.sz.match(symbol)):
			return err_msg
		import httplib, urllib
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
			# construct the result message
			# example.
			# ,------( stockname[code] )
			# | blah blah blah
			# | foo bar
			# `------
			from HTMLParser2 import HTMLParser
			class myp(HTMLParser):
				"test class"
				ignore_data = True
				data_list = []
				result = ""
				__newline = "\r\n| "
				__data_length = 25

				def handle_starttag(self, tag, attrs):
					tag = tag.lower()
					if tag == "script":
						self.ignore_data = True

				def handle_data(self, data):
					emptyre = re.compile("^\s*\r\n")
					if  not self.ignore_data:
						if len(self.data_list) >= self.__data_length:
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
					result = self.result
					result += ",------( %s )" % self.data_list[0] + self.__newline
					i = 1
					while i < self.__data_length - 1:
						if i % 4 != 0:
							if i % 2 != 0:
								result += self.data_list[i].ljust(6)
							else:
								result += self.data_list[i].rjust(8) + "     "
						else:
							result += self.data_list[i].rjust(8) + self.__newline
						i += 1
					result +=  self.data_list[self.__data_length - 1].rjust(8) + "\r\n`------"
					return result

			err_re = re.compile(".*您输入的股票代码错误!.*".decode("gbk", "replace"))
			html = response.read().decode("gbk", "replace")
			if err_re.search(html):
				return err_msg
			else:
				# parse the response html page
				p = myp()
				p.feed(html)
				return p.get_result()
