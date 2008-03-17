# Copyright (c) 2002 Daniel DiPaolo
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
handler_list = ["tell"]


class tell(MooBotModule):
	"""Used to tell another user about a factoid.
Invoked with something like: "moobot: tell sweede about foo sucks

"sweede" is the IRC user to tell in a /msg
"foo sucks" is the factoid text to tell them

Also, now with "faketell" - if you have the right privileges, you can pretend
that you are someone else (your bot), and speak through them!  Used the same
way as normal tell, but with "faketell" instead."""
	def __init__(self):
		self.regex="^(fake)?tell .+ about .+"

	def handler(self, **args):
		import database, priv

		from irclib import Event, nm_to_n
		# The target will always be a privmsg, and always to the person
		# we are telling it to.
		target = args["text"].split()[2]
		sender = nm_to_n(args["source"])
	
		# Check if this is faketell or not
		faketell = 0
		if args["text"].split()[1] == "faketell":
			if priv.checkPriv(args["source"], "faketell_priv"):
				faketell = 1
	
		# Get the factoid
		factoid_key = "".join(args["text"].split()[4:])
	
		# Check if it exists first
		count_query = "select count(factoid_key) from" \
			+ " factoids where lower(factoid_key) = '" + factoid_key.lower() + "'"
		count = database.doSQL(count_query)[0][0]
		if count == 0:
			# Send the sender a message that it doesn't exist
			target = sender
			message = "Factoid '" + factoid_key + "' does not exist"
			return Event("privmsg", "", target, [message])
	
		# Grab it and parse it
		factoid_query = "select factoid_value from factoids where" \
			+ " lower(factoid_key) = '" + factoid_key.lower() + "'"
		factoid = self.parse_sar(database.doSQL(factoid_query)[0][0])
		# Replace $who and $nick with the target
		factoid = factoid.replace("$who", target)
		factoid = factoid.replace("$nick", target)
	
		# If the factoid begins with <reply> then just tell it to them
		# otherwise, tell them what factoid and who sent it
		if faketell:
			if factoid.lower()[:7] == "<reply>":
				message = factoid[7:]
			else:
				message = factoid_key + " is " + factoid
		else:
			if factoid.lower()[:7] == "<reply>":
				factoid = factoid[7:]
				message = sender + " wanted you to know: " + factoid
			else:
				message = sender + " wanted you to know: " + factoid_key \
					+ " is " + factoid
	
		return Event("privmsg", "", target, [message])

	def parse_sar(self, text):
		import random
		stack = []
		# continue as long as text still has stuff in it
		while len(text) > 0:
			# get the first token from text
			token = self.get_token(text)
			# remove that token from text
			text = text[len(token):]
			# if the token is a ) and there is a ( in stack,
			# pop every element up to and including the (,
			# then chose one of those elements and append it
			# to stack.
			if token == ")" and "(" in stack and "|" in stack[stack.index('('):]:
				choices = []
				while stack[-1] != "(":
					choices.append(stack.pop())
				stack.pop()
				chosen="|"
				while chosen == "|":
					chosen = random.choice(choices)
				if len(stack) > 0:
					if stack[-1] != "(" and stack[-1] != "|":
						stack.append(stack.pop() + chosen)
					else:
						stack.append(chosen)
				else:
					stack.append(chosen)
			elif token == "|":
				stack.append(token)
				if len(text) and (text[0] == "|" or text[0] == ")"):
					stack.append("")
			else:
				if len(stack) == 0 or stack[-1] == "|" or stack[-1] == "(" or token == "(":
					stack.append(token)
				else:
					stack.append(stack.pop() + token)
		return "".join(stack)

	def get_token(self, text):
			""" gets the next token for SAR parsing from text """
			# Basically, this returns either:
			#  * one of the special_chars if it is the first character
			#  * otherwise, the string of non-special chars leading up
			#    to the first special char in the string
			special_chars = "()|"
			for length in range(len(text)):
					if text[length] in special_chars:
							# If we already have a string of chars going, back
							# up one and return that, we don't want to include
							# the special character we are currently on
							if length > 0:
									length -= 1
							# Once we hit a special character, break out of the
							# for loop so we can return
							break
			return text[:length+1]
