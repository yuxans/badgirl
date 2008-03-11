#!/usr/bin/env python

"""quake.py -- quake trigger """
from moobot_module import MooBotModule
from irclib import Event
handler_list = ["quake"]
# TODO? move into config file
ip = 3546805303
firstport = 3800

class quake(MooBotModule):
	def __init__(self):
		self.regex = "^quake.*$"

	def handler(self, **args):
		target_back = self.return_to_sender(args)
		target_nick = self.return_to_sender(args, 'nick')
		args = args["text"].split()[2:]
		args_l = len(args)

		if args_l != 1 and args_l != 2:
			return Event("privmsg", "", target_back, [ "syntax: quake <roomid> [invite-nick], roomid in (0...5)" ])

		try:
			roomid = int(args[0])
		except:
			return Event("privmsg", "", target_back, [ "invalid roomid" ])

		if roomid < 1 or roomid >= 6:
			return Event("privmsg", "", target_back, [ "roomid %d not in (0....5) " % roomid ])
				
		text = "DCC CHAT chat %d %d" % (ip, firstport + roomid - 1)
		if args_l == 2:
			return Event("ctcp", "", args[1], [ text ])
		elif args_l == 1:
			return Event("ctcp", "", target_nick, [ text ])
