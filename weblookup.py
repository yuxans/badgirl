#!/usr/bin/env python

# Copyright (c) 2002 Daniel DiPaolo, et. al.
# Copyright (C) 2005 by baa
# Copyright (C) 2005 by FKtPp
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
handler_list = ["slashdot", "google", # "insult", "excuse", "kernelStatus"
		"dict", "zipcode", "babelfish"]

class slashdot(MooBotModule):
	def __init__(self):
		self.regex = "^slashdot$"

	def handler(self, **args):
		"Gets headlines from slashdot.org"
		from irclib import Event
		target = self.return_to_sender(args)

		connect = httplib.HTTPConnection('slashdot.org', 80)
		connect.request("GET", "/slashdot.rdf")
		response = connect.getresponse()
		if response.status != 200:
			msg = response.status + ": " + response.reason
			self.debug(msg)
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
		from irclib import Event
		import string
		self.return_to_sender(args)
		
		search_terms = args["text"].split(" ")[3:]
		search_request = "/ie?hl=zh-CN&oe=UTF-8&ie=UTF-8&q="
									# the resulting output so much nicer
		search_request += string.join(search_terms, "+").encode("UTF-8", 'replace')
		connect = httplib.HTTPConnection('www.google.com', 80)
		connect.request("GET", search_request) 
		response = connect.getresponse()
		if response.status != 200:
			msg = response.status + ": " + response.reason
			self.debug(msg)
			return Event("privmsg", "", target, [msg])
		else:
			listing = response.read().decode("UTF-8", 'replace')
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
	
# class kernelStatus(MooBotModule):
# 	def __init__(self):
# 		self.regex = "^kernel$"

# 	def handler(self, **args):
# 		"""gets kernel status"""
# 		self.debug("kernelStatus")
# 		from telnetlib import Telnet
# 		import string
# 		connection=Telnet("kernel.org", 79)
# 		connection.write("\n")
# 		text=""
# 		text = connection.read_all()
	
# 		# Extract just the version numbers, instead of flooding
# 		# the channel with everything.
# 		result = ""
# 		for line in text.split("\n"):
# 			if len(line.split(":")) > 1:
# 				line = line.split(" ", 2)[2]
# 				version = string.strip(line.split(":")[1]) + " ;; "
# 				line = line.split("of", 2)[0]
# 				line = line.split("for", 2)[0]
# 				line = line.split("to", 2)[0]
# 				result += string.strip(line) + ":   " + version
	
# 		from irclib import Event
# 		target = self.return_to_sender(args)
# 		return Event("privmsg", "", target, [ result ])
	
# class insult(MooBotModule):
# 	def __init__(self):
# 		self.regex = "^insult .+"
# 	def handler(self, **args):
# 		"""gets an insult"""
# 		from telnetlib import Telnet
# 		connection=Telnet("insulthost.colorado.edu", 1695)
# 		connection.write("\n")
# 		text=""
# 		#i=connection.read_some()
# 		#while i != '':
# 		#	text = text + i
# 		#	i=connection.read_some()
# 		text = connection.read_all()
	
# 		import string
# 		who = args["text"]
# 		who = who[string.find(who, " ")+1:]
# 		who = who[string.find(who, " ")+1:]
# 		text = string.replace(text, "You are", who + " is")
# 		from irclib import Event
# 		target = self.return_to_sender(args)
# 		result = Event("privmsg", "", target, [ text ])
# 		return result
	
# class excuse(MooBotModule):
# 	def __init__(self):
# 		self.regex = "^excuse$"
# 	def handler(self, **args):
# 		"Grabs an excuse from the BOFH excuse server"
# 		from telnetlib import Telnet
# 		connection=Telnet("athena.jive.org", 666)
# 		text = ""
# 		text = connection.read_all()
# 		#i = connection.read_some()
# 		#while i != "":
# 		#	text = text + i
# 		#	i = connection.read_some()
# 		connection.close()
# 		text = text.split("\n")
# 		from string import join
#  		msg = join(text[3:-1])	# The first three lines and the last are unneeded
		
# 		from irclib import Event
# 		target = self.return_to_sender(args)
# 		return Event("privmsg", "", target, [msg])

class dict(MooBotModule):
	def __init__(self):
		import re
		# have problem filtering out `|' character
		self.regex = "^(dict |~)[^~\+\*/\\<>-]+"
		self.rStrip = re.compile("(<.*?>)+")
		self.rWord = re.compile("^<!-- WORD", re.I)
		self.rGif = re.compile("/gif/([\\w_]+)\\.gif", re.I)
		self.rBody = re.compile("^<!-- BODY", re.I)
		self.ymap = {"slash": "/", "quote": "'", "_e_": 2, "_a": "a:", "int": "S"}
		self.cmap = {"\\\\": "\\", "5": "'", "E": "2"}
		# 参见文件头 coding
		# 新版本才可以用 u"GBK"
		self.rNx = re.compile("找不到和您查询的".decode("gbk"))
		self.rCtoE = re.compile("简明汉英词典(.*)".decode("gbk"), re.M)
		self.rBlue = re.compile("<font color=blue>", re.I)
		self.rEtoC = re.compile("简明英汉词典</div>(.*?)</div>".decode("gbk"), re.S)
		self.rSpell = re.compile("str2img\('([^']+)", re.I)
		self.rExpl = re.compile(u'class="explain_(?:attr|item)">(.*)', re.I)

 	def handler(self, **args):
 		from irclib import Event
 		target = self.return_to_sender(args)
		if args["text"].split()[1][0][0] == '~':
			word = "".join(args["text"].split()[1:])[1:]
		else:
			word = "".join(args["text"].split()[2:])
 		# result = self.lookup_yahoo(word)
 		result = self.lookup_ciba(word)
		result = result.replace("&lt;","<").replace("&gt;",">")
 		if len(result) == 0:
 			result = "Could not find definition for " + word
 		return Event("privmsg", "", target, [ result ])

	def lookup_ciba(self, word):
		connect = httplib.HTTPConnection('cb.kingsoft.com', 80)
		connect.request("GET", "/search?s=%s&t=word&lang=utf-8" % (word.encode("UTF-8"), ))
		response = connect.getresponse()
		if response.status != 200:
			msg = "%d:%s" % (response.status, response.reason)
			loc = response.getheader("location")
			self.debug("dict word(%s) err(%s) loc(%s)" % (word, msg, loc))
			return "error"
		else:
			# Do the parsing here
			html = response.read().decode("UTF-8", "ignore")
			if self.rNx.search(html):
				return ""
	
			m = self.rCtoE.search(html)
			if m:
				m = self.rBlue.split(m.group(1))[1:]
				words = []
				for i in m:
					words.append(i[:i.find("<")])
				return word + ": " + ", ".join(words)
	
			m = self.rEtoC.search(html)
			if m:
				html = m.group(1)
				result = word + ":"
				m = self.rSpell.search(html)
				if m:
					spell = m.group(1)
					for k in self.cmap:
						spell = spell.replace(k, self.cmap[k])
					result += " /" + spell + "/"
				m = self.rExpl.search(html)
				if m:
					html = m.group(1)
					html = self.rStrip.sub(" ", html)
					result += " "
					result += html
				return result
				
			return ""

	def lookup_yahoo(self, word):
		connect = httplib.HTTPConnection('cn.yahoo.com', 80)
		connect.request("GET", "/dictionary/result/%s/%s.html" % (word[0], word))
		response = connect.getresponse()
		if response.status != 200:
			msg = "%d:%s" % (response.status, response.reason)
			loc = response.getheader("location")
			if re.compile("/error").match(loc):
				return ""
			else:
				self.debug("dict word(%s) err(%s) loc(%s)" % (word, msg, loc))
		else:
			import re
			# Do the parsing here
			listing = response.read()
			listing = listing.split("\n")
			ibody = 0
			str = word + " "
			for item in listing:
				if self.rWord.match(item):
					for m in self.rGif.finditer(item):
						m = m.group(1)
						if self.ymap.has_key(m):
							m = self.ymap[m]
						str += m
				elif self.rBody.match(item):
					str += self.rStrip.sub("", item) + " "
					ibody += 1
			return str

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
				self.debug('response from zipinfo' + str(status), reason)
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
			
			self.debug(pos1, pos2, data[pos1:pos2])
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
		# the languages babelfish can do

		self.languages = {"english" : "en",
				  "chinese" : "zh",
				  "schinese" : "zh",
				  "tchinese" : "zt",
				  "dutch": "nl",
				  "french" : "fr",
				  "german" : "de",
				  "italian" : "it",
				  "japanese" : "ja",
				  "korean" : "ko",
				  "portuguese" : "pt",
				  "russian" : "ru",
				  "spanish" : "es",
				  "greek": "el"}

		# the combinations (from_to) that babelfish can
		self.translations =["zh_en", "zt_en", "en_zh",
		"en_zt", "en_nl", "en_fr", "en_de", "en_el", "en_it",
		"en_ja", "en_ko", "en_pt", "en_ru", "en_es", "nl_en",
		"nl_fr", "fr_en", "fr_de", "fr_el", "fr_it", "fr_pt",
		"fr_nl", "fr_es", "de_en", "de_fr", "el_en", "el_fr",
		"it_en", "it_fr", "ja_en", "ko_en", "pt_en", "pt_fr",
		"ru_en", "es_en", "es_fr"]
		self.shortcuts = {
			"ec": "en_zh",
			"ce": "zh_en"
			}

		self.regex = "^((babelfish|translate) \w+ to \w+|(%s)\s+.+|babelfish$|translate$)" % ("|".join(self.translations + self.shortcuts.keys()))


	def help(self, args):
		from irclib import Event
		langs = " ".join(self.languages.keys())
		trans = " ".join(self.languages.values())
 		return Event("privmsg", "", self.return_to_sender(args), [
			"Usage: translate <FROM_LANGUAGE> to <TO_LANGUAGE> TEXT\r\nAvailable LANGUAGES are \"%s\"" % (langs)
			+ "\r\nSynonyms: {LN_LN} TEXT\r\nWhere LNs are \"%s\"" % (trans)
			])

	def handler(self, **args):
		from irclib import Event
		import string, re, urllib
		
		tmp = args["text"].split(" ", 2)
		translation_key = tmp[1].lower()
		if len(tmp) != 3:
			return self.help(args)
		request = tmp[2] # chop off the "moobot: babelfish"

		if self.shortcuts.has_key(translation_key):
			translation_key = self.shortcuts[translation_key]
			translation_text = request
		elif translation_key in self.translations:
			translation_text = request
		else:
			froml = request.split()[0].lower() # the source language
							# to get something like "english to spanish foo"
			tol = request.split()[2].lower() # the destination language
			translation_text = " ".join(request.split()[3:]) 
			# The string to translate, it's length wont't be ZERO
			if re.compile("^\s*$").match(translation_text):
				return self.help(args)

			# check if we know the languages they want to use
			if froml not in self.languages.keys() :
				return Event("privmsg", "", self.return_to_sender(args), 
					[ "unknown language: " + froml ])
			if tol not in self.languages.keys():
				return Event("privmsg", "", self.return_to_sender(args), 
					[ "unknown language: " + tol ])

			# the value for the lp= field for the cgi arguments
			translation_key = "%s_%s" % (self.languages[froml], 
				self.languages[tol])

			# make sure the translation_key is one we can use
			if translation_key not in self.translations:
				return Event("privmsg", "", self.return_to_sender(args), 
					[ "Babelfish doesn't know how to do %s to %s" % 
					(froml, tol)])

		translation_text = translation_text.replace("'", "’".decode("gbk"));

		# create the POST body
		params = {"doit": "done", "intl": "1", "tt": "urltext", "trtext": translation_text.encode("UTF-8"), "lp": translation_key}

		headers = {"Content-type": "application/x-www-form-urlencoded",
				"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0)",
				"Accept-Encoding": ""}
		# connect, make the reauest
		connect = httplib.HTTPConnection('babelfish.altavista.com', 80)
		connect.request("POST", "/tr", urllib.urlencode(params), headers)
		response = connect.getresponse()
		if response.status != 200: # check for errors
			msg = response.status + ": " + response.reason

			return Event("privmsg", "", self.return_to_sender(args), [msg])
		else:
			listing = response.read().decode("UTF-8", "ignore")
			listing = listing.replace('\n', '') # get rid of newlines

		searchRegex2 = re.compile("<td bgcolor=white class=s><div style=padding:10px;>(.*?)</div></td>")

		match = searchRegex2.search(listing)

		result = match.group(1)

		return Event("privmsg", "", self.return_to_sender(args), 
			[ "Translation: " + result ])

