#!/usr/bin/env python

# Copyright (c) 2002 Brad Stewart and Daniel DiPaolo
# Copyright (C) 2007 by moo
# Copyright (C) 2007 by FKtPp
# 
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
import FactoIds

class factoidClass(MooBotModule):
	"""Base class for all factoid classes, encapsulates a lot of common
	functions into one base class"""
	def strip_words(self, str, num):
		"""Strips a certain number of words from the beginning of a string"""

		str = " ".join(str.split()[num:])
		return str
		
	def strip_punctuation(self, str):
		"""Strips ?s and !s from the end of a string"""
		while len(str) > 1 and (str[-1] == "!" or str[-1] == "?"):
			str = str[:-1]
		return str	

class lookup(factoidClass):
	def __init__(self):
		self.regex = ".+"
		self.priority = 18
	def handler(self, **args):
		""" gets the factoid_value field """
		import time
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

		text = FactoIds.getValueByKey(factoid_key, args["source"])

		# If the factoid doesn't exist, simply continue trying
		# to match with other handlers using the continue event type 
		if not text:
			return Event("continue", "", target, [""])

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
			text = text.lstrip()

			# Parse parentheses and pipes to come up with one random string
			# from many choices specified in the factoid 
			text = FactoIds.parseSar(text)

			# Replace $who and $nick with the person requesting the factoid
			text = text.replace("$who", nm_to_n(args["source"]))
			if args.has_key("channel"):
				text = text.replace("$chan", args["channel"])
			text = text.replace("$nick", nm_to_n(args["source"]))

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
	
		return Event(eventtype, "", target, [ text.strip() ])

class cookie(factoidClass):
	def __init__(self):
		self.regex = "^cookie$"
		self.priority = 17
	def handler(self, **args):
		""" gets a random factoid """
		from irclib import nm_to_n, Event


		# Standard return_to_sender target, talk to who talks to us
		target = self.return_to_sender(args)

		factoids = FactoIds.getRandoms()
		if not factoids:
			return Event("privmsg", "", target, [ "no factoid defined" ])

		factoid = factoids[0]
		factoid_key = factoid[0]
		factoid_value = FactoIds.parseSar(factoid[1].lstrip())
		factoid_value = factoid_value.replace("$who", nm_to_n(args["source"]))

		return Event("privmsg", "", target, \
			[ "Random factoid: %s is %s" % (factoid_key,
				factoid_value.strip()) ])

class delete(factoidClass):
	def __init__(self):
		self.regex = "^(delete|forget)\s.+"
		self.priority = 17
	def handler(self, **args):
		"Remove a factoid"
		import priv
		from irclib import Event


		# If we got this via a /msg, /msg back, otherwise back to the channel
		# it goes 
		target = self.return_to_sender(args)

		# We are normally called with "moobot: forget foo", but the factoid key
		# is just the part after "moobot: forget", so we strip that here 
		factoid_key = self.strip_words(args["text"], 2)

		requester = args["source"]

		locked_by = FactoIds.getLockedBy(factoid_key)
		created_by = FactoIds.getCreatedBy(factoid_key)
		if locked_by == None or created_by == None:
			msg = "Factoid \"%s\" does not exist." % factoid_key
			return Event("privmsg", "", target, [ msg ])

		self.debug("created_by = ", created_by)
		self.debug("requester = ", requester)

		# If the factoid is locked, or the person doesn't have the right to
		# delete things anyway, tell them they can't.  ... unless they created
		# it. 
		if locked_by != None:
			msg = "Factoid \"%s\" is locked." % factoid_key
			return Event("privmsg", "", target, [ msg ])

		if (priv.checkPriv(requester, "delete_priv") == 0) \
		and (created_by != requester):
			msg = "You do not have delete privileges."
			return Event("privmsg", "", target, [ msg ])

		# If we made it here, they can delete it.  So delete it, and tell
		# them.
		FactoIds.delete(factoid_key)

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
		
		self.FACTOID_KEY_LENGTH = FactoIds.getMaxValueLength()

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

		msg = "ok"
		if len(factoid_key) > self.FACTOID_KEY_LENGTH:
			old_key = factoid_key
			factoid_key = factoid_key[:self.FACTOID_KEY_LENGTH]
			msg = "WARNING: The factoid key '" + old_key + "' is" + \
				" too long, using this truncated key '" + factoid_key + \
				"' instead."

		#  Check and make sure the factoid isn't there
		if FactoIds.exists(factoid_key):
			message = "Factoid \"%s\" already exists." % factoid_key
			return Event("privmsg", "", target, [ message ])

		FactoIds.add(factoid_key, factoid_value, args["source"])

		return Event("privmsg", "", target, [ msg ])
	
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

		limit = 15
		keys, matchcount = FactoIds.search(type[4:], search_string, limit, True)
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
		for key in keys:
			text += key + " ;; "
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

		locked_by = FactoIds.getLockedBy(factoid_key)
		if locked_by == None:
			message = "Factoid '" + factoid_key + "' does not exist."
			return Event("privmsg", "", target, [message])

		# Check if they can modify factoids, and if they can modify THIS
		# particular factoid (ie, it's not locked) 
		if priv.checkPriv(args["source"], "delete_priv") == 0 and locked_by != "":
			return Event("privmsg","", target, [ "Factoid \"%s\" locked by %s" % (factoid_key, locked_by)])

		FactoIds.add(factoid_key, factoid_value, args["source"])

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
				FactoIds.lock(factoid_key, args["source"])
				msg = "Factoid \"%s\" locked." % factoid_key
			else:
				msg = "You can't lock this factoid."
		elif action == "unlock":
			# For unlocking, first check who locked the factoid we are
			# talking about 
			locked_by = FactoIds.getLockedBy(factoid_key)
			if locked_by == None:
				msg = "Factoid \"%s\" not found." % factoid_key

			else:
				# if we aren't locked, tell them, otherwise, check if the factoid
				# is for the requester's nick or if they have lock_priv (which
				# allows unlocking as well) 
				if not locked_by:
					msg = "Factoid \"%s\" is not locked." % factoid_key
				elif locked_by != args["source"] and not priv.checkPriv(args["source"], "lock_priv"):
					msg = "You cannot unlock this factoid."
				else:
					FactoIds.unlock(factoid_key, args["source"])
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
		# Grab the factoid_key name requested
		factoid_key = self.strip_words(args["text"], 2)

		factinfo = FactoIds.getFactoInfoByKey(factoid_key)
		if not factinfo:
			return Event("continue", "", target, [""])
		# Convert timestamps to ASCII time strings
		# Makes "1030123142124L" into a long int
		# That gets converted into a special time tuple
		# That gets converted to a nice ASCII string
		try:
			requested_time_str = time.asctime(time.localtime(factinfo["requested_time"]))
		except:
			requested_time_str = "never"

		try:
			created_time_str = time.asctime(time.localtime(factinfo["created_time"]))
		except:
			created_time_str = "never"

		try:
			modified_time_str = time.asctime(time.localtime(factinfo["modified_time"]))
		except:
			modified_time_str = "never"

		#if locked_time == None:
		#	locked_time_str = "Not locked."
		#else:
		#	locked_time_str = time.asctime(time.localtime(locked_time))
		
		reply = factoid_key + ": created by " + self.str(factinfo["created_by"]) + " on " + created_time_str
		if (factinfo["modified_by"] is not None):
			reply += ".  Last modified by " + self.str(factinfo["modified_by"]) + " on " + modified_time_str
		reply += ".  Last requested by " + self.str(factinfo["requested_by"]) + " on " + requested_time_str + \
			", requested a total of " + str(factinfo["requested_count"]) + " times."
		if (factinfo["locked_by"] is not None and factinfo["locked_time"] != None):
			reply += "  Locked by " + self.str(factinfo["locked_by"]) + " on " + time.ctime(factinfo["locked_time"]) + "."

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

		# Check if the factoid is locked or not
		locked_by = FactoIds.getLockedBy(factoid_key)
		if locked_by == None:
			message = "Factoid '%s' does not exist." % factoid_key
			return Event("privmsg", "", target, [message])

		if priv.checkPriv(args["source"], "delete_priv") == 0 and (locked_by != "" and locked_by != args["source"]):
			message = "You do not have permission to delete factoid '%s." % factoid_key
			return Event("privmsg", "", target, [message])
		
		# Since we don't have delete_priv, we just delete and recreate the factoid
		orig_factoid = FactoIds.getValueByKey(factoid_key)
		new_factoid = orig_factoid + ", or " + to_add
		FactoIds.update(factoid_key, new_factoid, arg["source"])
		return Event("privmsg", "", target, ["ok"])

class alter(factoidClass):
	def __init__(self):
		self.regex = ".+=~.+"
		self.priority = 19
	def handler(self, **args):
		"""Allows someone to alter material in a factoid by using a regular
		expression.  Invoked like: "moobot: foo =~ s/moo/bar/"."""
		import priv, re, time
		from irclib import Event
		target = self.return_to_sender(args)
		
		# Grab the factoid to change:
		# first, drop the bot name
		factoid_key = " ".join(args["text"].split()[1:])
		# Now split on " =~ " and take the left half
		factoid_key = factoid_key.split(" =~ ", 1)[0]
		
			
		locked_by = FactoIds.getLockedBy(factoid_key)
		if locked_by == None:
			message = "Factoid '%s' does not exist." % factoid_key
			return Event("privmsg", "", target, [message])

		# Check for the appropriate privilege (delete_priv, even
		# though we aren't deleting - we are modifying, and there
		# is no modify priv)
		if priv.checkPriv(args["source"], "delete_priv") == 0 and (locked_by != "" and locked_by != args["source"]):
			message = "You do not have permission to modify factoid '%s." % factoid_key
			return Event("privmsg", "", target, [message])

		# get the original factoid value
		factoid = FactoIds.getValueByKey(factoid_key)

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
		FactoIds.update(factoid_key, factoid, args["source"])
		return Event("privmsg", "", target, ["ok"])

# vim:ts=4:sw=4:tw=78:
