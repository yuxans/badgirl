# grabs stock quotes

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

from moobot_module import MooBotModule
handler_list = ["stockQuote"]

class stockQuote(MooBotModule):
	def __init__(self):
		self.regex="^stockquote .+"

	def handler(self, **args):
		from irclib import Event 
		target = self.return_to_sender(args)

		import urllib2, sys
		symbol = args["text"].split()[2]
		base = 'http://finance.yahoo.com/d/quotes.csv?s=' 
		tail = '&f=sl1d1t1c1ohgv&e=.csv' 
		url = base+symbol+tail 
		try:    
			quote = urllib2.urlopen(url).read()
		except Exception, e:
			print e
			sys.exit()
		splitquote = quote.split(',')
		if splitquote[1] != "0.00":    
			quote = "The current price per share of %s is $%s" % ((splitquote[0])[1:-1] , splitquote[1])
		else:
			quote = "Sorry, I couldn't find that one"
		return Event("privmsg", "", target, [quote])
