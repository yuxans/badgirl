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

"""poll.py -- poll stuff """
from moobot_module import MooBotModule
handler_list = ["show_poll", "vote", "add_poll", "add_poll_option", "list_polls", "remove_poll", "remove_poll_option"]


class show_poll(MooBotModule):
	def __init__(self):
		self.regex = "^poll \d+$"

	def handler(self, **args):
		"""displays a poll"""
		import database
		from irclib import Event
		target=args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
	
		poll_num = args["text"].split()[-1]
		#first we check to make sure the requested poll exists.
		if database.doSQL("select count(poll_num) from poll where poll_num =" + poll_num )[0][0] == 0:
			return Event("privmsg", "", target, [ "No such poll." ])
	
		# Then get the question and each option, add them to a string,
		# and return them.
		text = database.doSQL("select question from poll where poll_num =" + poll_num)[0][0] + "  :  "
		for question in database.doSQL("select * from poll_options where poll_num =" + poll_num + " order by option_key"):
			text += question[1] + ")" + question[2] + " (" + str(database.doSQL("select count(voter_nickmask) from poll_votes where poll_num =" + poll_num + " and option_key = '"+ question[1].replace("'", "\\'")  +"'")[0][0])+ " votes)  ;;  "
	
		return Event("privmsg", "", target, [ text ])
	
class vote(MooBotModule):
	def __init__(self):
		self.regex = "^vote\s\d+\s.+$"

	def handler(self, **args):
		"""votes on a poll."""
		import database

		from irclib import Event
		from irclib import nm_to_h, nm_to_u
		target=args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
	
		poll_num = args["text"].split()[2]
		option_key = " ".join(args["text"].split()[3:])
		#first we check to make sure the requested poll exists.
		if database.doSQL("select count(poll_num) from poll where poll_num =" +poll_num)[0][0] == 0:
			return Event("privmsg", "", target, [ "No such poll." ])
	
		#now we check to make sure the user hasn't voted in that poll
		checkmask = "%!" + nm_to_u(args["source"]) + "@%" + nm_to_h(args["source"])[nm_to_h(args["source"]).find("."):]
		if database.doSQL("select count(option_key) from poll_votes where poll_num =" + poll_num + " and voter_nickmask like '" + checkmask + "'")[0][0] != 0:
			return Event("privmsg", "", target, [ "You already voted in that poll." ])
	
		#next we check to make sure the poll option exists.
		option_key = self.sqlEscape(option_key)
		if database.doSQL("select count(option_key) from poll_options where poll_num =" + poll_num + " and option_key = '" + option_key + "'")[0][0] == 0:
			return Event("privmsg", "", target, [ "No such poll option." ])
	
		# register the vote.
		database.doSQL("insert into poll_votes values('" + args["source"] + "', '" + option_key + "', " + poll_num + ")")
	
		return Event("privmsg", "", target, [ "Vote registered." ])
	
class add_poll(MooBotModule):
	def __init__(self):
		self.regex = "^add poll .+$"

	def handler(self, **args):
		""" Adds a new poll. """
		import database
		import priv
		from irclib import Event
		target=args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
		
		if priv.checkPriv(args["source"], "poll_priv") == 0:
			return Event("privmsg", "", target, [ "You are not authorized to do that." ])
		
		poll_question = " ".join(args["text"].split()[3:])
		poll_question = self.sqlEscape(poll_question)
		database.doSQL("Insert into poll(question) values('" + poll_question + "')")
		poll_num = database.doSQL("select poll_num from poll where question = '" + poll_question + "'")[0][0]
		return Event("privmsg", "", target, [ "Poll added. as number " + str(poll_num) + "." ])
	
			
class add_poll_option(MooBotModule):
	def __init__(self):
		self.regex = "^add option \d+ .+: .+"

	def handler(self, **args):
		""" Adds a poll option to an existing poll. 
		Format:
		moobot:  add option 1 a: yes"""
		import database
		import priv
		from irclib import Event
		target=args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
		
		if priv.checkPriv(args["source"], "poll_priv") == 0:
			return Event("privmsg", "", target, [ "You are not authorized to do that." ])
		
		poll_num = args["text"].split()[3]
		option = " ".join(args["text"].split()[4:])
		option_key = self.sqlEscape(option.split(":")[0])
		option_text = self.sqlEscape(" ".join(option.split(":")[1:]))
		if database.doSQL("select count(poll_num) from poll where poll_num =" + poll_num )[0][0] == 0:
			return Event("privmsg", "", target, [ "No such poll." ])
	
		self.debug("Insert into poll_options(poll_num, option_key, option_text) values(" + poll_num + ", \"" + option_key + "\", \"" + option_text + "\")")
		database.doSQL("Insert into poll_options(poll_num, option_key, option_text) values(" + poll_num + ", '" + option_key + "', '" + option_text + "')")
		return Event("privmsg", "", target, [ "Option added." ])
	
	
class list_polls(MooBotModule):
	def __init__(self):
		self.regex = "^(list )?polls$"

	def handler(self, **args):
		"List all polls available to be voted on"
		import database	
		from irclib import Event, nm_to_n
	
		if args["type"] == "privmsg": target=nm_to_n(args["source"])
		else: target=args["channel"]
		
		msg = ""
		if database.type == "mysql":
			questions = database.doSQL("select question, poll.poll_num, count(poll_votes.poll_num) from poll, poll_votes where poll.poll_num = poll_votes.poll_num group by poll_num")
		elif database.type == "pgsql":
			questions = database.doSQL("select question, poll.poll_num, count(poll_votes.poll_num) from poll, poll_votes where poll.poll_num = poll_votes.poll_num group by poll.poll_num, question") 
		for tuple in questions:
			msg += str(int(tuple[1])) + " - " + tuple[0] + " (" + str(tuple[2]) + " votes)\n"
		return Event("privmsg", "", target, [msg])
	
class remove_poll(MooBotModule):
	def __init__(self):
		self.regex = "^(remove|delete) poll \d+$"

	def handler(self, **args):
		""" removes a poll. 
		Syntax:
		moobot: remove poll #"""
		import database, priv
		from irclib import Event
		target=args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
		
		if priv.checkPriv(args["source"], "poll_priv") == 0:
			return Event("privmsg", "", target, [ "You are not authorized to do that." ])
		
		poll_num = args["text"].split()[3]
		database.doSQL("delete from poll_votes where poll_num = " + poll_num)
		database.doSQL("delete from poll_options where poll_num = " + poll_num)
		database.doSQL("delete from poll where poll_num = " + poll_num)
		return Event("privmsg", "", target, [ "Poll deleted." ])
			
class remove_poll_option(MooBotModule):
	def __init__(self):
		self.regex = "^(remove|delete) option \d+ .+$"

	def handler(self, **args):
		""" remove a poll option to an existing poll. 
		Format:
		moobot:  remove option <pollnum> <option> """
		import database
		import priv
		from irclib import Event
		target=args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
		
		if priv.checkPriv(args["source"], "poll_priv") == 0:
			return Event("privmsg", "", target, [ "You are not authorized to do that." ])
		
		option_key = "".join(args["text"].split()[4:])
		poll_num = self.sqlEscape(args["text"].split()[3])
	
		database.doSQL("delete from poll_options where poll_num = " + poll_num + " and option_key = '" + option_key + "'")
		return Event("privmsg", "", target, [ "Option deleted." ])
		
