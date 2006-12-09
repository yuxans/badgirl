#!/usr/bin/env python

# Copyright (c) 2002 Brad Stewart and Daniel DiPaolo
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

"""factoids.py -- Moobot Factoid Handlers

Includes handlers for factoid lookup and creation
"""
handler_list = ["augment", "cookie", "list_keys", "info", "delete", "lock", "lookup", "replace", "alter", "add"]


from moobot_module import MooBotModule
import database

class factoidClass(MooBotModule):
	"""Base class for all factoid classes, encapsulates a lot of common
	functions into one base class"""
	def strip_words(self, str, num):
		"""Strips a certain number of words from the beginning of a string"""
		import string
		str = string.join(str.split()[num:])
		return str
		
	def strip_punctuation(self, str):
		"""Strips ?s and !s from the end of a string"""
		while len(str) > 1 and (str[-1] == "!" or str[-1] == "?"):
			str = str[:-1]
		return str	

	def return_to_sender(self, args):
		"""Returns target for a given event, assuming we want to return it to
		the sender"""
		from irclib import nm_to_n
		if args["type"] == "privmsg": target = nm_to_n(args["source"])
		else: target = args["channel"]
		return target

	def parse_sar(self, text):
		import random, string
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
			if token == ")" and "(" in stack \
			and "|" in stack[stack.index('('):]:
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
				if len(stack) == 0 or stack[-1] == "|" \
				or stack[-1] == "(" or token == "(":
					stack.append(token)
				else:
					stack.append(stack.pop() + token)
		return string.join(stack, "")

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

	def escape_regex(self, line):
		import string
		line = string.replace(line, "[", "[\[")
		line = string.replace(line, "]", "[\]]")
		line = string.replace(line, "[\[", "[\[]")
		line = string.replace(line, "+", "[+]")
		line = string.replace(line, "*", "[*]")
		line = string.replace(line, ".", "\\.")
		line = string.replace(line, "?", "[?]")
		line = string.replace(line, "{", "[{]")
		line = string.replace(line, "}", "[}]")
		line = string.replace(line, "(", "[(]")
		line = string.replace(line, ")", "[)]")
		line = string.replace(line, "|", "[|]")
		return line


class lookup(factoidClass):
	def __init__(self):
		self.regex = ".+"
		self.priority = 18
	def handler(self, **args):
		""" gets the factoid_value field from the database """
		import string, time
		from irclib import Event, nm_to_n

		# Store the ref
# 		ref = args["ref"]()

		# If we were /msg'ed this, /msg it back, otherwise send it to the
		# channel
		# (set up here because there are some rather early returns for the
		# continue handler types and whatnot)
		target = self.return_to_sender(args)

		factoid_key = args["text"]
		factoid_key = self.strip_words(factoid_key, 1) # removes "moobot: "

		# By default we want to parse the factoid value after grabbing it from
		# the db, but certain flags along the way may set this flag so that we
		# don't do so (e.g., "literal").
		dont_parse = 0

		# If we are called with something like "moobot: literal foo", we want
		# to strip the "literal" from it as that is not part of the
		# factoid, unless of course nothing follows "literal", in which
		# case we would be looking for the factoid for "literal" 
		if len(args["text"].split(" ")) > 1 and \
			args["text"].split(" ")[1] == "literal":
				dont_parse = 1	# set for later, when we spit the value back
				factoid_key = self.strip_words(factoid_key, 1)

		# Strip trailing ?'s and !'s (so asking for "moobot: foo?!?!?!???" is
		# the same as just asking for "moobot: foo" 
		factoid_key = self.strip_punctuation(factoid_key)

		#  Query the database for the factoid value for the given key
		factoid_query = "select factoid_value from factoids "\
				"where (factoid_key) = "\
				"'%s'" % self.sqlEscape(factoid_key.lower())
		list = database.doSQL(factoid_query)

		# If the factoid doesn't exist, tell them, and then continue trying
		# to match with other handlers using the continue event type 
		if len(list) == 0:
			return Event("continue", "", target, [""])
		else:	
			tuple = list[0]

		# Now that we are sure we have a factoid that got requested, increment
		# the count, set the new requester, etc.  NOTE: even for "literal"
		# requests, this is set.  Whether or not this is really is wanted is
		# ... debatable, but we don't really care.
		update_query = "update factoids set "\
			       "requested_count = requested_count + 1, "\
			       "requested_by = '%s', "\
			       "requested_time = %s "\
			       "where (factoid_key) = '%s'" % (
			args["source"], str(int(time.time())),
			self.sqlEscape(factoid_key.lower())
			)

		database.doSQL(update_query)

		# The factoid is just the first field of the one-field tuple we got
		# back from the query earlier
		text = tuple[0]

		### The new length stuff
		# Here we check to see if the total message length would be greater
		# than irclib.MESSAGE_SIZE_LIMIT, and if so, split it up accordingly
		# and return the requested one, or print out a warning.

		# Message format:
		# nickname!username@localhost privmsg #channel_name :factoid_text
# 		self.debug("%s!%s@%s" % (ref.connection.ircname, 
# 			ref.connection.username, ref.connection.localhost))
# #		msg_length = len(text) + len(" privmsg # :") + len(target) + \
# #			len(ref.connection.nickname) + len(ref.connection.username) + \
# #			len(ref.connection.localhost)
# #		self.debug(msg_length)


		# by default we will just say something to the target, but if the
		# factoid contains an <action> tag, we will make it an action
		# eventtype 
		eventtype="privmsg"

		# If the person says something like "moobot: literal foo", we don't
		# want to parse the factoid, we just want to spit it back in its raw
		# form.  Otherwise, we want to replace parentheses and pipes as well
		# as see if we need to change the eventtype 
		if not dont_parse:  # awkward, but supports the more general case,
							# instead of having to set a flag for every case
							# where we DO want to parse, only set a flag where
							# we do NOT parse
			
			# Strip spaces from the left-hand side
			text = string.lstrip(text)

			# Parse parentheses and pipes to come up with one random string
			# from many choices specified in the factoid 
			text = self.parse_sar(text)

			# Replace $who and $nick with the person requesting the factoid
			text = string.replace(text, "$who", nm_to_n(args["source"]))
			text = string.replace(text, "$nick", nm_to_n(args["source"]))

			# If the new string (after previous replacements) begins with
			# "<action>" or "<reply>" (case insensitive), then we strip them
			# and possibly change the eventtype if necessary.  Otherwise, we
			# simply say "foo is bar" back to the target. 
			if text[:8].lower() == "<action>":
				eventtype="action"
				text = text[8:]
			elif text[:7].lower() == "<reply>":
				text = text[7:]
			else:
				text = factoid_key + " is " + text
	
		return Event(eventtype, "", target, [ string.strip(text) ])

class cookie(factoidClass):
	def __init__(self):
		self.regex = "^cookie$"
		self.priority = 17
	def handler(self, **args):
		""" gets a random factoid from the database"""
		from irclib import nm_to_n, Event
		import string

		# Standard return_to_sender target, talk to who talks to us
		target = self.return_to_sender(args)

		if database.type == "mysql":
			factoid_query = "select factoid_key, factoid_value "\
				"from factoids order by rand() limit 1"
		elif database.type == "pgsql":
			factoid_query = "select factoid_key, factoid_value "\
				"from factoids order by random() limit 1"

		factoid = database.doSQL(factoid_query)[0]
		factoid_key = factoid[0]
		factoid_value = self.parse_sar(string.lstrip(factoid[1]))
		factoid_value = factoid_value.replace("$who", nm_to_n(args["source"]))

		return Event("privmsg", "", target, \
			[ "Random factoid: %s is %s" % (factoid_key,
				factoid_value.strip()) ])

class delete(factoidClass):
	def __init__(self):
		self.regex = "^(delete|forget)\s.+"
		self.priority = 17
	def handler(self, **args):
		"Remove a factoid from the database"
		import priv
		from irclib import Event


		# If we got this via a /msg, /msg back, otherwise back to the channel
		# it goes 
		target = self.return_to_sender(args)

		# We are normally called with "moobot: forget foo", but the factoid key
		# is just the part after "moobot: forget", so we strip that here 
		factoid_key = self.strip_words(args["text"], 2)

		requester = args["source"]

		# We will always get back a (non-empty) list from this that is of the
		# format:
		#  [(<some number>,)]
		# That number is the number of instances of the factoid_key in the
		# factoid database (which should be 0 or 1).  If it's 0, tell them we
		# don't have the factoid. 
			
		count_query = "select count(factoid_key) "\
			      "from factoids "\
			      "where (factoid_key) = '%s'" % \
			      self.sqlEscape(factoid_key.lower())
		self.debug(count_query)
		self.debug(database.doSQL(count_query))
		if database.doSQL(count_query)[0][0] == 0:
			msg = "Factoid \"%s\" does not exist." % factoid_key
			return Event("privmsg", "", target, [ msg ])

		# This SQL query gets back a list similar to the one before:
		#  [(<person who locked the factoid>,)]
		# Only, if the locked_by value is NULL in SQL, we get None in our
		# tuple. 
		locked_query = "select locked_by, created_by "\
			       "from factoids "\
			       "where (factoid_key) = '%s'" % \
			       self.sqlEscape(factoid_key.lower())
		locked = database.doSQL(locked_query)

		locked_by = locked[0][0]
		created_by = locked[0][1]

		self.debug("created_by = ", created_by)
		self.debug("requester = ", requester)

		# If the factoid is locked, or the person doesn't have the right to
		# delete things anyway, tell them they can't.  ... unless they created
		# it. 
		if locked_by != None:
			msg = "Factoid \"%s\" is locked." % \
			self.sqlEscape(factoid_key)
			return Event("privmsg", "", target, [ msg ])

		if (priv.checkPriv(requester, "delete_priv") == 0) \
		and (created_by != requester):
			msg = "You do not have delete privileges."
			return Event("privmsg", "", target, [ msg ])

		# If we made it here, they can delete it.  So delete it, and tell
		# them.
		delete_query = "delete from factoids "\
			       "where (factoid_key) = '%s'" % \
			       self.sqlEscape(factoid_key.lower())
		database.doSQL(delete_query)

		msg = "Factoid \"%s\" deleted." % factoid_key
		return Event("privmsg", "", target, [ msg ])

class add(factoidClass):
	def __init__(self):
		self.priority = 20
		self.regex = ".+ (is|are|_is_|_are_) .+"
		# --- Get the max factoid key length ---
		# I insert a 255-char long string of a's with "factoid-length-check" as
		# the created_by field.  Since this created_by isn't a valid nickmask
		# on IRC, it can't be duplicated by anyone.  However, if the all-"a"
		# factoid is already there, we will see how long it is anyway and not
		# have to delete anything anyway when we just delete all factoids
		# created by "factoid-length-check"
		
		factoid_key = "a"*512	# 512 is the max chars in an IRC msg, from RFC
		created_by = "factoid-length-check"
		query = "insert into factoids(factoid_key, created_by) values('" + \
			factoid_key + "', '" + created_by + "')"
		database.doSQL(query)
		# Now retrieve the longest factoid that exists and delete the ones
		# created by "factoid-length-check"
		query = "select max(length(factoid_key)) from factoids"
		self.FACTOID_KEY_LENGTH = database.doSQL(query)[0][0]
		if self.FACTOID_KEY_LENGTH == None: #hack for postgres
			self.FACTOID_KEY_LENGTH = 64
		query = "delete from factoids where created_by='" + created_by + "'"
		database.doSQL(query)

	def handler(self, **args):
		"""adds a factoid"""
		import time
		from irclib import Event

		target = self.return_to_sender(args)

		#  Strip the bots name
		text = self.strip_words(args["text"], 1)

		# Figure out what to split the string on -- _is_ and _are_ can be used
		# to force the split at a certain point, instead of the first "is" or
		# "are"
		if text.find(" _is_ ") != -1:
			splitString = " _is_ "
		elif text.find(" _are_ ") != -1:
			splitString = " _are_ "
		elif text.find(" is ") != -1:
			splitString = " is "
		elif text.find(" are ") != -1:
			splitString = " are "

		# Separate the text into two parts, one is the factoid key (before
		# "is"), one is the factoid value.  "foo is bar" will result in foo
		# being the key and bar being the value.  Also, many is's will get
		# joined together in the factoid value, the first is separates the key
		# from the value 
		data = text.split(splitString, 1) # only split once
		factoid_key = self.strip_punctuation(data[0])
		factoid_value = data[1]

		if len(factoid_key) > self.FACTOID_KEY_LENGTH:
			old_key = factoid_key
			factoid_key = factoid_key[:self.FACTOID_KEY_LENGTH]
			warning = "WARNING: The factoid key '" + old_key + "' is" + \
				" too long, using this truncated key '" + factoid_key + \
				"' instead."

		#  Check and make sure the factoid isn't there
		count_query= "select count(factoid_key) "\
			     "from factoids "\
			     "where (factoid_key) = '%s'" % \
			     self.sqlEscape(factoid_key.lower())
		count = database.doSQL(count_query)[0][0]
			
		if count != 0:
			message = "Factoid \"%s\" already exists." % factoid_key
			return Event("privmsg", "", target, [ message ])

		#  Get the time for the database insertion
		insert_query = "insert into factoids("\
			"factoid_key, factoid_value, created_by, created_time, "\
			"requested_count) values ('%s', '%s', '%s', %s, 0)" % (
				self.sqlEscape(factoid_key),
				self.sqlEscape(factoid_value),
				args["source"], str(time.time()))
		database.doSQL(insert_query)

		if globals().has_key('warning'):
			return Event("privmsg", "", target, [ warning ])
		else:
			return Event("privmsg", "", target, [ "ok" ])
	
class list_keys(factoidClass):
	def __init__(self):
		self.regex = "^list(keys|values|auth)\s.+"
		self.priority = 17
	def handler(self, **args):
		"""searches factoid keys"""
		
		from irclib import Event

		# Strip bot name and "list*" from the text we get
		# Grab what kind of list(foo) thingy we are doing as well.
		search_string = self.strip_words(args["text"], 2)
		type = args["text"].split()[1]

		# have type search the appropriate attribute in the database
		if type == "listauth":
			match_query = "select count(created_by) "\
				      "from factoids "\
				      "where lower(created_by) like '%s!%%'" % (
				search_string.lower())
		else:
			if type == "listkeys":
				column = "factoid_key"
			elif type == "listvalues":
				column = "factoid_value"
			match_query = "select count(%s) "\
				      "from factoids "\
				      "where lower(%s) like '%s'" % (
				column, column, '%' + search_string.lower() + '%')

		# matchcount simply gets the number of matches for the SQL query that
		# counts factoids that are "like" the one given to us, and keys gets
		# the actual list (which is in the form of a list of one-element
		# tuples) 
		match = database.doSQL(match_query)
		matchcount = match[0][0]

		if type == "listauth": 
			if database.type == "mysql":
				keys_query = "select factoid_key "\
					     "from factoids "\
					     "where lower(created_by) like '%s!%%' "\
					     "order by rand() "\
					     "limit 15" % search_string.lower()
			elif database.type == "pgsql":
				keys_query = "select factoid_key "\
					     "from factoids "\
					     "where lower(created_by) like '%s!%%' "\
					     "order by random() "\
					     "limit 15" % search_string.lower()
		else:
			if database.type == "mysql":
				keys_query = "select factoid_key "\
					     "from factoids "\
					     "where lower(%s) like '%s' "\
					     "order by rand() "\
					     "limit 15" % (
					column, '%' + search_string.lower() + '%')
			elif database.type == "pgsql":
				keys_query = "select factoid_key "\
					     "from factoids "\
					     "where lower(%s) like '%s' "\
					     "order by random() "\
					     "limit 15" % (
					column, '%' + search_string.lower() + '%')

		keys = database.doSQL(keys_query)
		
		# Add a nifty little preface to the list showing what was searched
		# and how many match and (if applicable, how many we are showing) 
		text = "%s search of '%s' (%d matching" % (
			type, search_string, matchcount)

		# If we match more than fifteen, they only see fifteen (LIMIT 15,
		# above), so we'll tell them there are more there, but they only see
		# fifteen 
		if matchcount > 15:
			text += "; 15 shown"
		text += "): "

		#  Append on each of the fifteen terms and a separator
		index = 0
		while index < len(keys):
			text += keys[index][0] + " ;; "
			index += 1
		target = self.return_to_sender(args)
		return Event("privmsg", "", target, [ text ])

class replace(factoidClass):
	def __init__(self):
		self.regex = "^no,?\s.+\sis.+"
		self.priority = 19

	def handler(self, **args):
		""" replaces an existing factoid (no factoid is text> """
		import priv
		from irclib import Event
		from time import time

		target = self.return_to_sender(args)

		# Strip the bot name and "no" from the factoid
		factoid_text = self.strip_words(args["text"], 2)

		# Separate the factoid_keu (the word(s) before "is") from the
		# factoid value (anything after the first "is") 
		data = factoid_text.split(" is ", 1)
		factoid_key = data[0]
		factoid_value = data[1]

		select_query = "select count(factoid_key), locked_by "\
			       "from factoids "\
			       "where (factoid_key) = '%s' "\
			       "group by locked_by" % (
			self.sqlEscape(factoid_key.lower()))
		data = database.doSQL(select_query)
		count = data[0][0]
		locked_by = data[0][1]

		if count == 0:
			message = "Factoid '" + factoid_key + "' does not exist."
			return Event("privmsg", "", target, [message])

		# Check if they can modify factoids, and if they can modify THIS
		# particular factoid (ie, it's not locked) 
		if priv.checkPriv(args["source"], "delete_priv") == 0 and\
		locked_by != "" and locked_by != None:
			return Event("privmsg","", target, [ "Factoid is locked."])

		check_lock_query = "select count(factoid_key) "\
				   "from factoids "\
				   "where (factoid_key) = '%s' "\
				   "and (locked_by is null or locked_by = '')" % (
			self.sqlEscape(factoid_key.lower()))
		unlocked = database.doSQL(check_lock_query)[0][0]
		if not unlocked:
			msg = "Factoid \"%s\" is locked." % factoid_key
			return Event("privmsg","", target, [ msg ])

		#  If we make it here, we simply delete and recreate the factoid
		delete_query = "delete from factoids "\
			       "where (factoid_key) = '%s'" % (
			self.sqlEscape(factoid_key.lower()))
		database.doSQL(delete_query)

		insert_query = "insert into factoids("\
			       "factoid_key, created_by, created_time, factoid_value, "\
			       "requested_count) values ("\
			       "'%s', '%s', %d, '%s', 0)" % (
			self.sqlEscape(factoid_key),
			args["source"],
			int(time()),
			self.sqlEscape(factoid_value))
		database.doSQL(insert_query)

		return Event("privmsg", "", target,  [ "ok" ])

class lock(factoidClass):
	def __init__(self):
		self.regex = "^(un)?lock\s.+"
		self.priority = 17
	def handler(self, **args):
		""" lock and unlock factoids """
		import priv, time
		from irclib import Event, nm_to_n

		# Change the target based on how we were called
		target = self.return_to_sender(args)

		# Strip off the first word and then take the first word of
		# what's left to get our action, lock or unlock 
		action = self.strip_words(args["text"], 1).split(" ", 1)[0]

		# Every word after the first two is the factoid key
		factoid_key = self.strip_words(args["text"], 2)

		if action == "lock":
			# We allow people to lock their own factoid, or, if they have
			# lock_priv, whatever they want 
			if factoid_key == nm_to_n(args["source"]) \
			or priv.checkPriv(args["source"], "lock_priv") == 1:
				update_query = "update factoids "\
					"set locked_by = '%s', "\
					"locked_time = %d "\
					"where (factoid_key) = '%s'" % (
						args["source"],
						time.time(),
						self.sqlEscape(factoid_key.lower()))
				database.doSQL(update_query)
				msg = "Factoid \"%s\" locked." % factoid_key
			else:
				msg = "You can't lock this factoid."
		elif action == "unlock":
			# For unlocking, first check who locked the factoid we are
			# talking about 
			locked_query = "select locked_by "\
				"from factoids "\
				"where (factoid_key) = '%s'" % (
					self.sqlEscape(factoid_key.lower()))
			locked_by = database.doSQL(locked_query)

			# if we aren't locked, tell them, otherwise, check if the factoid
			# is for the requester's nick or if they have lock_priv (which
			# allows unlocking as well) 
			if len(locked_by) == 0 or \
			len(locked_by[0]) == 0 or \
			locked_by[0][0] == None:
				msg = "Factoid \"%s\" is not locked." % factoid_key
			elif locked_by[0][0] != args["source"] and \
			not priv.checkPriv(args["source"], "lock_priv"):
				msg = "You cannot unlock this factoid."
			else:
				update_query = "update factoids "\
					"set locked_by = NULL "\
					"where (factoid_key) = '%s'" % (
						self.sqlEscape(factoid_key.lower()))
				database.doSQL(update_query)
				msg = "Factoid \"%s\" unlocked." % factoid_key

		return Event("privmsg", "", target, [ msg ])

class info(factoidClass):
	def __init__(self):
		self.regex = "factinfo\s.+"
		self.priority = 17
	def handler(self, **args):
		"""Return information about a factoid to the person requesting it"""
		import time
		from irclib import Event

		target = self.return_to_sender(args)
		# Grab the factoid name requested
		factoid = self.strip_words(args["text"], 2)

		factinfo = database.doSQL("select requested_by, requested_time, " +
			"requested_count, created_by, created_time, modified_by, " +
			"modified_time, locked_by, locked_time from factoids where " +
			"(factoid_key) = '" + self.sqlEscape(factoid.lower()) + "'")
		if len(factinfo) == 0:
			return Event("continue", "", target, [""])
		requested_by, requested_time, requested_count, created_by, created_time, \
			modified_by, modified_time, locked_by, locked_time = factinfo[0]
		# Convert timestamps to ASCII time strings
		# Makes "1030123142124L" into a long int
		# That gets converted into a special time tuple
		# That gets converted to a nice ASCII string
		try:
			requested_time_str = time.asctime(time.localtime(requested_time))
		except:
			requested_time_str = "never"

		try:
			created_time_str = time.asctime(time.localtime(created_time))
		except:
			created_time_str = "never"

		try:
			modified_time_str = time.asctime(time.localtime(modified_time))
		except:
			modified_time_str = "never"

		#if locked_time == None:
		#	locked_time_str = "Not locked."
		#else:
		#	locked_time_str = time.asctime(time.localtime(locked_time))
		
		reply = factoid + ": created by " + self.str(created_by) + " on " + created_time_str
		if (modified_by is not None):
			reply += ".  Last modified by " + self.str(modified_by) + " on " + modified_time_str
		reply += ".  Last requested by " + self.str(requested_by) + " on " + requested_time_str + \
			", requested a total of " + str(requested_count) + " times."
		if (locked_by is not None and locked_time != None):
			reply += "  Locked by " + self.str(locked_by) + " on " + time.ctime(locked_time) + "."

		return Event("privmsg", "", target, [reply])

class augment(factoidClass):
	def __init__(self):
		self.regex = ".+\sis\salso\s.+"
		self.priority = 19
	def handler(self, **args):
		"""Allows someone to add material onto a factoid (that isn't locked) by
		saying "foo is also bar", for example"""
		import priv
		from irclib import Event
		from time import time
		target = self.return_to_sender(args)
		
		# args["text"] should look something like:
		#  "moobot: foo is also bar blatz qux"
		# Grab the factoid to change:
		factoid_key = self.strip_words(args["text"], 1).split(" is ")[0]
		# Grab the stuff to tack on:
		to_add = self.strip_words(args["text"], 1).split(" is also ")[1]

		# Check if the factoid exists, if it doesn't tell the user
		query = "select count(factoid_key) from factoids where" \
			" (factoid_key) = '" + factoid_key.lower() + "'"
		if database.doSQL(query)[0][0] == 0:
			message = "Factoid '" + factoid_key + "' does not exist."
			return Event("privmsg", "", target, [message])
		
		# Check if the factoid is locked or not
		lock_query = "select locked_by from factoids where (factoid_key) = '"\
			+ factoid_key.lower() + "'"
		locked_by = database.doSQL(lock_query)[0][0]
		if priv.checkPriv(args["source"], "delete_priv") == 0 and (locked_by != None and locked_by != "" and locked_by != args["source"]):
			message = "You do not have permission to delete this factoid."
			return Event("privmsg", "", target, [message])
		
		if locked_by != None:
			message = "That factoid is locked."
			return Event("privmsg", "", target, [message])
		
		# Since we don't have delete_priv, we just delete and recreate the factoid
		orig_factoid_query = "select factoid_value, requested_by," \
			+ " requested_time, requested_count, created_by, created_time"\
			+ " from factoids where" \
			+ " (factoid_key) = '" + factoid_key.lower() + "'"
		result = database.doSQL(orig_factoid_query)
		orig_factoid, orig_req_by, orig_req_time, orig_req_count, orig_cre_by, \
			orig_cre_time = result[0]
		if orig_req_by == None:
			orig_req_by = "NULL"
			orig_req_time = "NULL"
			orig_req_count = 0
		else:
			orig_req_by = "'" + orig_req_by + "'"
			orig_req_time = "'" + str(orig_req_time) + "'"
		new_factoid = self.sqlEscape(orig_factoid + ", or " + to_add)
		# Delete the factoid
		delete_query = "delete from factoids where (factoid_key) = '" \
			+ factoid_key.lower() + "'"
		database.doSQL(delete_query)
		# Re-create
		create_query = "insert into factoids(factoid_key, requested_by," \
			+ " requested_time, requested_count, created_by, created_time," \
			+ " modified_by, modified_time, factoid_value) values('" \
			+ factoid_key + "', " + orig_req_by + ", " + str(orig_req_time) \
			+ ", " + str(orig_req_count) + ", '" + orig_cre_by + "', " \
			+ str(orig_cre_time) + ", '" + args["source"] + "', " \
			+ str(int(time())) + ", '" + new_factoid + "')"
		database.doSQL(create_query)
		return Event("privmsg", "", target, ["ok"])

class alter(factoidClass):
	def __init__(self):
		self.regex = ".+=~.+"
		self.priority = 19
	def handler(self, **args):
		"""Allows someone to alter material in a factoid by using a regular
		expression.  Invoked like: "moobot: foo =~ s/moo/bar/"."""
		import priv, re, string, time
		from irclib import Event
		target = self.return_to_sender(args)
		
		# Grab the factoid to change:
		# first, drop the bot name
		factoid_key = string.join(args["text"].split()[1:])
		# Now split on " =~ " and take the left half
		factoid_key = factoid_key.split(" =~ ", 1)[0]
		
			
		# Check if the factoid exists
		count_query = "select count(factoid_key) from factoids where" \
			" (factoid_key) = '%s'" % \
			self.sqlEscape(factoid_key.lower())
		count = database.doSQL(count_query)[0][0]
		if count == 0:
			message = "Factoid '" + factoid_key + "' does not exist."
			return Event("privmsg", "", target, [message])

		# Now check and make sure we can modify this factoid
		# Locked?
		lock_query = "select locked_by from factoids " \
			"where (factoid_key) = '%s'" % \
			self.sqlEscape(factoid_key.lower())
		locked_by = database.doSQL(lock_query)[0][0]
		if locked_by != None: 
			message = "That factoid is locked."
			return Event("privmsg", "", target, [message])
		
		# Check for the appropriate privilege (delete_priv, even
		# though we aren't deleting - we are modifying, and there
		# is no modify priv)
		if priv.checkPriv(args["source"], "delete_priv") == 0:
			message = "You do not have permission to modify"
			return Event("privmsg", "", target, [message])

		# get the original factoid value
		orig_factoid_query = "select factoid_value from factoids where " \
			"(factoid_key) = '%s'" % \
			self.sqlEscape(factoid_key.lower())
		factoid = database.doSQL(orig_factoid_query)[0][0]

		# Grab the regex(es) to apply
		# First split on =~, then split on spaces for the RHS
		regexes_str = args["text"].split(" =~ ", 1)[1]
		# Now we can't split just on spaces, because the regex itself
		# can have spaces in it.  We gotta grab each one individually
		# because a regex to get them all (potentially each having 
		# unique separators, like "s/foo/bar blatz/g s:moo:mooooo!:i
		# s%this%makes it hard to parse%".
		#
		# The basic algorithm is:
		# 1 - find out the separator character (2nd)
		# 2 - find the index of the third occurrence of this character
		# 3 - find the next space, chop off everything before it and
		#     append it to the regex_list
		regex_list = []
		# regex for removing leading spaces, compiling it first
		lead_spaces = re.compile("^\s+")
		while len(regexes_str) > 2:
			# Strip leading spaces first (so regexes with many spaces
			# between them don't mess things up when we assume the separator
			# is the second character)
			regexes_str = lead_spaces.sub("", regexes_str)
			# Separator = 2nd char
			separator = regexes_str[1]
			# Find it once, then use that as a low range
			# NOTE - if there is garbage at any point, ignore everything
			# after it
			second_sep = regexes_str.find(separator, 2)
			if second_sep == 0:	break
			third_sep = regexes_str.find(separator, second_sep+1)
			if third_sep == 0: break
			# now the space
			space_index = regexes_str.find(" ", third_sep)
			
			if space_index == -1:	# no space found
				regex_list.append(regexes_str)
				break
			else:
				regex_list.append(regexes_str[:space_index])
				regexes_str = regexes_str[space_index:]

		# apply each of the regexes in order
		# For now we are assuming all of the regexes are search and replace
		# s/foo/bar/[gi]
		ACCEPTABLE_PREFIXES = "sy"
		ACCEPTABLE_SUFFIXES = "gi"
		for regex_string in regex_list:
			# Split the regex into parts - strictly, we split on the second
			# character, as s:foo:bar: is valid as well
			try:
				parts = regex_string.split(regex_string[1])
			except IndexError:
				break

			# If we don't get four parts (even if the last is empty)
			# then it's not a valid regex - chastise them ... also,
			# if it's not one of the valid prefixes/suffixes, chastise them :)
			if len(parts) != 4 or \
			parts[0] not in ACCEPTABLE_PREFIXES:
				message = "Invalid regular expression: " + regex_string
				return Event("privmsg", "", target, [message])
			for letter in parts[3]:
				if letter not in ACCEPTABLE_SUFFIXES:
					message = "Invalid regular expression: " + regex_string
					return Event("privmsg", "", target, [message])

			# Get some flags before we compile a regex
			if "g" in parts[3]: count = 0
			else: count = 1
			if "i" in parts[3]: case_sensitive = 0
			else: case_sensitive = 1

			# Make a regex object for the first pattern
			try:
				re_str = parts[1]
				if case_sensitive:
					regex = re.compile(re_str)
				else:
					regex = re.compile(re_str, re.I)
			except re.error:
				message = "Invalid regular expression: " + regex_string
				return Event("privmsg", "", target, [message])
			
			# Actually perform the transformation
			if parts[0] == "s":
				factoid = regex.sub(parts[2], factoid)
			elif parts[0] == "y":
				message = "This regex not yet supported.  Sorry :("
				return Event("privmsg", "", target, [message])
				
					
		# When all the regexes are applied, store the factoid again
		# with the new date as the modification date.
		factoid = self.sqlEscape(factoid)
		mod_date = str(int(time.time()))
		mod_author = args["source"]
		insert_query = "update factoids set factoid_value='%s', " \
			"modified_time='%s', modified_by='%s' " \
			"where (factoid_key)='%s'" % (
			factoid, mod_date, mod_author,
			self.sqlEscape(factoid_key.lower()))
		#insert_query = "update factoids set factoid_value = '" + factoid + "'" \
		#	+ " where (factoid_key) = '" + factoid_key.lower() + "'"
		database.doSQL(insert_query)
		return Event("privmsg", "", target, ["ok"])

# vim:ts=4:sw=4:tw=78:
