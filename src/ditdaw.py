#!/usr/bin/env python

# Copyright (c) 2002 Vincent Foley, et. al.
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
handler_list=["ditdaw","dawdit"]

class ditdaw(MooBotModule):
	"""
	Module to convert plain text to morse code for MooBot
	"""

	def __init__(self):
		self.regex = "^ditdaw .+"

	def handler(self, **args):
		# Code definition.	Pretty long
		tr = {
			"A" : ".- ",
			"B" : "-... ",
			"C" : "-.-. ",
			"D" : "-.. ",
			"E" : ". ",
			"F" : "..-. ",
			"G" : "--. ",
			"H" : ".... ",
			"I" : ".. ",
			"J" : ".--- ",
			"K" : "-.- ",
			"L" : ".-.. ",
			"M" : "-- ",
			"N" : "-. ",
			"O" : "--- ",
			"P" : ".--. ",
			"Q" : "--.- ",
			"R" : ".-. ",
			"S" : "... ",
			"T" : "- ",
			"U" : "..- ",
			"V" : "...- ",
			"W" : ".-- ",
			"X" : "-..- ",
			"Y" : "-.-- ",
			"Z" : "--.. ",
			"0" : "----- ",
			"1" : ".---- ",
			"2" : "..--- ",
			"3" : "...-- ",
			"4" : "....- ",
			"5" : "..... ",
			"6" : "-.... ",
			"7" : "--... ",
			"8" : "---.. ",
			"9" : "----. ",
			"?" : "..--.. ",
			"." : ".-.-.- ",
			"," : "--..-- ",
			" " : "	 "
		}
	
		# Strip botname and command
		message = args["text"].split()
		message = " ".join(message[2:]) 
	
		n_message = ""
		
		# Make the message all uppercase
		message = message.upper()
	
		# Make the translation. If the letter has no code in the 
		# translation table, add it in its "natural" form.
		#
		for letter in message:
			try:
				n_message += tr[letter]
			except KeyError:
				n_message += letter + " "
	
		target = self.return_to_sender(args)
	
		from irclib import Event
		result = Event("privmsg", "", target, [ n_message ])
		return result

class dawdit(MooBotModule):
	"""
	Module to convert morse code to plain text for MooBot
	"""

	def __init__(self):
		self.regex = "^dawdit .+"

	def handler(self, **args):
		# Code definition.	Pretty long
		tr = {
			".-"    : "a",
			"-..."  : "b",
			"-.-."  : "c",
			"-.."   : "d",
			"."     : "e",
			"..-."  : "f",
			"--."   : "g",
			"...."  : "h",
			".."    : "i",
			".---"  : "j",
			"-.-"   : "k",
			".-.."  : "l",
			"--"    : "m",
			"-."    : "n",
			"---"   : "o",
			".--."  : "p",
			"--.-"  : "q",
			".-."   : "r",
			"..."   : "s",
			"-"     : "t",
			"..-"   : "u",
			"...-"  : "v",
			".--"   : "w",
			"-..-"  : "x",
			"-.--"  : "y",
			"--.."  : "z",
			"-----" : "0",
			".----" : "1",
			"..---" : "2",
			"...--" : "3",
			"....-" : "4",
			"....." : "5",
			"-...." : "6",
			"--..." : "7",
			"---.." : "8",
			"----." : "9",
			""      : " ",
			"..--.." : "?",
			".-.-.-" : ".",
			"--..--" : ","
		}
	
		# Strip botname and command
		message = args["text"].split(" ")[2:]
	
		n_message = ""
	
		# Make the translation. If the letter has no code in the 
		# translation table, add it in its "natural" form.
		#
		for group in message:
			try:
				n_message += tr[group]
			except KeyError:
				n_message += group + " "
	
		target = self.return_to_sender(args)
	
		from irclib import Event
		result = Event("privmsg", "", target, [ n_message ])
		return result
