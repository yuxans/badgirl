#!/usr/bin/env python

# Copyright (c) 2002 Keith Jones
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

"""stack.py - a simple stack 
stack functionality on input ^stack\s+(push\s.*|pop|xray)" """

from moobot_module import MooBotModule
handler_list = ["stack"]


class stack(MooBotModule):
	def __init__(self):
		""" stack functionality on input ^stack\s+(push\s.*|pop|xray\s\d+)" """
		
		self.regex="^stack\s+(push\s.*|pop|size|xray\s\d+)"
		self.stack = []

	def handler(self, **args):
		from irclib import Event

		
		message = 'invalid stack command'
		words = args['text'].split()
		try:
			cmd = words[2].lower()
		except IndexError:
			cmd = 'none'

		try:
			item = "".join(words[3:])
		except IndexError:
			item = 'none'
		
		if cmd == 'pop':
			if self.stack == []:
				message = 'Stack is empty'
			else:
				message = self.stack.pop()
		
		elif cmd == 'push':
			self.stack.append(item)
			message = '"%s" pushed' % item

		elif cmd == 'xray':
			try: 
				item = item.strip()
				pos = int(item)
				message = self.stack[-pos]
			except ValueError:
				message = "Invalid position: " + "'" + item + "'"
			except IndexError:
				message = "Invalid position: " + "'" + item + "'"

		elif cmd == 'size':
			message = 'stack size is: ' + str(len(self.stack))
			
		return Event("privmsg", "", self.return_to_sender(args), [ message ])
