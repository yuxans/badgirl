#!/usr/bin/env python

# Copyright (c) 2002 Daniel DiPaolo and Brad Stewart
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

"""MooBot - The Pro-Trustix Python bot.

This bot aims to be a lot like the blootbot, apt, that
is found in #debian on OPN all the time - minus the
sucking and the whole being written in Perl part (wait,
I already said "the sucking" :)).  This is a work in
progress.
"""

# Colorized output constants
ESCAPE = "\33"
RED = ESCAPE + "[31m"
GREEN = ESCAPE + "[32m"
YELLOW = ESCAPE + "[33m"
BLUE = ESCAPE + "[34m"
PURPLE = ESCAPE + "[35m"
NORMAL = ESCAPE + "[0m"
UNDERLINE = ESCAPE + "[4m"
BLINK = ESCAPE + "[5m"

# Debugging turns stack traces on (allows bot crash)
DEBUG = 0

import string, thread, threading


from ircbot import SingleServerIRCBot, IRCDict, Channel
from irclib import irc_lower, Debug


class MooBot(SingleServerIRCBot):
	class MooBotException(Exception): pass
	class HandlerExists(MooBotException): pass
	config_files = ['moobot.conf', '/etc/moobot/moobot.conf']

	def __init__(self, channels=[], nickname="", server="", port=6667, password="", module_list=[], encoding=""):
		"""MooBot initializer - gets values from config files and uses those
		unless passed values directly"""
		Debug("possible config files: " + ", ".join(self.config_files))

		# Get values from config files and replace any of the empty ones above
		configs = self.get_configs()
		config_nick = configs['nick']
		config_server = configs['server']
		config_port = configs['port']
		config_encoding = configs['encoding']
		config_password = configs['password']
		config_channels = configs['channels']
		config_module_list = configs['module_list']
		config_others = configs['others']
		# If we are passed any values directly, use those, but if they are empty
		# we will fall back to the values we got from the config file
		if channels == []: channels = config_channels
		if nickname == "": nickname = config_nick
		if server == "": server = config_server
		if port == 6667: port = config_port
		if password == "": password = config_password
		if module_list == []: module_list = config_module_list
		if encoding == "": encoding = config_encoding
		# Now that we have our values, initialize it all
		SingleServerIRCBot.__init__(self, [(server, port, password, encoding)], nickname, nickname)
		self.channels = IRCDict()
		for channel in channels:
			self.channels[channel] = Channel()
		self.handlers = []
		self.configs = config_others
		self.module_list = module_list

	def on_join(self, c, e):
		"""Whenever a client joins a channel the bot is in, this is
		executed"""
		pass

	def on_welcome(self, c, e):
		"""Whenever this bot joins a server, this is executed"""
		for channel in self.channels.keys():
			Debug("Joining", channel)
			c.join(channel)

	def on_privmsg(self, c, e):
		"""Whenever someone sends a /msg to our bot, this is executed"""
		msg = e.arguments()[0]	# the string of what was said
		# build the args dict for the handlers
		args={}
		args["text"] = self.connection.get_nickname() + ": " + msg
		args["type"] = e.eventtype()
		args["source"] = e.source()
		args["channel"] = e.target()
		msg = string.strip(msg)
		from irclib import nm_to_n
		# Debug(what was said to the stdout with a bit of colour.)
		Debug(YELLOW + "<" + nm_to_n(args["source"]) + NORMAL + "/" + \
			BLUE + args["channel"] + ">" + NORMAL + \
			RED + "(" + args["type"] + ")" + NORMAL, args["text"])
		temp = threading.Thread(target=self.process_privmsg, args=(msg, args), name="privmsg subthread")
		temp.setDaemon(1)
		temp.start()
	
	def process_privmsg(self, msg, args):
		"""Process private messages (/msg's) to the bot"""
		eventlist = self.get_local_handler(msg, args)
		if eventlist != []:
			for event in eventlist:
				self.do_event(event)

	def on_pubmsg(self, c, e):
		"""Whenever someone speaks in a channel where our bot resides, this is
		executed"""
		import string
		msg = e.arguments()[0]
		args = {}
		args["text"] = msg
		args["type"] = e.eventtype()
		args["source"] = e.source()
		args["channel"] = e.target()
		# Then check with all the global handlers, see if any match
		from irclib import nm_to_n
		# Debug(what was said to the stdout with a bit of colour.)
		Debug(YELLOW + "<" + nm_to_n(args["source"]) + NORMAL + "/" +\
			BLUE + args["channel"] + ">" + NORMAL +\
			RED + "(" + args["type"] + ")" + NORMAL, args["text"])
		temp = threading.Thread(target=self.process_pubmsg, \
			args=(msg, args), name="pubmsg subthread")
		temp.setDaemon(1)
		temp.start()
	
	def process_pubmsg(self, msg, args):
		"""Process messages into the channel"""
		from re import compile
		import string
		eventlist = self.get_global_handler(msg, args)
		if eventlist != []:
			for event in eventlist:
				self.do_event(event)
			if eventlist[-1].eventtype() != "continue":
				return
		# If we are referred to with our shorthand name, make it look
		# like we were referred to normally.
		shortname = "^\s*" + self.configs["shorthand"]
		shortregex = compile(shortname)
		replace_str = self.connection.get_nickname() + ": "
		if shortregex.search(msg):
			msg = string.replace(msg, self.configs["shorthand"], replace_str, 1)
			args["text"] = msg
		# Now, check and see if we are being spoken too
		ourname = "^" + self.connection.get_nickname()
		regex = compile(ourname)
		if regex.search(msg):
			msg = string.strip(msg[string.find(msg, " "):])
			eventlist = self.get_local_handler(msg, args)
			if eventlist != []:
				for event in eventlist:
					self.do_event(event)

	def get_global_handler(self, msg, args):
		"""Used when an event is raised that needs a global handler"""
		return self.get_handler(Handler.GLOBAL, msg, args)

	def get_local_handler(self, msg, args):
		"""Used when an event is raised that needs a local handler"""
		return self.get_handler(Handler.LOCAL, msg, args)

	def get_handler(self, type, msg, args):
		"""Used when an event is raised that needs an event handler"""
		# Check through the handlers for a key that matches
		# the message contents.
		from irclib import nm_to_n
		from irclib import Event
		import weakref
		nickname = self.connection.get_nickname()
		if type == Handler.GLOBAL and args["text"][:len(nickname)] != nickname:
			# For now we are going to rewrite the message with the
			# name on the front so that modules don't care if they are
			# local or global.
			args["text"] = self.connection.get_nickname() + ": " +\
				args["text"]
		# Iterate over the list of registered handlers, looking for a handler
		# that matches in type and regex.  When it is found, call it and get a
		# resulting event or list of events which we return
		eventlist = [Event("continue", "", "", [""])]
		for handler in self.handlers:
			if eventlist[-1].eventtype() != "continue":
				break

			if handler.type == type:
				if handler.regex.search(msg):
					instance = handler.instance
					# result can either be an Event or a list of Events, 
					# in either case, we just add on all the Events to
					# eventlist
					result = instance.handler(text=args["text"], 
						type=args["type"], source=args["source"], 
						channel=args["channel"], ref=weakref.ref(self))
					if isinstance(result, Event):
						eventlist.append(result)
					else:
						eventlist += result

		if len(eventlist) >1:
			return eventlist

		# This should never come up unless you take out the "dunno" handlers
		# that generally hand every case that no other handler takes care of
		if type == Handler.LOCAL:
			Debug("Could not get event handler.")
			Debug("msg:", args["text"])
			Debug("type:", args["type"])
			Debug("source:", args["source"])
			Debug("channel:", args["channel"])

		return []

	def list_handlers(self):
		"""Display the handlers currently registered with the bot"""
		strings =[] 
		for handler in self.handlers:
			if handler.function.__doc__ is not None:
				string = handler.pattern() + ": " + handler.func_name() + \
					"() - " + handler.function.__doc__ + " ("
				if handler.type == Handler.GLOBAL: string += "global)"
				else: string += "local)"
			else:
				string = handler.pattern() + ": " + handler.func_name() + "() ("
				if handler.type == Handler.GLOBAL: string += "global)"
				else: string += "local)"
			strings.append(string)
		return strings

	def do_event(self, event):
		"""Does an appropriate action based on event"""
		if event.eventtype() == "privmsg":
			for line in string.split(event.arguments()[0], "\n"):
				# Debug(the output to the STDOUT, with a bit of colour)
				Debug(RED + ">" + \
					PURPLE + self.connection.get_nickname() + \
					RED + "/" + \
					GREEN + event.target() + \
					RED + "<" + \
					NORMAL, line)
				self.connection.privmsg(event.target(), line)
		elif event.eventtype() == "action":
			Debug(RED + " * " + \
				PURPLE + self.connection.get_nickname() + \
				RED + "/" + \
				GREEN + event.target() + \
				NORMAL, event.arguments())
			self.connection.action(event.target(), event.arguments()[0])
		elif event.eventtype() == "internal":
			#Debug("internal", event.arguments()[0], event.target)
			if event.arguments()[0] == "join":
				Debug("Joining", event.target())
				self.connection.join(event.target())
			elif event.arguments()[0] == "part":
				Debug("Parting", event.target())
				self.connection.part(event.target())
			elif event.arguments()[0] == "load":
				self.load_module(event);
			elif event.arguments()[0] == "unload":
				self.unload_module(event);
			elif event.arguments()[0] == "nick":
				Debug("Changing nick to ", event.target())
				self.connection.nick(event.target())
			elif event.arguments()[0] == "kick":
				Debug("Kicking", event.target(), "from", event.arguments()[1])
				self.connection.kick(event.arguments()[1], event.target())
			elif event.arguments()[0] == "send_raw":
				Debug("Sending raw command: " + event.arguments()[0])
				self.connection.send_raw(event.arguments()[1])
			elif event.arguments()[0] == "modules":
				from irclib import Event
#				if event.arguments()[1] == "":
#					strings = self.list_handlers()
#					reply = ""
#					for msg in strings:
#						reply += msg + " ;; "
#					self.do_event(Event("privmsg", "", event.target(), [reply]))
#				else:
				for module in event.arguments()[1].split(" "):
					match = 0
					for handler in self.handlers:
						if handler.className == module:
							match = 1
							if handler.className is not None:
								msg = `handler.pattern()` + ": " + \
									`handler.func_name()` + "() - " + \
									`handler.instance.__doc__` + " ("
								if handler.type == Handler.GLOBAL:
									msg += "global)"
								else:
									msg += "local)"
							else:
								msg = handler.pattern() + ": " + \
									handler.func_name() + "() ("
								if handler.type == Handler.GLOBAL:
									msg += "global)"
								else:
									msg += "local)"
					if match == 0:
						msg = "no handler found with function " + module + "()"
					self.do_event(Event("privmsg", "", event.target(), [msg]))
		elif event.eventtype() == "continue":
			return
		else:
			Debug("This event type", event.eventtype(), "has no suitable event")

	def get_configs(self, filelist=[]):
		"""Gets configuration options from a list of files"""
		from ConfigParser import ConfigParser, NoSectionError, NoOptionError

		config = ConfigParser()
		filelist += MooBot.config_files
		Debug("Parsed config files:", config.read(filelist))

		# Initialize the things we will return just in case they aren't in
		# any of the files that we parse through.  Then get their values
		# and stick the rest in "others"
		nick=""; server=""; port=6667; password=""; channels=[]; others={}
		encoding = "utf-8"
		module_list = []
		try:
			nick = config.get('connection', 'nick')
			server = config.get('connection', 'server')
			encoding = config.get('connection', 'encoding')
			port = int(config.get('connection', 'port'))
			password = config.get('connection', 'password')
			channels = config.get('connection', 'channels').split(" ")
			module_list = config.get('modules', 'modulefiles').split(" ")
		except ValueError:
			Debug("ERROR: Non-numeric port in config files.")
		except NoSectionError:
			Debug("ERROR: [connection] section missing from config files.")
		except NoOptionError:
			Debug("ERROR: missing vital option")
		for section in config.sections():
			if section != "connection":
				# These will all be returned, don't need to be in others
				for option in config.options(section):
					others[option] = config.get(section, option)
		return {'nick': nick, 'server': server, 'port': port, 'password': password, 
			'channels': channels, 'module_list': module_list, 'encoding': encoding,
			'others': others}
	
	def load_module(self, event):
		""" this loads a module, at run-time.  event is an Event whose arguments()
		attribute contains a list of modules to write (starting with the second
		element """
		import imp
		for newmod in event.arguments()[1:]:
			# why this?  --djd
			fp = ""
			pathname = ""
			description = ""

			# we need to do this to make sure the module is there, and to
			# get some information needed by imp.load_module
			try:
				fp, pathname, description = imp.find_module(newmod)
			except:
				Debug("Module \"%s\" not found " % (newmod))
				if fp:
					fp.close()
				continue

			# as a side note, imp.load_module doesn't add the module to
			# the modules table, it only returns a reference to that 
			# module.
			try:
				importedModule = imp.load_module(newmod, fp, pathname, description)
				# each module contains a list called handler_list, which
				# contains the names of classes to be loaded as bot modules
				for handlerName in importedModule.handler_list:
					newHandler = Handler(importedModule, handlerName)
					self.handlers.append(newHandler)
					Debug("Added handler: " , handlerName, "for \"" \
						+ newHandler.regex.pattern+"\"", \
						"priority ", newHandler.instance.priority)
				if importedModule.__name__ not in self.module_list:
					self.module_list.append(importedModule.__name__)
			finally:
				# sort the list (for priorities)
				self.handlers.sort()
				# Since we may exit via an exception, close fp explicitly.
				if fp:
					fp.close()

	def unload_module(self, event):
		""" remove any handlers from self.handlers that are from any of the
		modules passed in event.arguments()[1:]"""
		module_list = event.arguments()[1:]
		for index in range(len(self.handlers)-1, -1, -1):
			if self.handlers[index].module.__name__ in module_list:
				self.handlers.pop(index)
		# sort the list (for priorities)
		for module in module_list:
			if module in self.module_list:
				self.module_list.remove(module)
		self.handlers.sort()
	
class Handler:
	"""This class defines how chat messages are processed to generate chat
	events that the bot acts out"""
	GLOBAL = 1
	LOCAL = 0

	def __init__(self, module, className, type=0):
		from re import compile
		self.instance = getattr(module, className)()
		self.module = module
		self.className = className
		self.regex = compile(self.instance.regex)
		self.type = type or self.instance.type

	def __str__(self):
		return '"' + self.regex + '": ' + self.function.__name__
	
	def __cmp__(self, other):
		return cmp(self.instance, other.instance)

	def reInstantiate(self):
		from re import compile
		Debug("reloading %s from %s" % (self.className, self.module.__name__))
		reload(self.module)
		self.instance = getattr(self.module, self.className)()
		self.regex = compile(self.instance.regex)

	def toggle_global(self):
		if self.type == Handler.LOCAL:
			self.type = Handler.GLOBAL
		else:
			self.type = Handler.LOCAL
	def pattern(self):
		return self.regex.pattern
	def func_name(self):
		return self.className

def main():
	bot = MooBot()
	from irclib import Event
	for module in bot.module_list:
		bot.load_module(Event("", "", "", ["", module]))
	bot.start()

# config_files is needed by database
import sys
if len(sys.argv) > 1:
	MooBot.config_files = [sys.argv[1]] + MooBot.config_files

if __name__ == '__main__':
	main()

