#!/usr/bin/env python

# Copyright (C) 2005 by FKtPp
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

"""RssQuery.py - query manage rssfeeds""" 
from moobot_module import MooBotModule
handler_list=["RssQuery"]

class cool(MooBotModule):
	def __init__(self):
		self.regex = "^rss .+"

	def handler(self, **args):
		"""
		TODO.
		commandline summarys:
		rss shortcut ---- query rss feeds
		rss [-a|--assign] foo http://foo.bar/foo/bar/foo.rss ---- asssign uri shortcuts.
		rss [-u|--uri[=]] http://foo.bar/foo/bar/foo.rdf ----query uri
		rss -l|--list [keywords] ---- list assigned rss feeds match the keywords or if keywords not present list all rss feeds.
		rss -r|--remove shortcut
		
		from RSS import ns, CollectionChannel, TrackingChannel

#Create a tracking channel, which is a data structure that
#Indexes RSS data by item URL
tc = TrackingChannel()

#Returns the RSSParser instance used, which can usually be ignored
tc.parse("http://www.python.org/channews.rdf")

RSS10_TITLE = (ns.rss10, 'title')
RSS10_DESC = (ns.rss10, 'description')

#You can also use tc.keys()
items = tc.listItems()
for item in items:
	#Each item is a (url, order_index) tuple
	url = item[0]
	print "RSS Item:", url
	#Get all the data for the item as a Python dictionary
	item_data = tc.getItem(item)
	print "Title:", item_data.get(RSS10_TITLE, "(none)")
	print "Description:", item_data.get(RSS10_DESC, "(none)")
	
		"""
		import string
		from irclib import Event

		# Split the string and take every word after the first two as the
		# words to "cool-ify" (first two are the bot name and "cool")
		who = string.join(args["text"].split(" ")[2:])

		# Surround whatever with ":cool:" tags
		text = ":cool: " + who + " :cool:"

		target = self.return_to_sender(args)
		result = Event("privmsg", "", target, [ text ])
       		return result

	def parse_args(self, *args):
		"""parse the argument line acroding the following switchs

		-u --uri	uri to query
		-l --list	list assigned shorts
		-h --help	display help message
		-a --assign	assign a RSS feed uri to a shortcut
		-r --remove	remove shortcut from database

		Returns None if encounter a help request, otherwise, returns a map of {"server":SERVER_STRING, "port":PORT_STRING, "query":QUERY_STRING} form. SERVER_STRING or PORT_STRING or QUERY_STRING will be None if not set in the argument line"""
		import getopt
		TempMap = {"server":None, "port":None, "query":None}
		argv = args.split()[2:]
		try:
			optlist, argv = getopt.getopt(argv, 'u:l:ha:r:', ["help", "uri=", "list=", "assign=", "remove="])
# 			for o, a in optlist:
# 				if o in ("-h", "--help"):
# 					return None
# 				if o in ("-u", "--uri"):

# 				if o in ("-p", "--port"):


			
		except GetoptError:
			debug(argv.[2])
		# return something

