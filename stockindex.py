# grabs stock index quotes

# Copyright (c) 2002 Brett Kelly
# Copyright (C) 2004 by FKtPp
# Copyright (C) 2004 by aster
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
handler_list = ["stockIndex"]

class stockIndex(MooBotModule):
	def __init__(self):
		self.regex="^stockindex"

	def handler(self, **args):
		from irclib import Event
		target = self.return_to_sender(args)

		import urllib2, string, sys, re
		symbols = args["text"].split()
		if len(symbols) <= 2:
			symbol = ""
		else:
			symbol = symbols[2]

		indexList = [ "SSEC", "SZSA" ]
		indexDict = { "SSEC" : ['http://cn.finance.yahoo.com/d/quotes.csv?s=^SSEC&f=sl1d1t1c1ohgv&e=.csv', "\"^SSEC\"", "SSEC"] ,
			"SZSA": ['http://cn.finance.yahoo.com/d/quotes.csv?s=^SZSA&f=sl1d1t1c1ohgv&e=.csv', "\"^SZSA\"", "SZSA"]
			}

		quote = ""
		for i in indexList:
			if i == symbol:
				quote = self.getIndexQuote( indexDict[i][0], indexDict[i][1], indexDict[i][2] )
		if quote == "":
			quote = "Usage: ~stockindex SSEC | SZSA"
		return Event("privmsg", "", target, [quote])
	def getIndexQuote(self, url, matchname, name):
		import urllib2, string, sys, re

		try:
			quote = urllib2.urlopen(url).read()
		except Exception, e:
			self.debug(e)
			quote = "Data source error."
			sys.exit()
		splitquote = quote.split(',')
		if splitquote[0] == matchname:
			quote = "%s %s %s index is %s, volume is %s kilo hands" % (splitquote[2], splitquote[3], name, splitquote[1], splitquote[8])
		else:
			quote = "Data format error."
		return quote


