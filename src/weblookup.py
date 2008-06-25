#!/usr/bin/env python
# -*- coding:gb2312 -*-

# Copyright (C) 2005, 2006, 2007 by FKtPp, moo
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

import re, httplib, urllib, urllib2, HTMLParser, weather
from moobot_module import MooBotModule
from irclib import Event, IrcStringIO

handler_list = ["weathercn", "google", "kernelStatus", "dict", "acronym",
		"babelfish", "debpackage", "debfile", "genpackage", "foldoc", "pgpkey",
		"geekquote", "lunarCal", "ohloh"]

# Without this, the HTMLParser won't accept Chinese attribute values
HTMLParser.attrfind=re.compile(
               r'\s*([a-zA-Z_][-.:a-zA-Z_0-9]*)(\s*=\s*'
               r'(\'[^\']*\'|"[^"]*"|[^ <>]*))?')

class IEURLopener(urllib.FancyURLopener):
	version = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"

urllib._urlopener = IEURLopener()

class weathercn(MooBotModule):
	"""weather module to get weather forecast infomation
	
	This module depends on weather.py, it use weather.py to
	parse the html page of weathercn.com. Note, we must ignore
	the HTMLParser.HTMLParseError because of the malformed
	html pages.
	"""
	def __init__(self):
		"""
		>>> import re
		>>> from weblookup import weathercn
		>>> a = weathercn()
		>>> r = re.compile(a.regex)
		>>> r.match("w") and True or False
		True
		>>> r.match("weather") and True or False
		True
		>>> r.match("w 0335") and True or False
		True
		>>> r.match("weather 0335") and True or False
		True
		>>> r.match("wo03335") and True or False
		False
		>>> r.match("w 10086") and True or False
		True
		>>> r.match(u"w 通化") and True or False
		True
		>>> r.match(u"weather 通辽") and True or False
		True
		>>> r.match(u"w 北京") and True or False
		True
		>>> r.match(u"w 通化 8") and True or False
		True
		>>> r.match(u"weather 通辽 9") and True or False
		True
		>>> r.match(u"w 北京 37") and True or False
		True
		>>> r.match("who") and True or False
		False
		"""
		self.regex = "^(weather|w)($|( [^ ]+){1,2})"

	def handler(self, **args):
		"""Parse the received commandline arguments
		
		case length of the real arguments:
		
		zero, check database to see if the user already
		      have a record. y: use it to get the forcast
		      and setting change tips; n: print help 
		      message.
		   1, get and print the citylist.
		   2, get the citylist, and then get the forecast
		      accroding the second argument. print the
		      result, save settings to database.

		and any any any better throughts ;) --save to control
		database operation?
		"""
 
		# TODO: ... save settings to database
		# TODO: ... get settings from database

		self.result = {'notice': '',
			       'msg': ''}

		tmp_args_list = args["text"].strip().split(" ")
		del(tmp_args_list[0])

		lenlist = len(tmp_args_list)
		
		if lenlist in (2, 3):
			len1 = len(tmp_args_list[1])
				
			if lenlist == 3\
					and not tmp_args_list[2].isdigit():
				self.result['notice'] = u"区域索引”n“必须是数字，"\
					u"请重新输入"
			
			elif len1 < 2:
				self.result['notice'] = u"“城市名称”不可少于两个字符，"\
				u"请重新输入"
			elif tmp_args_list[1].isdigit():
				if len1 not in (3, 4, 6) or tmp_args_list[1][:2] == '00':
					self.result['notice'] = u"非法的区号或邮政编码，"\
							u"请重新输入"
				elif len1 == 6 and tmp_args_list[1][3:] != '000':
					self.result['notice'] = u"请使用市级以上邮政编码，"\
							u"TIP：将您的邮编后三位改为“000”"
				elif len1 in (3, 4) \
						and tmp_args_list[1][0] != '0':
					self.result['notice'] = u"非法的电话区号, "\
							u"请重新输入"
				else: 
					self.gogetit(tmp_args_list)
					
			elif tmp_args_list[1].isalpha() and len1 > 4:
				self.result['notice'] = u"请给我一个“城市名或拼音缩写”多于"\
				u" 4 个字符的理由"
			else:
				self.gogetit(tmp_args_list)
				
		else:
			self.result['notice'] = self._help()
		
# 		print self.result['notice'].encode('utf8')
# 		print self.result['msg'].encode('utf8')

		if self.result['notice'] and not self.result['msg']:
			target = self.return_to_sender(args, 'nick')
			return Event("notice", "", target, [self.result['notice']])

		if self.result['msg']:
			target = self.return_to_sender(args)
			return Event("privmsg", "", target, [self.result['msg']])

	def gogetit(self, l):
		"""get back the citylist or recursively invoke getforecast
		
		get the citylist, setup notice message it if there is
		no 3rd arg.  check length against the 3rd arg, invoke
		getforcast if valid.
		""" 
		
		citykeyword = l[1].lower()
		search_parm = urllib.urlencode({"searchname": citykeyword.encode("gbk")})
		print search_parm
		try:
			response = urllib.urlopen("http://www.weathercn.com/search/search.jsp",
									  search_parm)
		except IOError, e:
			print e
		
		rp = weather.WeatherCNCITYParser()
		try:
			rp.feed(response.read().decode("gbk"))
			print response.read()
		except HTMLParser.HTMLParseError:
			pass
		
		response.close()
		
		regionlist = rp.o()
		
		if len(l) < 3:
			if len(regionlist) == 1:
				c, u = regionlist[0]
				self.getforcast(u)
			else:
				i = 1
				result = IrcStringIO('%s: ' % citykeyword, 200)
				for c, u in regionlist:
					result.write("".join(("=", str(i),"=>", c)))
					i += 1
				self.result['notice'] = result.getvalue()

		elif len(regionlist) < int(l[2]):
			self.result['notice'] = u"地区索引”n”大于地区总个数"
		else:
			c, u = regionlist[int(l[2])-1]
			self.getforcast(u)

	def getforcast(self, url):
		"""Get the weather forcast from the given url
		
		get and then parse the weather forcast, setup the
		result message
		"""
		try:
			response = urllib.urlopen("http://www.weathercn.com%s" % url)
		except IOError, e:
			print e
		
		fp = weather.WeatherCNParser()
		
		try:
			fp.feed(response.read().decode("gbk"))
		except HTMLParser.HTMLParseError:
			pass
		
		response.close()
		
		self.result['msg'] = " ".join(fp.o())

	def _help(self, a="help"):
		"""return help messages
		"""
		myhelpmsg = u"BadGirl 天气预报员模块！使用 <weather 你的城市> 获\
取详细城市列表，使用 <weather 你的城市 n> 获取对应城市的天气信息。“你的\
城市”可以是“城市的中文名，城市拼音缩写，城市的邮政编码，城市的长途区号”；地区索引“n”是\
<weather 你的城市> 返回的地区列表中区域对应的数字。"
		mytipmsg = u"您可以重新执行 <weather 您想要查看的城市> 和\
 <weather 您想要查看的城市 n> 来修改自己的首选城市。"
		if a == "help":
			msg = myhelpmsg
		else:
			msg = mytipmsg

		return msg

class google(MooBotModule):
	"Does a search on google and returns the first 5 hits"
	def __init__(self):
		self.regex = "^google for .+"

	def handler(self, **args):
		self.return_to_sender(args)

		search_terms = args["text"].split(" ")[3:]
		search_request = "/ie?hl=zh-CN&oe=UTF-8&ie=UTF-8&q="
		# the resulting output so much nicer
		search_request += '+'.join(search_terms).encode("UTF-8", 'replace')
		connect = httplib.HTTPConnection('www.google.com', 80)
		headers = {"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0)"}
		connect.request("GET", search_request, None, headers)

		try:
			response = connect.getresponse()
		except:
			msg = "error"
			return Event("privmsg", "", target, [msg])

		if response.status != 200:
			msg = str(response.status) + ": " + response.reason
			self.debug(msg)
			return Event("privmsg", "", target, [msg])
		else:
			listing = response.read().decode("UTF-8", 'replace')
		urls=[]
		for i in listing.split():
			if i.find("href=http://") >= 0:
				url = i[:i.find(">")]
				url = url[5:]
				urls.append(url)
		line = "Google says \"" + ' '.join(search_terms) + "\" is at: "
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
		"""
		gets kernel status
		"""
		# self.debug("kernelStatus")
		connect=httplib.HTTPConnection("www.kernel.org", 80)
		connect.request('GET', '/kdist/finger_banner')
		response = connect.getresponse()
		if response.status != 200:
			msg = '%d: %s' % (response.status, response.reason)
			self.debug(msg)
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

		
		target = self.return_to_sender(args)
		return Event("privmsg", "", target, [ result ])


class dict(MooBotModule):
	cache = {}
	cache_old = {}
	def __init__(self):
		
		# have problem filtering out `|' character
		self.regex = "^(dict |~)[^~\+\*/\\<>-]+"
		self.rStrip = re.compile("(<.*?>)+")
		self.rWord = re.compile("^<!-- WORD", re.I)
		self.rGif = re.compile("/gif/([\\w_]+)\\.gif", re.I)
		self.rBody = re.compile("^<!-- BODY", re.I)
		self.ymap = {"slash": "/", "quote": "'", "_e_": "2", "_a": "a:", "int": "S"}
		self.cmap = {"\\\\": "\\", "5": "'", "E": "2"}
		self.rNx = re.compile(u"找不到和您查询的")
		self.rCtoE = re.compile(u"简明汉英词典")
		self.rRwWord = re.compile('rwWord\("([^"]+)"\)')

		self.rEtoC = re.compile(u"简明英汉词典")
		self.rExplain = re.compile('explain_item">(.*?)</div>', re.S)
		self.rSpell = re.compile("str2img\('([^']+)", re.I)
		self.ciba_failed = 1
		self.rSearch = re.compile(u'^[^*?_%]{2,}[*?_%]')

	def handler(self, **args):
		import dict
		target = self.return_to_sender(args)
		if args["text"].split()[1][0][0] == '~':
			word = " ".join(args["text"].split()[1:])[1:]
		else:
			word = " ".join(args["text"].split()[2:])

		# simple yet powerful garbage collection
		# better not use time
		if len(self.cache) > 500:
			self.cache_old = self.cache
			self.cache = {}

		if self.rSearch.match(word):
			words = dict.search(word)
			self.Debug(words)
			if not words:
				result = False
			elif len(words) == 1:
				result = words[0] + ', ' + dict.lookup(words[0])
			else:
				result = "Found %d" % len(words)
				if len(words) >= dict.maxsearch:
					result += " or more"
				result += ": " + ", ".join(words)

			if not result:
				result = "not found"
		else:
			result = dict.lookup(word)

		if result:
			result = word + ": " + result
		elif self.cache.has_key(word):
			result = self.cache[word]
		elif self.cache_old.has_key(word):
			self.cache[word] = self.cache_old[word]
			result = self.cache[word]
		else:
			#if self.ciba_failed <= 0:
			#	result = self.lookup_ciba(word)
			#	if result == "error":
			#		self.ciba_failed = 5
			#		result = self.lookup_yahoo(word)
			#else:
			#	result = self.lookup_yahoo(word)
			#	self.ciba_failed = self.ciba_failed - 1
			result = self.lookup_ciba(word)
			result = result.replace("&lt;","<").replace("&gt;",">")
			if len(result) == 0:
				result = "Could not find definition for " + word
			elif result == "error":
				pass
			else:
				self.cache[word] = result

		return Event("privmsg", "", target, [ result ])

	def lookup_ciba(self, word):
		connect = httplib.HTTPConnection('www.iciba.com', 80)
		connect.request("GET", "/search?s=%s&t=word&lang=utf-8" % (word.encode("UTF-8"), ))
		response = connect.getresponse()
		if response.status != 200:
			msg = "%d:%s" % (response.status, response.reason)
			loc = response.getheader("location")
			self.Debug("dict word(%s) err(%s) loc(%s)" % (word, msg, loc))
			return "error"
		else:
			# Do the parsing here
			html = response.read().decode("UTF-8", "ignore")
			if self.rNx.search(html):
				return ""
	
			m = self.rCtoE.search(html)
			if m:
				m = self.rRwWord.findall(html)
				if m:
					result = word + ':'
					for i in m:
						result += ' ' + i
					return result

			m = self.rEtoC.search(html)
			if m:
				result = word + ":"

				m = self.rSpell.search(html)
				if m:
					spell = m.group(1)
					for k in self.cmap:
						spell = spell.replace(k, self.cmap[k])
					result += " /" + spell + "/"

				m = self.rExplain.search(html)
				if m:
					result += ' ' + m.group(1).strip()
				return result
				
			return ""

	def lookup_yahoo(self, word):
		connect = httplib.HTTPConnection('cn.yahoo.com', 80)
		w = word.encode("GBK") # better than error
		connect.request("GET", "/dictionary/result/%s/%s.html" % (w[0], w))
		response = connect.getresponse()
		if response.status != 200:
			msg = "%d:%s" % (response.status, response.reason)
			loc = response.getheader("location")

			self.Debug(loc)
			if loc and re.compile("/error").match(loc):
				return ""
			else:
				self.debug("dict word(%s) err(%s) loc(%s)" % (word, msg, loc))
				return ""
		else:
			# Do the parsing here
			listing = response.read().decode("GBK")
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



class babelfish(MooBotModule):
	"Does a search on babelfish.altavista.com and returns the translation"
	# the languages babelfish can do
	languages = {"english" : "en", "chinese" : "zh",
		     "french" : "fr", "german" : "de",
		     "italian" : "it", "japanese" : "ja",
		     "korean" : "ko", "portuguese" : "pt",
		     "russian" : "ru", "spanish" : "es"}
	# the combinations (from_to) that babelfish can translate
	translations =["en_zh", "en_fr", "en_de" , "en_it", "en_ja", "en_ko",
		       "en_pt", "en_es" , "zh_en", "fr_en" , "fr_de", "de_en",
		       "de_fr" , "it_en", "ja_en", "ko_en", "pt_en", "ru_en",
		       "es_en"]

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
		langs = " ".join(self.languages.keys())
		trans = " ".join(self.languages.values())
		return Event("privmsg", "", self.return_to_sender(args), [
			"Usage: translate <FROM_LANGUAGE> to <TO_LANGUAGE> TEXT\r\nAvailable LANGUAGES are \"%s\"" % (langs)
			+ "\r\nSynonyms: {LN_LN} TEXT\r\nWhere LNs are \"%s\"" % (trans)
			])

	def handler(self, **args):
		
		tmp = args["text"].split(" ", 2)
		translation_key = tmp[1].lower()
		if len(tmp) != 3:
			return self.help(args)
		request = tmp[2] # chop off the "moobot: babelfish"

		if self.shortcuts.has_key(translation_key):
			if request.find(' ') == -1 and re.compile('^[a-z]+$', re.I).search(request):
				return Event("privmsg", "", self.return_to_sender(args), 
					[ "use: dict " + request + " or ~~" + request])
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

		translation_text = translation_text.replace("'", u"’");

		# create the POST body
		params = {"doit": "done", "intl": "1", "tt": "urltext", "trtext": translation_text.encode("UTF-8"), "lp": translation_key}
		headers = {"Content-type": "application/x-www-form-urlencoded",
			   "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0)",
			   "Accept-Encoding": ""}
		# connect, make the reauest
		connect = httplib.HTTPConnection('babelfish.yahoo.com', 80)
		connect.request("POST", "/translate_txt", urllib.urlencode(params), headers)
		response = connect.getresponse()
		if response.status != 200: # check for errors
			msg = response.status + ": " + response.reason
			return Event("privmsg", "", self.return_to_sender(args), [msg])
		else:
			listing = response.read().decode("UTF-8", "ignore")
			listing = listing.replace('\n', '') # get rid of newlines
		searchRegex2 = re.compile('<div id="result"><div style="padding:0.6em;">(.*?)</div></div>')
		match = searchRegex2.search(listing)
		result = match.group(1)
		return Event("privmsg", "", self.return_to_sender(args), 
			[ "Translation: " + result ])

class debpackage(MooBotModule, HTMLParser.HTMLParser):
	"""
	Does a package search on http://packages.debian.org and returns top 10 result
	"""
	def __init__(self):
		self.regex="^debpackage .+"
		self.package = ""
		self.branch = ""
		HTMLParser.HTMLParser.__init__(self)

	def reset(self):
		HTMLParser.HTMLParser.reset(self)
		self.__max_hit = 10
		self.inner_div = False
		self.in_ul = False

		self.o = IrcStringIO("%s(%s):" % (self.package, self.branch))

		self.li = 0
		self.li_over = False
		self.after_br = False

	def handler(self, **args):

		target = self.return_to_sender(args)

		## Parse the request
		# A branch can be specified as the first argument, and multiple
		# packages can be requested.
		branches = ['oldstable',
			    'stable',
			    'testing',
			    'unstable',
			    'experimental',
			    'all']

		request = args["text"].split()[2:]
		if request[0] in branches:
			self.branch = request[0]
			del request[0]
		else:
			self.branch = 'testing'

		# Now, they may have forgotten to specify a package if
		# they provided a branch (the regex will still match)
		if len(request) != 1:
			msg = "Usage: debpackage [oldstable|stable|testing|unstable|experimental|all] PackageName"
			return Event("privmsg", "", target, [msg])
		else:
			self.package = request[0]

		# Otherwise, request should now contain a list of
		# packages We'll step through them one by one and
		# display them all at once at the end.
		form_action = "http://packages.debian.org/search?%s"
		form_inputs = urllib.urlencode ({"keywords": self.package,
						 "searchon": "names",
						 "exact": 1,
						 "suite": self.branch,
						 "section": "all"})
		# build the request
		try:
			response = urllib.urlopen(form_action % form_inputs)
		except Exception, e:
			self.Debug(e)
		else:
			self.reset()
			self.feed(response.read())
		response.close()
		return Event("privmsg", "", target, [self.o.getvalue()])

	def handle_starttag(self, tag, attrs):
		if tag == "div":
			for a_name, a_value in attrs:
				if a_name == "id" and a_value == "inner":
					self.inner_div = True
		elif tag == "ul" and self.inner_div:
			self.in_ul = True
		elif tag == "li" and self.in_ul:
			self.li += 1
			self.after_br = False
			if self.li <= self.__max_hit:
				self.o.write(" =%d=> " % self.li)
			else:
				self.li_over = True
		elif tag == "a" and self.in_ul and not self.li_over:
			for a_name, a_value in attrs:
				if a_name == "href":
					self.o.write("http://packages.debian.org%s " % a_value)
					self.in_a = True
		elif tag == "br" and self.in_ul:
			self.after_br = True

	def handle_endtag(self, tag):
		if tag == "ul":
			self.in_ul = False
		elif tag == "a":
			self.in_a = False

	def handle_data(self, data):
		if self.in_ul and \
			    not self.li_over and \
			    not self.in_a and \
			    not self.after_br:
			self.o.write(data.strip())

class debfile(MooBotModule, HTMLParser.HTMLParser):
	"""
	Does a file search on http://packages.debian.org and returns
	top 10 matched package names
	"""

	def __init__(self):
		self.regex = "^debfile .+"
		self.file = ""
		self.version = ""
		HTMLParser.HTMLParser.__init__(self)

	def reset(self):
		HTMLParser.HTMLParser.reset(self)
		self.o = IrcStringIO("%s(%s):" % (self.file, self.version))
		
		# s stands for stats, True means inside that tag
		# p stands for parent
		# c stands for children
		self.tag_structs = {'div': {'s': False,
					    'p': None,
					    'c': ('table',),
					    'id': 'pcontentsres'},
				    'table': {'s': False,
					      'p': 'div',
					      'c': ('tr',)},
				    'tr': {'s': False,
					   'p': 'table',
					   'c': ('td',)},
				    'td': {'s': False,
					   'p': 'tr',
					   'c': ('span', 'a')},
				    'span': {'s': False,
					     'p': 'td',
					     'c': None,
					     'class': 'keyword'},
				    'a': {'s': False,
					  'p': 'td',
					  'c': None}}


		# first raw is table header <th>
		self.hit = -1
		self.__max_hit = 10
		
		self.in_file_td_head = False
		self.file_td_head = ''
		self.in_file_td_tail = False
		self.file_td_tail = ''

		self.file_keyword = ''

	def handler(self, **args):
		
		target = self.return_to_sender(args)
		self.version = ['oldstable', 'stable', 'testing', 'unstable']
		request = args["text"].split()[2:]
		if request[0] in self.version:
			self.version = request[0]
			del request[0]
		else:
			self.version = "testing"
		if len(request) != 1:
			msg = "Usage: debfile [oldstable|stable|testing|unstable] filename"
			return Event("privmsg", "", target, [msg])
		self.file = request[0]
		form_action = "http://packages.debian.org/search?%s"
		form_inputs = urllib.urlencode({"searchon": "contents",
						"keywords": self.file,
						"mode": "path",
						"suite": self.version,
						"arch": "i386"})
		try:
			result = urllib.urlopen(form_action % form_inputs)
		except Exception, e:
			self.Debug(e)
		else:
			self.reset()
			self.feed(result.read())
			result.close()
			return Event("privmsg", "",
				     target,
				     [self.found_or_not()])

	def found_or_not(self):
		return self.o.getvalue().strip() or \
		    "%s(%s): Not Found!" % (self.file, self.version)

	def _check_stat(self, tag):
		"""To see if we can change tag's inside/outside stat

		return True if we can change it, or return False.
		"""
		# out of parent tag, we do nothing
		if self.tag_structs[tag]['p'] and \
		   not self.tag_structs[self.tag_structs[tag]['p']]['s']:
			return False

		# must be out of all chilren tags or we do nothing
		elif self.tag_structs[tag]['c']:
			for c in self.tag_structs[tag]['c']:
				if self.tag_structs[c]['s']:
					return False

		return True

	def handle_starttag(self, tag, attrs):
		if self.tag_structs.has_key(tag):
			if attrs:
				for a, v in attrs:
					if self.tag_structs[tag].has_key(a) and \
						    self.tag_structs[tag][a] != v:
						return

			if self._check_stat(tag) and \
				    not self.tag_structs[tag]['s']:
				self.tag_structs[tag]['s'] = True

				for a, v in attrs:
					if tag == 'td' and \
						    a == 'class' and\
						    v == 'file':
						self.in_file_td_head = True
					elif tag == 'span' and \
						    a == 'class' and \
						    v == 'keyword':
						self.in_file_td_head = False



	def handle_endtag(self, tag):
		if self.tag_structs.has_key(tag):
			if self._check_stat(tag) and \
				    self.tag_structs[tag]['s']:
				self.tag_structs[tag]['s'] = False

				if tag == 'tr':
					self.hit += 1

				elif tag == 'span':
					# YES, it's unreliable. But if
					# there's no 'span' there
					# would be no
					# file_td_head/tail either,
					# there would be only one
					# file_td
					self.in_file_td_tail = True

				elif tag == 'td' and \
					    (self.in_file_td_head or \
						     self.in_file_td_tail):
					# span is unreliable
					self.in_file_td_head = False
					self.in_file_td_tail = False
					

	def handle_data(self, data):
		if self.hit < self.__max_hit:
			if self.tag_structs['td']['s']:
				if self.in_file_td_head:
					self.file_td_head = data
				elif self.in_file_td_tail:
					self.file_td_tail = data

			if self.tag_structs['span']['s']:
				self.file_keyword = data

			if self.tag_structs['a']['s']:
				self.o.write(' =%d=> ' % (self.hit + 1))
				if self.file_td_head:
					self.o.write(self.file_td_head)
				if self.file_keyword:
					self.o.write(self.file_keyword)
				if self.file_td_tail:
					self.o.write(self.file_td_tail)
				
				self.o.write(' ')
				self.o.write(data)

class genpackage(MooBotModule):
	"""
	Does a package or file search on http://www.portagefilelist.de/index.php/Special:PFLQuery2 and returns top 10 result
	"""
	re_tag = re.compile("<[^>]+>")
	re_td = re.compile("<td[^>]*>(.*?)</td>", re.S)
	def __init__(self):
		self.regex="^(genpackage|genfile)( .+)?$"

	def handler(self, **args):
		target = self.return_to_sender(args)

		request = args["text"].split()[1:]

		if len(request) == 2:
			all = False
			cmd, param = request
		elif len(request) == 3 and request[1] == 'all':
			all = True
			cmd, dummy, param = request
		else:
			msg = "Usage: genpackage [all] [$dir/]$packagename, OR genfile [all] $path"
			return Event("privmsg", "", target, [msg])
		form_action = "http://www.portagefilelist.de/index.php/Special:PFLQuery2"
		if cmd == 'genpackage':
			package = param
			if package.find('/') != -1:
				dir, package = package.split('/', 1)
			else:
				dir = ''

			params = {
				"dir": dir,
				"package": package,
				"searchpackage": "lookup",
				"lookup": "package"}
			if not all:
				params["group_pkgs"] = "on"
		else:
			file = param

			params = {
				"file": file,
				"searchfile": "lookup",
				"lookup": "file"}
			if not all:
				params["group_file"] = "on"

		form_inputs = urllib.urlencode(params)
		# build the request
		try:
			response = urllib.urlopen(form_action + '?' + form_inputs)
		except Exception, e:
			return Event("privmsg", "", target, [str(e)])
		msg_notfound = Event("privmsg", "", target, ["not found"])
		html = response.read().decode("UTF-8")
		if html.find("query execution time") == -1:
			return msg_notfound
		dummy, html = html.split("query execution time", 1)
		if html.find("</table") == -1:
			return msg_notfound
		html, dummy = html.split("</table", 1)
		results = []
		rows = html.split("</tr")[:-1]
		for row in rows:
			tds = self.re_td.findall(row)
			# genpackage
			if len(tds) == 2:
				results.append(self.re_tag.sub("", "%s/%s" % (tds[0], tds[1])))
			elif len(tds) == 3:
				results.append(self.re_tag.sub("", "%s/%s-%s" % (tds[0], tds[1], tds[2])))
			# genfile
			elif len(tds) == 5:
				results.append(self.re_tag.sub("", "%s/%s in %s/%s" % (tds[2], tds[3], tds[0], tds[1])))
			elif len(tds) == 6:
				results.append(self.re_tag.sub("", "%s/%s in %s/%s-%s" % (tds[2], tds[3], tds[0], tds[1], tds[5])))
			#else:
			#	return msg_notfound
		results.sort(lambda x,y: cmp(y.lower(), x.lower()))
		result = ", ".join(results[0:10])
		return Event("privmsg", "", target, [result])

class acronym(MooBotModule):
	""" Does a search on www.acronymfinder.com and returns all definitions

	TODO. According to http://www.acronymfinder.com/terms.htm , we
	must switch to other sites. like:

	http://silmaril.ie/cgi-bin/uncgi/acronyms
	http://acronyms.thefreedictionary.com/
	TODO. http://www.gaarde.org/acronyms/?lookup=ASAP
	TODO. http://www.urbandictionary.com/define.php?term=ASAP
	TODO. Parser
	"""
	def __init__(self):
		self.regex = "^explain [a-zA-Z]+"

	def handler(self, **args):
		target = self.return_to_sender(args)

		search_term = args["text"].split(" ")[2].upper()
		search_parms = urllib.urlencode({'Acronym': search_term,
				 'Find': 'find',
				 'string':'exact'})
		response = urllib.urlopen('http://www.acronymfinder.com/af-query.asp?%s' % search_parms)
		listing = response.read().decode("UTF-8")

		search = re.compile("<td[^>]*>[^<>\n\r]*%s[^<>\n\r]*</td>\s*<td[^>]*>([A-Za-z][^<\n\r]+)\s*</td>" % search_term)
		definitions = search.findall(listing)
		if len(definitions) == 0:
			line = "Could not find a definition for " + search_term
		elif len(definitions) == 1:
			line = search_term + " is " + definitions[0]
		else:
			line = search_term + " is one of the following: \"" + '", "'.join(definitions) + "\""
		line = line.replace("&nbsp;", " ")
		return Event("privmsg", "", self.return_to_sender(args), [ line ])


class foldoc(MooBotModule):
	"""
	Free On-line Dicitionary Of Computing
	"""
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
		self.return_to_sender(args)

		
		search_terms = args["text"].split(" ")[2:]
		domain = "pgp.mit.edu"
		port=11371
		search_request = "/pks/lookup?op=index&search="
		search_request += '+'.join(search_terms)
		connect = httplib.HTTPConnection(domain, port)
		connect.request("GET", search_request)
		response = connect.getresponse()
		if response.status != 200:
			msg = str(response.status) + ": " + response.reason
			self.debug(msg)
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
		line = "pgpkey matches for \"" + ' '.join(search_terms) + "\": "
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
		
		target = self.return_to_sender(args)

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


class lunarCal(MooBotModule):
	"""黄历查询 by Ian@linuxfire.com.cn
		Action: http://www.shpan.com/huangli/MyDetail.asp?currentDate=
		Method: GET
		Params: yyyy-mm-dd
	"""
	URL = "http://www.shpan.com/huangli/MyDetail.asp?currentDate="
	def __init__(self):
		self.regex = "^hl( +[^ ]*)?"
	
	def parse_date(self, strDate):
		from datetime import date
		if strDate.isdigit():
			d = date(int(strDate[0:-4]), int(strDate[-4:-2]), int(strDate[-2:]))
		else:
			tupDate = re.findall('(\d+)-(\d+)-(\d+)', strDate)
			if len(tupDate) == 1:
				d = date(int(tupDate[0][0]), int(tupDate[0][1]), int(tupDate[0][2]))
			else:
				raise ValueError, "输入格式不正确。";
		return d.isoformat()
	
	def fetch(self, date):
		#print date
		response = urllib.urlopen(lunarCal.URL+date)
		html = response.read().decode("GBK")
		response.close()
		return html
	
	def extract(self, text):
		date = re.compile("中华人民共和国\d{4}年\d+月\d+日黄历".decode("GBK"))
		hl = re.search(date, text)
		if hl:
			msg = ["\002" + hl.group(0) + "\002.  "]
			date = re.compile('<tr>[^<]*<td[^>]*class="TdShow"\s*>([^<]*)</td>\s*<td[^>]*class="TdShow"\s*>([^<]*)</td>\s*</tr>')
			for item in re.findall(date, text):
				msg.append("\002" + item[0].strip() + "\002 " + item[1].strip())
			return msg
		else:
			raise ValueError, "查询结果无效。";
	
	def handler(self, **args):
		qstr = args["text"].strip().split(" ")[1:]
		try:
			if len(qstr) == 1:
				from datetime import date
				theDate = date.today().isoformat()
			elif len(qstr) == 2:
				theDate = self.parse_date(qstr[1])
			else:
				raise ValueError, "输入格式不正确。";
			msg = ["\n".join(self.extract(self.fetch(theDate)))]
		except ValueError, e:
			desc = str(e).decode("GBK")
			msg = [desc]
		#for m in msg: print m
		return Event("notice",
			     "",
			     self.return_to_sender(args, select="nick"),
			     msg)

class ohloh(MooBotModule):
	urlAccount = "http://www.ohloh.net/accounts/{account_id}.xml"
	def __init__(self):
		self.regex = "^((ohloh|kudo)( +.+)?|(ohloh|kudo) +[^ ]+( +[^ ]+)?|(ohloh|kudo) help)$"
	
	def getKey(self, bot):
		return bot.configs["ohloh"]["key"]

	def domNodeToObject(self, node):
		import xml.dom.minidom as dom
		obj = {}
		text = ''
		for node in node.childNodes:
			if node.nodeType == node.ELEMENT_NODE:
				obj[node.nodeName] = self.domNodeToObject(node)
			elif node.nodeType == node.TEXT_NODE:
				text += node.nodeValue
		if not obj:
			obj = text
		return obj

	def queryAccount(self, bot, account):
		if account.find("@") != -1:
			import md5
			m = md5.new()
			m.update(account)
			account = m.hexdigest()


		params = urllib.urlencode({ 'api_key': self.getKey(bot), 'v': 1 })
		url = self.urlAccount.replace('{account_id}', account) + "?" + params
		print url
		response = urllib.urlopen(url)
		html = response.read()
		response.close()

		import xml.dom.minidom as dom
		doc = self.domNodeToObject(dom.parseString(html).documentElement)
		if not doc or doc["status"] != "success":
			return None

		return doc["result"]["account"]
	
	def handler(self, **args):
		bot = args["ref"]()
		try:
			self.getKey(bot)
		except ValueError:
			return Event("privmsg", "", self.return_to_sender(args), [ u"ohloh key not configured" ])

		argv = args["text"].strip().split(" ")
		del argv[0]
		cmd = argv[0].replace("kudo", "ohloh")
		del argv[0]
		target = self.return_to_sender(args)

		while True:
			if cmd == "ohloh":
				if len(argv) == 1:
					name = argv[0]
				else:
					from irclib import nm_to_n
					name = nm_to_n(args['source'])

				account = self.queryAccount(bot, name)
				if not account:
					msg = [ u"%s not found on ohloh" % name ]
					break

				try:
					kudo_rank = int(account["kudo_score"]["kudo_rank"])
					kudo_position = int(account["kudo_score"]["position"])
				except KeyError:
					kudo_rank = 1
					kudo_position = 999999

				name = account["name"]
				msg = [ u"%s has kudo lv %d #%d on ohloh, located at %s %s" % (
						name,
						kudo_rank,
						kudo_position,
						account["location"],
						account["homepage_url"]
						) ]
			elif cmd == "ohlohpk" and len(argv) > 0:
				if len(argv) == 2:
					name1, name2 = argv
				else:
					from irclib import nm_to_n
					name1, name2 = (nm_to_n(args['source']), argv[0])

				# getting info
				account1 = self.queryAccount(bot, name1)
				if not account1:
					msg = [ u"%s not found on ohloh" % name1 ]
					break

				account2 = self.queryAccount(bot, name2)
				if not account2:
					msg = [ u"%s not found on ohloh" % name2 ]
					break

				# compare
				try:
					pos1 = int(account1["kudo_score"]["position"])
				except KeyError:
					pos1 = 999999
				try:
					pos2 = int(account2["kudo_score"]["position"])
				except KeyError:
					pos2 = 999999

				# result
				name1 = account1["name"]
				name2 = account2["name"]
				result = pos1 - pos2
				self.Debug(result)
				if result == 0:
					msg = [ u"both %s and %s are just newbie on ohloh" % (name1, name2) ]
				elif result < 0:
					msg = [ u"%s#%d ROCKS and %s#%d sucks" % (name1, pos1, name2, pos2)  ]
				else:
					msg = [ u"%s#%d sucks and %s#%d ROCKS" % (name1, pos1, name2, pos2)  ]
			else:
				msg = [ u"Usage: ohloh OR ohloh help OR ohloh $nick OR ohlohpk $nick1 $nick2, see http://www.ohloh.net/" ]
			break

		return Event("privmsg", "", target, msg)

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()


# vim:set shiftwidth=4 softtabstop=4
