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

"""MooBot - The pro-Debian Python bot.

This bot aims to be a lot like the blootbot, apt, that
is found in #debian on OPN all the time - minus the
sucking and the whole being written in Perl part (wait,
I already said "the sucking" :)).  This is a work in
progress.
"""

# Debugging turns stack traces on (allows bot crash)
DEBUG = 0

import string, thread, threading


from utilities import *
from os import environ
from ircbot import SingleServerIRCBot, IRCDict, Channel
from irclib import irc_lower, Debug
from handler import Handler
import string, thread, threading

class MooBot(SingleServerIRCBot):
	class MooBotException(Exception): pass
	class HandlerExists(MooBotException): pass
	config_files = [environ['HOME']+'/.moobot.conf', 'moobot.conf',
            '/etc/moobot.conf']

	def __init__(self, channels=[], nickname="", realname="", server="", port=6667, module_list=[], encoding=""):
		"""MooBot initializer - gets values from config files and uses those
		unless passed values directly"""
		Debug("possible config files: " + ", ".join(self.config_files))

		# Get values from config files and replace any of the empty ones above
		configs = self.get_configs()
		config_nick = configs['nick']
		config_username = configs['username']
		config_realname = configs['realname']
		config_server = configs['server']
		config_port = configs['port']
		config_encoding = configs['encoding']
		config_password = configs['password']
		config_channels = configs['channels']
		config_module_list = configs['module_list']
		config_others = configs['others']
		# If we are passed any values directly, use those, but if they are empty
		# we will fall back to the values we got from the config file
#		for var in \
#			['channels', 'nickname', 'username', 'server', 
#			'port', 'module_list', 'others']:
#				if kwargs.has_key(var): 
#		if kwargs.has_key('channels'): channels = kwargs['channels']
#		else: channels = config_channels
		if channels == []: channels = config_channels
		if nickname == "": nickname = config_nick
		if realname == "": realname = config_realname
		if server == "": server = config_server
		if port == 6667: port = config_port
		if password == "": password = config_password
		if module_list == []: module_list = config_module_list
		if encoding == "": encoding = config_encoding
		# Now that we have our values, initialize it all
		SingleServerIRCBot.__init__(self, [(server, port, password, encoding)], nickname, realname)
		self.channels = IRCDict()
		for channel in channels:
			self.channels[channel] = Channel()
		self.handlers = {}
		self.configs = config_others
		self.module_list = module_list


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
		args["event"] = e
		msg = string.strip(msg)
		from irclib import nm_to_n
		# Debug(what was said to the stdout with a bit of colour.)
		Debug(YELLOW + "<" + nm_to_n(args["source"]) + NORMAL + "/" + \
			BLUE + args["channel"] + ">" + NORMAL + \
			RED + "(" + args["type"] + ")" + NORMAL, args["text"])
		temp = threading.Thread(target=self.process_privmsg, \
			args=(msg, args), name="privmsg subthread")
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
		msg = e.arguments()[0]
		args = {}
		args["text"] = msg
		args["type"] = e.eventtype()
		args["source"] = e.source()
		args["channel"] = e.target()
		args["event"] = e
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

	def on_ctcp(self, c, e):
		""" Executed on CTCP events."""
		self.on_other(c, e)
		SingleServerIRCBot.on_ctcp(self, c, e)
		
	def on_other(self, c, e):
		""" executed when an event without a specific on_<event>
		handler happens """
		if e.eventtype() != "all_raw_messages": # ignore these, because they
							# happen for every event
			#print "in on_other with eventtype:", e.eventtype()
			args = {}
			args["event"] = e
			args["type"] = e.eventtype()
			temp = threading.Thread(target=self.process_other, \
				args=(args, ""), name="other subthread")
			temp.setDaemon(1)
			temp.start()

	def process_other(self, args, a):
		""" Process events caught by on_other """
		eventlist = self.get_handler(args["event"].eventtype(), "", args)
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
		from irclib import Event
		import weakref
		eventlist = [Event("continue", "", "", [""])]

		# "all" handlers should be done first.
		# Skip them for LOCAL pubmsgs, though, because they'll already
		# have run on the GLOBAL handler.
		if type != Handler.LOCAL or args["event"].eventtype() != "pubmsg":
			if "all" in self.handlers.keys():
				for handler in self.handlers["all"]:
					instance = handler.instance
					e = args["event"]
					if e.source() == "":
						e._source = self.connection.get_nickname()
					arguments = {"event" :  e,
					     	"ref": weakref.ref(self)}
					instance.handler(**arguments)
	
		if type in self.handlers.keys():
			for handler in self.handlers[type]:
				if eventlist[-1].eventtype() != "continue":
					break
				if (type <> Handler.GLOBAL and type <> Handler.LOCAL) or \
				   (handler.regex.search(msg)):
					for key in ["text", "type", "source",
						    "channel", "event"]:
						if key not in args.keys():
							args[key] = None
					instance = handler.instance
					result = instance.handler(text=args["text"],
								  type=args["type"],
								  source=args["source"],
								  channel=args["channel"],
								  event=args["event"],
								  ref=weakref.ref(self))
					if isinstance(result, Event):
						eventlist.append(result)
					elif result != None:
						eventlist += result
						
		if len(eventlist) >1:
			return eventlist

		# This should never come up unless you take out the "dunno"
		# handlers that generally hand every case that no other handler
		# takes care of.
		if type == Handler.LOCAL:
			Debug("Could not get event handler.")
			Debug("msg:", args["text"])
			Debug("type:", args["type"])
			Debug("source:", args["source"])
			Debug("channel:", args["channel"])

		return []

	def do_event(self, event):
		"""Does an appropriate action based on event"""
		self.get_handler(event.eventtype(), "", args={"event": event})

	def get_configs(self, filelist=[]):
		"""Gets configuration options from a list of files"""
		from ConfigParser import ConfigParser, NoSectionError, NoOptionError

		config = ConfigParser()
		filelist += MooBot.config_files
		config.read(filelist)
		Debug("Parsed config files:", config.read(filelist))
		# Initialize the things we will return just in case they aren't in
		# any of the files that we parse through.  Then get their values
		# and stick the rest in "others"
		nick=""; username=""; realname=""; server=""
		port=6667; channels=[]; others={}
		encoding = "utf-8"
		try:
			nick = config.get('connection', 'nick')
			username = config.get('connection', 'username')
			realname = config.get('connection', 'realname')
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
		return {'nick': nick, 'username': username,
			'realname': realname, 'server': server, 'port': port,
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
					if newHandler.type not in self.handlers.keys():
						self.handlers[newHandler.type] = []
					self.handlers[newHandler.type].append(newHandler)
					Debug("Added handler:" , handlerName, "for", \
					        newHandler.type, "\"" \
						+ newHandler.regex.pattern + "\"", \
						"priority ", newHandler.instance.priority)
				if importedModule.__name__ not in self.module_list:
					self.module_list.append(importedModule.__name__)
			finally:
				# sort the list (for priorities)
				for key in self.handlers.keys():
					self.handlers[key].sort()
				# Since we may exit via an exception, close fp explicitly.
				if fp:
					fp.close()

	def unload_module(self, event):
		""" remove any handlers from self.handlers that are from any of the
		modules passed in event.arguments()[1:]"""
		module_list = event.arguments()[1:]
		temp = []
		for handlerType in self.handlers.keys():
			for handler in self.handlers[handlerType]:
				if handler.module.__name__ in module_list:
					temp.append((handlerType, handler))
					print handler

		for handlerType, h in temp:
			print h, repr(h)
			self.handlers[handlerType].remove(h)

		for module in module_list:
			if module in self.module_list:
				self.module_list.remove(module)

		# sort the list (for priorities)
		for handlerType in self.handlers.keys():
			self.handlers[handlerType].sort()
	
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

