# grabs stock quotes

# Copyright (c) 2002 Brett Kelly
# Copyright (C) 2004 by FKtPp
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
handler_list = ["stockQuote"]

class stockQuote(MooBotModule):
	def __init__(self):
		self.regex="^stockquote .+"

	def handler(self, **args):
		from irclib import Event 
		target = self.return_to_sender(args)

		import urllib2, string, sys, re
		symbol = args["text"].split()[2]

		ss = re.compile('^6\d{5}')
		sz = re.compile('^0\d{5}')
		flg = 0
		if ss.match(symbol):
			mode = '&m=c'
		elif sz.match(symbol):
			mode = '&m=z'
		else:
			flg = 1
			quote = "Please use formal STOCK ID to query, exp. 600000 or 000001"
		if flg == 0:
			newsymbol = symbol.upper()
			base = 'http://cn.finance.yahoo.com/d/quotes.csv?s='
			tail = '&f=nsl1d1t1c1ohgv&e=.csv' 
			url = base+symbol+mode+tail 
			try:    
				quote = urllib2.urlopen(url).read()
			except Exception, e:
				print e
				sys.exit()
			splitquote = quote.split(',')
			if splitquote[1] != "0.00":    
				quote = "The current price of %s(%s) is %s" % (splitquote[0].strip('"').rstrip(), (splitquote[1])[1:-4] , splitquote[2])
			else:
				quote = "Sorry, I couldn't find that one"
		return Event("privmsg", "", target, [quote])
