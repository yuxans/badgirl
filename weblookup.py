#!/usr/bin/env python

# Copyright (c) 2002 Daniel DiPaolo, et. al.
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

import httplib
from moobot_module import MooBotModule
handler_list = ["slashdot", "google", "kernelStatus", "insult", "excuse", "dict", "zipcode", "babelfish"]

class slashdot(MooBotModule):
	def __init__(self):
		self.regex = "^slashdot$"

	def handler(self, **args):
		"Gets headlines from slashdot.org"
		from irclib import Event, nm_to_n
		target = self.return_to_sender(args)

		connect = httplib.HTTPConnection('slashdot.org', 80)
		connect.request("GET", "/slashdot.rdf")
		response = connect.getresponse()
		if response.status != 200:
			msg = response.status + ": " + response.reason
			print msg
			return Event("privmsg", "", target, [msg])
		else:
			import re
			# Do the parsing here
			listing = response.read()
			listing = listing.split("\n")
			regex = re.compile("^<title>.*</title>$", re.IGNORECASE)
			match_count = 0
			articles = []
			for item in listing:
				if regex.match(item):
					match_count += 1
					# ignore the first two
					if match_count != 1 and match_count != 2:
						item = re.sub("</*title>", "", item)
						articles.append(item)	
			# Drop the last one as well
			articles = articles[:len(articles)-1]
			match_count -= 3
			# now lets make it into a big string
			string = "Slashdot Headlines (" + str(match_count) + " shown): "
			for article in articles:
				string += article + " ;; "
			# and send it back
			string = string[:len(string)-4] + "."
			string = string.replace("amp;", "")
			connect.close()
			return Event("privmsg", "", target, [string])
	
class google(MooBotModule):
	"Does a search on google and returns the first 5 hits"
	def __init__(self):
		self.regex = "^google for .+"

	def handler(self, **args):
		from irclib import Event, nm_to_n
		import string
		self.return_to_sender(args)
		
		search_terms = args["text"].split(" ")[3:]
		search_request = "/ie?hl=zh-CN&oe=GBK&ie=GBK&q="
									# the resulting output so much nicer
		search_request += string.join(search_terms, "+")
		connect = httplib.HTTPConnection('www.google.com', 80)
		connect.request("GET", search_request) 
		response = connect.getresponse()
		if response.status != 200:
			msg = response.status + ": " + response.reason
			print msg
			return Event("privmsg", "", target, [msg])
		else:
			listing = response.read()
		urls=[]
		for i in listing.split():
			if string.find(i, "HREF=http://") >= 0:
				url = i[:string.find(i, ">")]
				url = url[5:]
				urls.append(url)
		line = "Google says \"" + string.join(search_terms) + "\" is at: "
		count=0
		for url in urls:
			count += 1
			if count <= 5:
				line += url + " "
		return Event("privmsg", "", self.return_to_sender(args), [ line ])
	
class kernelStatus(MooBotModule):
	def __init__(self):
		self.regex = "^kernel$"

	def handler(self, **args):
		"""gets kernel status"""
		print "kernelStatus"
		from telnetlib import Telnet
		import string
		connection=Telnet("kernel.org", 79)
		connection.write("\n")
		text=""
		text = connection.read_all()
	
		# Extract just the version numbers, instead of flooding
		# the channel with everything.
		result = ""
		for line in text.split("\n"):
			if len(line.split(":")) > 1:
				line = line.split(" ", 2)[2]
				version = string.strip(line.split(":")[1]) + " ;; "
				line = line.split("of", 2)[0]
				line = line.split("for", 2)[0]
				line = line.split("to", 2)[0]
				result += string.strip(line) + ":   " + version
	
		from irclib import Event
		target = self.return_to_sender(args)
		return Event("privmsg", "", target, [ result ])
	
class insult(MooBotModule):
	def __init__(self):
		self.regex = "^insult .+"
	def handler(self, **args):
		"""gets an insult"""
		from telnetlib import Telnet
		connection=Telnet("insulthost.colorado.edu", 1695)
		connection.write("\n")
		text=""
		#i=connection.read_some()
		#while i != '':
		#	text = text + i
		#	i=connection.read_some()
		text = connection.read_all()
	
		import string
		who = args["text"]
		who = who[string.find(who, " ")+1:]
		who = who[string.find(who, " ")+1:]
		text = string.replace(text, "You are", who + " is")
		from irclib import Event
		target = self.return_to_sender(args)
		result = Event("privmsg", "", target, [ text ])
		return result
	
class excuse(MooBotModule):
	def __init__(self):
		self.regex = "^excuse$"
	def handler(self, **args):
		"Grabs an excuse from the BOFH excuse server"
		from telnetlib import Telnet
		connection=Telnet("athena.jive.org", 666)
		text = ""
		text = connection.read_all()
		#i = connection.read_some()
		#while i != "":
		#	text = text + i
		#	i = connection.read_some()
		connection.close()
		text = text.split("\n")
		from string import join
 		msg = join(text[3:-1])	# The first three lines and the last are unneeded
		
		from irclib import Event
		target = self.return_to_sender(args)
		return Event("privmsg", "", target, [msg])

class dict(MooBotModule):
	def __init__(self):
		self.regex = "^dict .+$"

	def handler(self, **args):
		import string
		from irclib import Event
		target = self.return_to_sender(args)
		defs = self.lookup(string.join(args["text"].split()[2:]))
		result = ""
		for element in defs:
			for line in element.split("."):
				if len( result + line) < 800:
					result += line
		if len(defs) == 0:
			result = "Could not find definition for " + string.join(args["text"].split()[2:])
		return Event("privmsg", "", target, [ result ])

	def lookup(self, word):
		""" parse the definitions"""
		import string
		output = self.raw_lookup(word).replace("\r\n", "\n")
		if string.find(output, "552 no match") >= 0 or string.find(output, "501 syntax error") >= 0 or string.find(output, "\n150") < 0:
			return []
		output = output.split("\n150", 1)[1]
		defs = output.split("\n.\n")

		results = []
		for d in defs:
			line = d.replace("\n", " ").strip()
			while line.find("  ") >= 0:
				line = line.replace("  ", " ")
			#if line[0] in "123456789/" and len(line)  <= 200:
			#if len(line)  <= 200:
			if d != defs[0] and d != defs[-1]:
				results.append(string.join(line.split()[1:]))
		return results

	def raw_lookup(self, word):
		"""gets word definition"""
		import telnetlib 
		import time
		connection=telnetlib.Telnet("dict.org", 2628)
		connection.write("define * " + word + "\r\n")
		text=""
		while connection.read_eager() == "":
		   time.sleep(.5)
		i=connection.read_eager()
		while i != '':
			text = text + i
			i=connection.read_eager()

		connection.write("quit\n\r")
		connection.close()
		return text

class zipcode(MooBotModule):
	def __init__(self):
		self.regex="^zipcode.*"

	def handler(self, **args):
		"""A dummy handler we used for testing -- this is the first handler
		we wrote"""
		from irclib import Event
		import httplib

		message = 'zipinfo.com: '
		

		info = self.parse_cmdline(args['text'])
		if info[0] == None:
			message += info[1]
		else:
			(zipcode, flags) = info
			request = self.get_zipinfo_cgi_request(info[0], info[1])
			conn = httplib.HTTPConnection('www.zipinfo.com')
 			conn.request('GET', request)
			response = conn.getresponse()
			conn.close()
			if response.status != 200:
				print 'response from zipinfo' + str(status), reason
			else: 
				data = response.read()
				message += self.parse_zipinfo_response(data, flags)

		return Event("privmsg", "", self.return_to_sender(args), [ message ])

	def parse_cmdline(self, cmdline):
		words = cmdline.split()
		if len(words) < 3 or len(words) > 4:
			return(None, '"zipcode [c][a][t][l] \d+" (i.e zipcode ca 12458)')
		else:
			zipcode = words.pop()
			if len(zipcode) != 5:
				return (None, "zipcode must be 5 digits only")
			else:
				try:
					int_check = int(zipcode)
				except ValueError:
					return (None, 'invalid zipcode: ' + '"' + zipcode + '"')

		if (len(words) == 3):
			flags = words.pop()
		else:
			flags = ''

		return (zipcode, flags)

					
	def get_zipinfo_cgi_request(self, zipcode, flags):
		req = '/cgi-local/zipsrch.exe?'
		if 'c' in flags:
			req += 'cnty=cnty&'
		if 'a' in flags:
			req += 'ac=ac&'
		if 't' in flags:
			req += 'tz=tz&'
		if 'l' in flags:
			req += 'll=ll&'

		if req[-1] != '&':
			req += '&'

		req += 'zip=' + str(zipcode)

		req += '&Go=Go'
	
		return req
		
	def parse_zipinfo_response(self, data, flags):
		if data.find('not currently assigned') != -1:
			message = "sorry, that zipcode isn't currently in use"
		elif data.find('reached the daily usage limit') != -1:
			message = "sorry, they've locked me out. too many requests. try again tomorrow"
		elif data.find('is not a valid ZIP code') != -1:
			message = "the zipcode you provided is invalid."
		else:
			TDTAG = '<td align=center>'

			pos1 = data.find('Mailing') # skip into this table
			pos1 = data.find(TDTAG, pos1+1)
			pos2 = data.find('<', pos1+1)
			
			print pos1, pos2, data[pos1:pos2]
			message = data[pos1+len(TDTAG):pos2]
			message += ', '
	
			pos1 = data.find(TDTAG, pos2)
			pos2 = data.find('<', pos1+1)
			message += data[pos1+len(TDTAG):pos2]
		
			pos1 = data.find(TDTAG, pos2)
			pos2 = data.find('<', pos1+1)
			if 'c' in flags:
				pos1 = data.find(TDTAG, pos2)
				pos2 = data.find('<', pos1+1)
				message += '; county: ' + data[pos1+len(TDTAG):pos2]
				pos1 = data.find(TDTAG, pos2)
				pos2 = data.find('<', pos1+1)
				#pos1 = data.find(TDTAG, pos1+1)

			if 'a' in flags:
				pos1 = data.find(TDTAG, pos2)
				pos2 = data.find('<', pos1+1)
				message += '; aread code: ' + data[pos1+len(TDTAG):pos2]

			if 't' in flags:
				pos1 = data.find(TDTAG, pos2)
				pos2 = data.find('<', pos1+1)
				message += '; time zone: ' + data[pos1+len(TDTAG):pos2]
				pos1 = data.find(TDTAG, pos2)
				pos2 = data.find('<', pos1+1)
				daylight = data[pos1+len(TDTAG):pos2]
				if daylight.lower() == 'yes':
					message += '(d)'

			if 'l' in flags:
				pos1 = data.find(TDTAG, pos2)
				pos2 = data.find('<', pos1+1)
				lat = data[pos1+len(TDTAG):pos2]
				pos1 = data.find(TDTAG, pos2)
				pos2 = data.find('<', pos1+1)
				long = data[pos1+len(TDTAG):pos2]
				message += '; %sN/%sW ' % (lat, long)

		return message

class babelfish(MooBotModule):
	"Does a search on babelfish.altavista.com and returns the translation"
	def __init__(self):
		self.regex = "^(babelfish|translate) \w+ to \w+ .+"

		# the languages babelfish can do
		self.languages = { "english" : "en", "chinese" : "zh",
					"french" : "fr", "german" : "de",
					"italian" : "it", "japanese" : "ja",
					"korean" : "ko", "portuguese" : "pt",
					"russian" : "ru", "spanish" : "es"}

		# the combinations (from_to) that babelfish can translate
		self.translations =[ "en_zh", "en_fr", "en_de" , "en_it",
			"en_ja", "en_ko" , "en_pt", "en_es" , "zh_en",
			"fr_en" , "fr_de", "de_en", "de_fr" , "it_en",
			"ja_en", "ko_en", "pt_en", "ru_en", "es_en"]

	def handler(self, **args):
		from irclib import Event, nm_to_n
		import string, re
		
		request = args["text"].split(" ", 2)[2] # chop off the "moobot: babelfish"
							# to get something like "english to spanish foo"
		from_language = request.split()[0] # the source language
		to_language = request.split()[2] # the destination language
		translation_text = string.join(request.split()[3:], "+") # the string to translate
						# we also switch whitespace for +s here,
						# to work in the HTTP request

		# check if we know the languages they want to use
		if from_language.lower() not in self.languages.keys() :
			return Event("privmsg", "", self.return_to_sender(args), 
				[ "unknown language: " + from_language ])
		if to_language.lower() not in self.languages.keys():
			return Event("privmsg", "", self.return_to_sender(args), 
				[ "unknown language: " + to_language ])

		# the value for the lp= field for the cgi arguments
		translation_key = "%s_%s" % (self.languages[from_language.lower()], 
			self.languages[to_language.lower()])

		# make sure the translation_key is one we can use
		if translation_key not in self.translations:
			return Event("privmsg", "", self.return_to_sender(args), 
				[ "Babelfish doesn't know how to do %s to %s" % 
				(from_language, to_language)])

		search_request = "/tr?tt=urltext&urltext=%s&lp=%s" % \
			(translation_text, translation_key) # create the HTTP request

		# connect, make the reauest
		connect = httplib.HTTPConnection('babelfish.altavista.com', 80)
		connect.request("GET", search_request) 

		response = connect.getresponse()
		if response.status != 200: # check for errors
			msg = response.status + ": " + response.reason
			print msg
			return Event("privmsg", "", target, [msg])
		else:
			listing = response.read() # grab the html source
			listing = string.replace(listing, '\n', '') # get rid of newlines

		searchRegex = re.compile("<textarea[^<]+</textarea>")
		searchRegex2 = re.compile("<td bgcolor=white[^<]+</td>")
				#for some reason, the results are sometimes in a textarea,
				# and sometimes in a table.  We check if there's a 
				# <td bgcolor=white before the first textarea, if there is,
				# we use that.
		if searchRegex2.search(listing) != None:
			match = searchRegex2.search(listing)
		else:
			match = searchRegex.search(listing)

		result = match.group() #get the whole textarea node
		result = string.replace(result, "</textarea>", "")#chop off the closing tag
		result = string.replace(result, "</td>", "")#chop off the closing tag
		result = result[result.find(">")+1:] # chop off everything up to the first >
						# which should be the opening textarea or td 
						# tag

		return Event("privmsg", "", self.return_to_sender(args), 
			[ "Translation: " + result ])
