#!/usr/bin/env python

# Copyright (c) 2002 Brad Kester
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

"""eightball.py - moobot eightball fortune dispensing module fun for the whole
				  family

eightball
"""
handler_list=["eightball"]
from moobot_module import MooBotModule

class eightball(MooBotModule):
	def __init__(self):
		self.regex = "^8ball .+"

	def handler(self, **args):
		"""provides a fanciful and wonderful fortune for the
	   	not-so-fortunate
		"""
		self.debug("eightball", args["text"])
		import string
		from irclib import Event
	
		args["text"] = stripTextHeader(args["text"])
	
		if len(args["text"]) > 0:
			if string.find(args["text"], '?') != -1:
				if len(args["text"]) == 1:
					line = 'Just enter the yes/no question, followed by a ' + \
					   	'question mark, and I\'ll give you a prediction.'
				else:
					line = makeline("8ball")
			else:
				line = 'Without a question mark, how do I know it\'s in the' + \
				   	' form of a question?'
		else:
			# They didn't put anything
			line = 'Ahhhhhhhhhhhhhhhhhhhh!'
	
		return  Event("privmsg", "", self.return_to_sender(args), [ line ])


def makeline(type):
	"""eightball.  usage:  Moobot:  eightball <question>?"""
	import database

	if database.type == "mysql":
		line = database.doSQL("select data from data where type='" + \
			   type + "' order by rand() limit 1")[0][0]
	elif database.type == "pgsql":
		line = database.doSQL("select data from data where type='" + \
			   type + "' order by random() limit 1")[0][0]

	return line

def stripTextHeader(text):
	"""strips off the moobot: and 8ball thingie
	"""
	import string
	text = text[string.find(text, "8ball")+5:]
	while text[0] == ' ':
	  text = text[1:]

	return text
