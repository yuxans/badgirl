#!/usr/bin/env python
# Copyright (C) 1999, 2000 Phil Gregory
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#		
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# Phil Gregory <phil_g+moobot@pobox.com>

"""moolog -- logging of moobot events"""

handler_list=["moolog"]

import string
import time
from moobot_module import MooBotModule
from utilities import *

logtype = ""
template = ""
logfile = None

class moolog(MooBotModule):
	def __init__(self):
		self.type='all'
		self.priority = -100
	def handler(self, **args):
		logevent(args["event"])

def logevent(ev):
	"""Takes an IRC event and logs it."""

	log_ev_to_file(ev)
	log_ev_to_stdout(ev)


def log_ev_to_file(ev):
	"""Logs an event to a log file."""

	check_logfile()

	if logfile != None:
		args = {}
		args["type"] = ev.eventtype().upper()
		args["src"] = ev.source()
		args["dst"] = ev.target()
		args["args"] = "".join(ev.arguments())


		if args["type"] in ["JOIN", "NICK"]:
			print >> logfile, time.strftime("%Y-%m-%d %H:%M:%S"),
			print >> logfile, ":%s %s :%s" % (
				args["src"], args["type"], args["dst"])
		elif args["type"] in ["KICK", "ENDOFNAMES", "LUSEROP",
				      "LUSERCHANNELS", "AWAY", "CHANOPRIVSNEEDED",
				      "NICKNAMEINUSE", "BANNEDFROMCHAN"]:
			print >> logfile, time.strftime("%Y-%m-%d %H:%M:%S"),
			print >> logfile, ":%s %s %s %s :%s" % (
				args["src"], args["type"], args["dst"],
				ev.arguments()[0], ev.arguments()[1])
		elif args["type"] == "TOPIC" and len(ev.arguments()) == 2:
			print >> logfile, time.strftime("%Y-%m-%d %H:%M:%S"),
			print >> logfile, ":%s %s %s :%s" % (
				args["src"], args["type"], ev.arguments()[0],
				ev.arguments()[1])
		elif args["type"] in ["MODE", "TOPICINFO", "MYINFO",
				      "FEATURELIST"]:
			print >> logfile, time.strftime("%Y-%m-%d %H:%M:%S"),
			print >> logfile, ":%s %s %s %s" % (
				args["src"], args["type"], args["dst"],
				args["args"])
		elif args["type"] == "NAMREPLY":
			print >> logfile, time.strftime("%Y-%m-%d %H:%M:%S"),
			print >> logfile, ":%s %s %s %s %s :%s" % (
				args["src"], args["type"], args["dst"],
				ev.arguments()[0], ev.arguments()[1],
				ev.arguments()[2])
		elif args["dst"] == None:
			print >> logfile, time.strftime("%Y-%m-%d %H:%M:%S"),
			print >> logfile, ":%s %s :%s" % (
				args["src"], args["type"], args["args"])
		elif args["type"] in ["CONTINUE", "PING", "INTERNAL"]:
			pass
		elif len(ev.arguments()) == 0:
			print >> logfile, time.strftime("%Y-%m-%d %H:%M:%S"),
			print >> logfile, ":%s %s %s" % (
				args["src"], args["type"], args["dst"])
		elif args["type"] in ["PRIVMSG", "PUBMSG"]:
			for line in args["args"].split("\n"):
				if line != "":
					print >> logfile, time.strftime("%Y-%m-%d %H:%M:%S"),
					print >> logfile, ":%s %s %s :%s" % (
						args["src"], args["type"], args["dst"], line)
		else:
			print >> logfile, time.strftime("%Y-%m-%d %H:%M:%S"),
			print >> logfile, ":%s %s %s :%s" % (
				args["src"], args["type"], args["dst"], args["args"])

		logfile.flush()


def check_logfile():
	global logtype, template, logfile

	import database

	if logtype == "":
		line = database.doSQL("SELECT data FROM data WHERE type = 'logtype'")
		if len(line) > 0 and len(line[0]) > 0:
			logtype = line[0][0]
	if template == "":
		line = database.doSQL("SELECT data FROM data WHERE type = 'logfile'")
		if len(line) > 0 and len(line[0]) > 0:
			template = line[0][0]

	if logtype in ["date", "file"] and template == "":
		if (logfile != None):
			logfile.close()
		print "logtype is " + logtype + ", but there is no logfile entry."
		logfile = None
		return

	if logtype == "date":
		filename = time.strftime(template)
	elif logtype == "file":
		filename = template
	else:
		return

	if (logfile != None and filename != logfile.name):
		logfile.close()
	if (logfile == None or filename != logfile.name):
		logfile = open(filename, "a")


def log_ev_to_stdout(ev):
	"""Displays an event in nice colors."""

	args = {}
	args["type"] = ev.eventtype().upper()
	args["src"] = ev.source()
	args["dst"] = ev.target()
	args["args"] = "".join(ev.arguments())

	if args["src"]:
		hostmask = args["src"].split("!")
		nick = hostmask[0]
		if len(hostmask) > 1:
			host = hostmask[1]
	else:
		nick = ""
	channel = args["dst"]
	if args["type"] == "JOIN":
		print time.strftime("%H:%M:%S"),
		print GREEN + "-->" + NORMAL + " " + \
			  YELLOW + nick + NORMAL + " " + \
			  RED + "joined" + NORMAL + " " +\
			  BLUE + channel + NORMAL
	elif args["type"] == "INVITE":
		print time.strftime("%H:%M:%S"),
		print GREEN + "--?" + NORMAL + " " + \
			  RED + "invited to" + NORMAL + " " + \
			  BLUE + args["args"] + NORMAL + " " + \
			  "by " + \
			  YELLOW + nick + NORMAL
	elif args["type"] == "NICK":
		print time.strftime("%H:%M:%S"),
		print GREEN + "---" + NORMAL + " " + \
			  YELLOW + nick + NORMAL + " " + \
			  RED + "changed nick to" + NORMAL + " " + \
			  YELLOW + args["dst"] + NORMAL + " " + \
			  "[" + PURPLE + host + NORMAL + "]"
	elif args["type"] == "NICKNAMEINUSE":
		print time.strftime("%H:%M:%S"),
		print GREEN + "===" + NORMAL + " " + \
			  RED + "nick already in use" + NORMAL + \
			  ": " + \
			  YELLOW + ev.arguments()[0] + NORMAL
	elif args["type"] == "KICK":
		print time.strftime("%H:%M:%S"),
		print GREEN + "<--" + NORMAL + " " + \
			  YELLOW + ev.arguments()[0] + NORMAL + " " + \
			  RED + "was kicked from" + NORMAL + " " + \
			  BLUE + channel + NORMAL + " " + \
			  "by " + \
			  YELLOW + nick + NORMAL + " " + \
			  "(" + ev.arguments()[1] + ")"
	elif args["type"] == "BANNEDFROMCHAN":
		print time.strftime("%H:%M:%S"),
		print GREEN + "xxx" + NORMAL + " " + \
			  YELLOW + args["dst"] + NORMAL + " " + \
			  RED + "is banned from" + NORMAL + " " + \
			  BLUE + ev.arguments()[0] + NORMAL
	elif args["type"] == "CHANOPRIVSNEEDED":
		print time.strftime("%H:%M:%S"),
		print GREEN + "///" + NORMAL + " " + \
			  YELLOW + args["dst"] + NORMAL + " " + \
			  RED + "is not opped on" + NORMAL + " " + \
			  BLUE + ev.arguments()[0] + NORMAL
	elif args["type"] == "TOPIC" and len(ev.arguments()) == 2:
		print time.strftime("%H:%M:%S"),
		print GREEN + "---" + NORMAL + " " + \
			  BLUE + ev.arguments()[0] + NORMAL + " " + \
			  RED + "topic is" + NORMAL + " " + \
			  ev.arguments()[1]
	elif args["type"] == "TOPIC":
		print time.strftime("%H:%M:%S"),
		print GREEN + "---" + NORMAL + " " + \
			  YELLOW + nick + NORMAL + " " + \
			  RED + "sets topic on" + NORMAL + " " + \
			  BLUE + channel + NORMAL + " " + \
			  "to " + args["args"]
	elif args["type"] == "TOPICINFO":
		print time.strftime("%H:%M:%S"),
		print GREEN + "---" + NORMAL + " " + \
			  RED + "topic set by" + NORMAL + " " + \
			  YELLOW + ev.arguments()[1] + NORMAL + " " + \
			  "at " + time.strftime("%a, %b %d %X", time.localtime(int(ev.arguments()[2])))
	elif args["type"] == "NAMREPLY":
		print time.strftime("%H:%M:%S"),
		print GREEN + "---" + NORMAL + " " + \
			  RED + "users on" + NORMAL + " " + \
			  BLUE + ev.arguments()[1] + NORMAL + ": " + \
			  YELLOW + ev.arguments()[2] + NORMAL
	elif args["type"] == "MODE":
		print time.strftime("%H:%M:%S"),
		print GREEN + "---" + NORMAL + " " + \
			  BLUE + channel + NORMAL + " " + \
			  RED + "mode change by" + NORMAL + " " + \
			  YELLOW + nick + NORMAL + " " + \
			  args["args"]
	elif args["type"] in ["MOTDSTART", "MOTD", "ENDOFMOTD"]:
		print time.strftime("%H:%M:%S"),
		print GREEN + "===" + NORMAL + " " + \
			  RED + "MOTD" + NORMAL + " " + \
			  ": " + args["args"]
	elif args["type"] in ["WELCOME", "YOURHOST", "CREATED", "MYINFO",
			      "FEATURELIST", "LUSERCLIENT", "LUSEROP",
			      "LUSERCHANNELS", "LUSERME", "N_LOCAL", "N_GLOBAL",
			      "LUSERCONNS"]:
		print time.strftime("%H:%M:%S"),
		print GREEN + "===" + NORMAL + " " + \
			  RED + "servinfo" + NORMAL + " " + \
			  ": " + args["args"]
	elif args["type"] == "PART":
		print time.strftime("%H:%M:%S"),
		print GREEN + "<--" + NORMAL + " " + \
			  YELLOW + nick + NORMAL + " " + \
			  RED + "parted from" + NORMAL + " " + \
			  BLUE + channel + NORMAL + " " + \
			  "(" + args["args"] + ")"
	elif args["type"] == "QUIT":
		print time.strftime("%H:%M:%S"),
		print GREEN + "<--" + NORMAL + " " + \
			  YELLOW + nick + NORMAL + " " + \
			  RED + "quit IRC" + NORMAL + " " + \
			  "(" + args["args"] + ")"
	elif args["type"] in ["PRIVNOTICE", "PUBNOTICE"]:
		print time.strftime("%H:%M:%S"),
		print GREEN + "-" + NORMAL + \
			  YELLOW + nick + NORMAL + \
			  "/" + \
			  BLUE + channel + NORMAL + \
			  GREEN + "-" + NORMAL + " " + \
			  args["args"]
	elif args["type"] in ["PRIVMSG", "PUBMSG"]:
		for line in args["args"].split("\n"):
			if line != "":
				print time.strftime("%H:%M:%S"),
				print GREEN + "<" + NORMAL + \
				      YELLOW + nick + NORMAL + \
				      "/" + \
				      BLUE + channel + NORMAL + \
				      GREEN + ">" + NORMAL + " " + \
				      line
	elif args["type"] == "CTCP" and ev.arguments()[0] == "ACTION":
		print time.strftime("%H:%M:%S"),
		print GREEN + "*" + NORMAL + " " + \
			  YELLOW + nick + NORMAL + \
			  "/" + \
			  BLUE + channel + NORMAL + " " + \
			  ev.arguments()[1]
	elif args["type"] in ["ENDOFNAMES", "CONTINUE", "PING", "INTERNAL"]:
		pass
	else:
		print time.strftime("%H:%M:%S"),
		print ":%s %s %s :%s" % (
			args["src"], args["type"], args["dst"], args["args"])
		
