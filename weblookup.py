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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

import httplib
from moobot_module import MooBotModule
handler_list = ["deblookup", "cfactive", "horoscope", "debianize", "slashdot",
"google", "kernelStatus", "insult", "dict", "zipcode", "acronym", "gkstats",
"foldoc", "pgpkey", "geekquote", "weather"]
#, "babelfish"]

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
			msg = "%d: %s" % (response.status, response.reason)
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
		from irclib import Event
		import string
		self.return_to_sender(args)

		search_terms = args["text"].split(" ")[3:]
		search_request = "/ie?q="   # using ie instead of search makes
									# the resulting output so much nicer
		search_request += string.join(search_terms, "+")
		connect = httplib.HTTPConnection('www.google.com', 80)
		connect.request("GET", search_request)
		response = connect.getresponse()
		if response.status != 200:
			msg = str(response.status) + ": " + response.reason
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
		import string
		connect=httplib.HTTPConnection("www.kernel.org", 80)
		connect.request('GET', '/kdist/finger_banner')
		response = connect.getresponse()
		if response.status != 200:
			msg = '%d: %s' % (response.status, response.reason)
			print msg
			return Event("privmsg", "", target, [msg])
		text = response.read()

		# Extract just the version numbers, instead of flooding
		# the channel with everything.
		result = ""
		for line in text.split("\n"):
			if len(line.split(":")) > 1:
				line = line.split(" ", 2)[2]
				version = '%s ;; ' % line.split(":")[1].strip()
				line = line.split("of", 2)[0]
				line = line.split("for", 2)[0]
				line = line.split("to", 2)[0]
				result += '%s: %s' % (line.strip(), version)

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
		#   text = text + i
		#   i=connection.read_some()
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
		#   text = text + i
		#   i = connection.read_some()
		connection.close()
		text = text.split("\n")
		from string import join
		msg = join(text[3:-1])  # The first three lines and the last are unneeded

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
		self.regex="^zipcode .*"

	def handler(self, **args):
		"""A dummy handler we used for testing -- this is the first handler
		we wrote"""
		from irclib import Event

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
				print 'response from zipinfo' + str(response.status)
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
					int(zipcode)
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
				message += '; area code: ' + data[pos1+len(TDTAG):pos2]

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
	# the languages babelfish can do
	languages = { "english" : "en", "chinese" : "zh",
				"french" : "fr", "german" : "de",
				"italian" : "it", "japanese" : "ja",
				"korean" : "ko", "portuguese" : "pt",
				"russian" : "ru", "spanish" : "es"}

	# the combinations (from_to) that babelfish can translate
	translations =[ "en_zh", "en_fr", "en_de" , "en_it",
		"en_ja", "en_ko" , "en_pt", "en_es" , "zh_en",
		"fr_en" , "fr_de", "de_en", "de_fr" , "it_en",
		"ja_en", "ko_en", "pt_en", "ru_en", "es_en"]

	def __init__(self):
		self.regex = "^(babelfish|translate) \w+ to \w+ .+"

	def handler(self, **args):
		from irclib import Event
		import string, re
		target = self.return_to_sender(args)

		request = args["text"].split(" ", 2)[2] # chop off "moobot: babelfish"
		from_language = request.split()[0] # the source language
		to_language = request.split()[2] # the destination language
		translation_text = string.join(request.split()[3:], "+") # the string to translate
						# we also switch whitespace for +s here,
						# to work in the HTTP request

		# check if we know the languages they want to use
		if from_language.lower() not in babelfish.languages.keys() :
			return Event("privmsg", "", self.return_to_sender(args),
				[ "unknown language: " + from_language ])
		if to_language.lower() not in babelfish.languages.keys():
			return Event("privmsg", "", self.return_to_sender(args),
				[ "unknown language: " + to_language ])

		# the value for the lp= field for the cgi arguments
		translation_key = "%s_%s" % (babelfish.languages[from_language.lower()],
			babelfish.languages[to_language.lower()])

		# make sure the translation_key is one we can use
		if translation_key not in babelfish.translations:
			return Event("privmsg", "", self.return_to_sender(args),
				[ "Babelfish doesn't know how to do %s to %s" %
				(from_language, to_language)])

		search_request = "/tr?doit=done&tt=urltext&intl=1&urltext=%s&lp=%s" % \
			(translation_text, translation_key) # create the HTTP request

		# connect, make the reauest
		connect = httplib.HTTPConnection('babelfish.altavista.com', 80)
		# blah, have to set the 'referer'
		connect.putrequest("GET", search_request)
		connect.putheader("Http-Referer", "http://babelfish.altavista.com/tr")
		connect.endheaders()
		connect.send("")

		response = connect.getresponse()
		if response.status != 200: # check for errors
			msg = str(response.status) + ": " + response.reason
			print msg
			return Event("privmsg", "", target, [msg])
		else:
			listing = response.read() # grab the html source
		match = \
			re.search("<input.*?name=\"q\"\s+value=\"?(?P<trans>.*?)\"?.*?>",
			listing, re.DOTALL | re.I)
		match2 = \
			re.search("<td\s+bgcolor=white.*?><div.*?>(?P<trans>.*?)</div>",
			listing, re.DOTALL | re.I)
		match3 = \
			re.search("<td.*?class=s><div.*?>(?P<trans>.*?)\s*</div>",
			listing, re.DOTALL | re.I)
		if match is None and match2 is None and match3 is None:
			msg = "Failed translation."
			return Event("privmsg", "", target, [msg])

		# if the first doesn't match, check the second (stupid babelfish is
		# inconsistent on how they return the results, grrr)
		if match is None: match = match2
		if match is None: match = match3

		result = match.group('trans')

		return Event("privmsg", "", self.return_to_sender(args),
			[ "Translation: " + result ])

class debianize(MooBotModule):
	""" looks up the debian package name for any string, using
	http://www.pigdog.org/cgi_bin/dpn.html"""
	def __init__(self):
		self.regex = "^debianize .+"

	def handler(self, **args):
		from irclib import Event
		import string, re
		target = self.return_to_sender(args)

		search_terms = args["text"].split(" ")[2:]# everything after the first word
		search_request = "/cgi_bin/dpn.phtml?name=" # the script on the remote server
		search_request += string.join(search_terms, "+")
		connect = httplib.HTTPConnection('www.pigdog.org', 80)
		connect.request("GET", search_request)
		response = connect.getresponse()
		if response.status != 200:
			msg = str(response.status) + ": " + response.reason
			print msg
			return Event("privmsg", "", target, [msg])
		else:
			listing = response.read()
			listing = string.replace(listing, '\n', '') # get rid of newlines

		searchRegex = re.compile('<p><b><font size="\+2">[^<]+</font></b>.</p>') #find the package name
		if searchRegex.search(listing) != None:
			match = searchRegex.search(listing)
			result = match.group() #get the whole textarea node
			result = string.replace(result, "</font></b>.</p>", "")#chop off the closing tags
			result = result[result.rfind(">")+1:] # chop off everything up to the last >
			return Event("privmsg", "", target, [ "Your debian package name is: " + result])
		else:
			print listing
			return Event("privmsg", "", target, [ "Sorry, I couldn't find the package name."])


class horoscope(MooBotModule):
	""" gets a horoscope from TheOnion.com
	Author: kmj
	Updates by: Scrapz, jamessan """
	def __init__(self):
		self.regex = "^horoscope .+"

	def handler(self, **args):
		import re, string
		from irclib import Event

		sign = args["text"].split(" ")[2]

		# first, go to the onion mainpage, so we can find the volume
		# and issue number, so we know where to find the current horoscope
		#
		conn = httplib.HTTPConnection('www.theonion.com',80)
		conn.request('GET','/redirect.php')
		response = conn.getresponse()
		if response.status != 302:
			msg = "Bad response from the onion: " + str(response.status)
			return Event("privmsg", "", self.return_to_sender(args), [msg])
		url = response.msg.headers[3].split()[1]

		# find the volume and issue
		match = re.search('.*?/onion(\d{4})/.*', url)
		try:
			volume = match.group(1)
		except AttributeError:
			return "Could not parse out the volume number from: " + url

		# Now make the connection with theonion's horoscope page
		conn = httplib.HTTPConnection('www.theonion.com')
		conn.request('GET',
					 '/onion' + volume + '/horoscopes_' + volume + '.html')
		response = conn.getresponse()
		if response.status != 200:
			msg = "bad response getting horoscopes:", str(response.status)

		#parse out the info for the given sign
		data = response.read()
		data = re.sub('<.*?>', '', data)

		match = re.search(sign, data, re.IGNORECASE)
		if match is None:
			msg = "sorry, couldn't find: " + sign
			return Event("privmsg", "", self.return_to_sender(args), [msg])

		start = match.start()
		end = string.find(data, '\n', match.start())
		if end == -1:
			msg = "aw, crap!"
			return Event("privmsg", "", self.return_to_sender(args), [msg])

		msg = data[start:end]
		msg = re.sub('&#151;',' - ',msg)
		return Event("privmsg", "", self.return_to_sender(args), [msg])

class cfactive(MooBotModule):
	""" returns a list of currently active users at coderforums.net """

	def __init__(self):
		self.regex = "^cfactive$"

	def handler(self, **args):
		import re
		from irclib import Event

		conn = httplib.HTTPConnection('www.coderforums.net')
		conn.request('GET', "")

		response = conn.getresponse()
		if response.status != 200:
			msg = "bad response from coderforums: " + str(response.status)
			return Event("privmsg", "", self.return_to_sender(args), [msg])

		data = response.read()
		match = re.search('ever online was .*\n(?P<list>.*?)\n', data)
		data = re.sub('<.*?>', '', match.group('list').strip())
		if match is None:
			msg =  "data not found; gosh that sucks"
			return Event("privmsg", "", self.return_to_sender(args), [msg])

		return Event("privmsg", "", self.return_to_sender(args), [data])


class deblookup(MooBotModule):
	max_packages = 10
	def __init__(self):
		self.regex="^deblookup .+"

	def handler(self, **args):
		import re
		import httplib
		from irclib import Event

		target = self.return_to_sender(args)

		## Parse the request
		# A branch can be specified as the first argument, and multiple
		# packages can be requested.
		branches = ['stable', 'testing', 'unstable']

		request = args["text"].split()[2:]
		if request[0] in branches:
			branch = request[0]
			del request[0]
		else:
			branch = None

		# Now, they may have forgotten to specify a package if they provided a
		# branch (the regex will still match)
		if len(request) == 0:
			msg = "You must specify a package name."
			return Event("privmsg", "", target, [msg])

		# Otherwise, request should now contain a list of packages
		# We'll step through them one by one and display them all at once at
		# the end.
		host = "packages.debian.org"
		page = "/cgi-bin/search_packages.pl"

		msg = ""
		for package in request:
			# build the request
			cgi_params = \
				"?keywords=%s&searchon=names&version=%s&release=all" % (
					package, branch or "all")
			conn = httplib.HTTPConnection(host)
			print page + cgi_params
			conn.request("GET", page + cgi_params)

			response = conn.getresponse()
			if response.status != 200:
				msg = "Bad response from packages.debian.org: %d" % \
					response.status
				return Event("privmsg", "", target, [msg])
			else:
				data = response.read()
				# Drop everything but the table
				match = re.search('<TABLE .*?>.*?</TABLE>', \
					data, re.DOTALL | re.I)
				if match is None:
					msg += "no package found for: %s (%s) ;; " % (
						package, branch or "all")
				else:
					table_data = match.group()
					## Now run through each row of the table and build the msg
					rows = table_data.split("</TR>")

					# Check for greater than max_packages (note that the first
					# and last row don't have pkgs)
					num_pkgs_match = re.search('out of total of (?P<num>\d+)', \
						data, re.DOTALL | re.I)
					num_pkgs = int(num_pkgs_match.group('num'))

					if num_pkgs > deblookup.max_packages:
						msg += "%d packages found, displaying %d: " % (
							num_pkgs, deblookup.max_packages)
						last_row = deblookup.max_packages
					else:
						last_row = -1

					for row in rows[1:last_row]:
						pkg_match = re.search("<a.*>(?P<pkg_ver>.*?)</a>", \
							row, re.DOTALL | re.I)
						br_match = re.search(
							"<td ALIGN=\"center\">(?P<pkg_br>.*?)</?td>", \
							row, re.DOTALL | re.I)
						msg += "%s (%s) ;; " % (
							pkg_match.group('pkg_ver').strip(),
							br_match.group('pkg_br').strip())

		return Event("privmsg", "", target, [msg])

class acronym(MooBotModule):
	"""Does a search on www.acronymfinder.com and returns all definitions"""
	def __init__(self):
		self.regex = "^explain [A-Z]+"

	def handler(self, **args):
		from irclib import Event
		import string, re
		target = self.return_to_sender(args)

		search_term = args["text"].split(" ")[2]
		search_request = "/af-query.asp?String=exact&Acronym=%s" % search_term
		connect = httplib.HTTPConnection('www.acronymfinder.com', 80)
		connect.request("GET", search_request)
		response = connect.getresponse()
		if response.status != 200:
			msg = "%d: %s" % (response.status,response.reason)
			print msg
			return Event("privmsg", "", target, [msg])
		else:
			listing = response.read()


		search = re.compile("<td[^>]*><b>%s\s+</b></td>[^<]+<td[^>]*>([A-Za-z][^<\n\r]+)\s*</td>" % search_term)
		definitions = search.findall(listing)
		if len(definitions) == 0:
			line = "Could not find a definition for " + search_term
		elif len(definitions) == 1:
			line = search_term + " is " + definitions[0]
		else:
			line = search_term + " is one of the following: \"" + string.join(definitions,'", "') + "\""
		return Event("privmsg", "", self.return_to_sender(args), [ line ])

class gkstats(MooBotModule):
	""" Returns user stats from gameknot.com
	Author: inkedmn
	Updates by: jamessan """
	def __init__(self):
		self.regex = "^gkstats .+"

	def handler(self, **args):
		from irclib import Event
		target = self.return_to_sender(args)

		import urllib2
		import re
		# grab the user
		user = args["text"].split()[2]
		gkurl = "http://www.gameknot.com/stats.pl?%s" % user
		try:
			html = urllib2.urlopen(gkurl).read()
		except urllib2.URLError:
			return "error connecting to gameknot.com"
		rating = re.search('.*<font color="#FFFF33">(\d+)</font>.*', html)
		games = re.search('s:&nbsp;&nbsp;</td><td class=sml>(\d+)</td></tr>', html)
		record = re.search('FFFF00">(\d+)</f.*?FF00">(\d+)</f.*?FF00">(\d+)</f.*?',html)

		try:
			result = "%s is rated %d and has %d active games; W-%d L-%d D-%d." % \
						(user, int(rating.group(1)), int(games.group(1)),\
						 int(record.group(1)), int(record.group(2)),\
						 int(record.group(3)))
		except AttributeError:
			result = "could not find gameknot stats for %s" % user
		except UnboundLocalError:
			result = "could not find gameknot stats for %s" % user

		return Event("privmsg", "", target, [result])

class foldoc(MooBotModule):
	def __init__(self):
		self.regex = "^foldoc .+"

	# Returns the position of the nth element in lst.
	def index(self, lst, element, n=1):
		m = 0
		for i in xrange(len(lst)):
			if lst[i] == element:
				m += 1
				if m == n:
					return i

	def handler(self, **args):
		from irclib import Event
		import urllib2
		import re
		target = self.return_to_sender(args)

		try:
			url = "http://foldoc.doc.ic.ac.uk/foldoc/foldoc.cgi?query=" + args["text"].split()[2]
		except urllib2.URLError:
			return "error connecting to foldoc"
		fd = urllib2.urlopen(url).readlines()
		start = self.index(fd, "<P>\n", 1)
		stop = self.index(fd, "<P>\n", 2)
		descr = " ".join(fd[start:stop])   # Get the base description
		descr = re.sub("\n", "", descr)	# Remove newlines
		descr = re.sub("<.*?>", "", descr) # Remove HTML tags
		descr = re.sub("&.*;", "", descr)  #   "	 "	"
		descr = descr.lstrip() # Remove leading white spaces

		return Event("privmsg", "", target, [descr])

class pgpkey(MooBotModule):
	""" Does a key search on pgp.mit.edu and returns the first 5 hits
	Author: jamessan """
	def __init__(self):
		self.regex = "^pgpkey .+$"

	def handler(self, **args):
		from irclib import Event
		import string
		self.return_to_sender(args)

		import re
		search_terms = args["text"].split(" ")[2:]
		domain = "pgp.mit.edu"
		port=11371
		search_request = "/pks/lookup?op=index&search="
		search_request += string.join(search_terms, "+")
		connect = httplib.HTTPConnection(domain, port)
		connect.request("GET", search_request)
		response = connect.getresponse()
		if response.status != 200:
			msg = str(response.status) + ": " + response.reason
			print msg
			return Event("privmsg", "", target, [msg])
		else:
			listing = response.read()
		url="http://" + domain + ':' + `port`
		pgpkeys={}
		pgp = re.compile('pub\s+\d{4}\w/<a'\
			' href="([^"]+)">([^<]+)</a>[^>]+>([^<]+)</a>')
		for i in listing.split('\n'):
			info = pgp.search(i)
			try:
				path, keyid, email = info.groups()
				pgpkeys[keyid]=(email,'%s%s' % (url,path))
			except AttributeError:
				pass
		line = "pgpkey matches for \"" + string.join(search_terms) + "\": "
		count=0
		if len(pgpkeys.keys()) == 0:
			return Event("privmsg", "", self.return_to_sender(args), [ '%s'\
				' 0 matches found' % line ])
		for i in pgpkeys.keys():
			count += 1
			if count <= 5:
				line += pgpkeys[i][0] + " (" + pgpkeys[i][1] + ") :: "
		return Event("privmsg", "", self.return_to_sender(args), [ line[:-4] ])

class geekquote(MooBotModule):
	""" Grabs a one-liner from bash.org
	Author: jamessan """
	def __init__(self):
		self.regex = "^geekquote.*$"

	def handler(self, **args):
		from irclib import Event
		target = self.return_to_sender(args)

		import urllib2
		import re

		quoteurl = "http://bash.org/?random1"
		try:
			html = urllib2.urlopen(quoteurl).read()
		except urllib2.URLError:
			return "error connecting to bash.org"
		# Grab a one-line quote unless they specify multiline
		if args["text"].find("multiline") == -1:
			quote_text=re.search('<p class="qt">(.*?)</p>',html)
		else:
			quote_text=re.search('<p class="qt">(.*?)</p>',html,re.DOTALL)
		try:
			quote=quote_text.group(1)
		except AttributeError:
			return "No quote found"

		# This replaces various bits of html chars. If someone wants to replace
		# it with HTMLParser stuff, feel free
		quote=re.sub('&lt;','<',quote)
		quote=re.sub('&gt;','>',quote)
		quote=re.sub('&nbsp;',' ',quote)
		quote=re.sub('&quot;','"',quote)
		quote=re.sub('<br />','',quote)

		return Event("privmsg", "", target, [quote])

class weather(MooBotModule):
	""" Grabs the current weather conditions from www.srh.noaa.gov
	Author: jamessan """
	def __init__(self):
		self.regex = "^weather (\d{5}|\w+\s?\w+)$"

	def handler(self, **args):
		from irclib import Event
		import string
		self.return_to_sender(args)

		import re
		search_terms = args["text"].split(" ")[2:]
		domain = "www.srh.noaa.gov"
		search_request = "/zipcity.php?inputstring="
		search_request += string.join(search_terms,"")
		connect = httplib.HTTPConnection(domain, 80)
		connect.request("GET", search_request)
		response = connect.getresponse()
		if response.status != 302:
			msg = str(response.status) + ": " + response.reason
			print msg
			return Event("privmsg", "", target, [msg])
		else:
			pass
		search_request = response.msg.headers[4].split(" ")[1][23:-2]
		connect = httplib.HTTPConnection(domain, 80)
		connect.request("GET", search_request)
		response = connect.getresponse()
		if response.status != 200:
			msg = str(response.status) + ": " + response.reason
			return Event("privmsg", "", target, [msg])
		else:
			html = response.read()
		if html.find('Could not find your zip') > -1:
			return "Could not find given zip code"
		elif html.find('Could not find') > -1:
			return "Could not find weather info"
		else:
			pass

		update = re.search('Last Update on (.*?)<br>',html)
		try:
			update = update.group(1)
		except AttributeError:
			return "Problems finding latest udpate info"

		weather = re.search('<td class="big" width="120" align="center">'\
			'(\w+)?<br><br>(.*?)</td>',html)
		try:
			weather = [weather.group(1),weather.group(2)]
			weather[1] = re.sub('&deg;','',weather[1])
			weather[1] = re.sub('<br>',' ',weather[1])
		except AttributeError:
			return "Problems finding weather info"

		humidity = re.search('Humidity.*?"right">(.*? %)',html,re.DOTALL)
		try:
			humidity = humidity.group(1)
			humidity = re.sub(' ','',humidity)
		except AttributeError:
			return "Problem finding humidity info"

		wind = re.search('Wind Speed.*?"right">(.*?)</td>.*Wind'
			'Chill.*?"right">(.*?)</td>',html,re.DOTALL)
		try:
			wind = [wind.group(1),wind.group(2)]
			wind[1] = re.sub('&deg;','',wind[1])
		except AttributeError:
			return "Problem finding wind info"

		line = "weather info for \"%s\" as of %s: %s %s, %s humidity, %s"\
			"wind, %s wind chill" %(search_terms, update, weather[0],
			weather[1], humidity, wind[0], wind[1])
		return Event("privmsg", "", self.return_to_sender(args), [ line ])

# vim:ts=4:sw=4:tw=78:
