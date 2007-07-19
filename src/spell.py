#!/usr/bin/env python

# Copyright (c) 2002 Brad Stewart
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
handler_list=["spell"]


class spell(MooBotModule):
	""" spell.py -- spell checking """
	def __init__(self):
		self.regex = "^spell [A-Za-z]+$" # DO NOT change this, letting things
						# other than letters in could create
						# a security hole

	def handler(self, **args):
		""" checks spelling """
		from irclib import Event	
		import os
		target = self.return_to_sender(args)
	
		word = args["text"].split()[2]
		if os.access("/usr/bin/aspell", os.F_OK) != 1:
			result = Event("privmsg", "", target, [ "Error:  aspell not found" ])
		text = os.popen("echo " + word + " | /usr/bin/aspell pipe -S").read()
		if text.split("\n")[1][0] in "*+":
			message = word + " may be spelled correctly."
		elif text.split("\n")[1][0] == "#":
			message = "could not find alternate spelling for " + word
		elif text.split("\n")[1][0] == "&":
			message = "Possible spellings for " + word + ":" + text.split("\n")[1].split(":")[1]
			
		else:
			message = "something wierd happened."

		result = Event("privmsg", "", target, [ message ])
		return result
