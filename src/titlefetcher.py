
import HTMLParser
import re
import socket
from htmlentitydefs import name2codepoint
rTitle = re.compile(".*?<title>.*?</title>", re.I | re.S)

import httpfetcher
httpfetcher.HttpFetcher.version = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"

fallbackEncodings = ["GB2312", "UTF-8", "GBK", "BIG5", "Shift_JIS", "latin1"]

__all__ = ["fetch", "UnimplementedProtocol"]
UnimplementedProtocol = httpfetcher.UnimplementedProtocol

def getEncodingFromHeaders(headers):
	if headers.has_key("content-type"):
		return getEncodingFromContentType(headers["content-type"])

def getEncodingFromContentType(contentType):
	for value in contentType.split(";"):
		value = value.strip().split("charset=", 1)
		if len(value) == 2 and len(value[0]) == 0:
			return value[1]

class TitleGetter(HTMLParser.HTMLParser):
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.title = None
		self.encodings = []
		self.inTitle = False

	def handle_starttag(self, tag, attrs):
		if tag == 'title':
			self.inTitle = True
			self.title = ''
		# look for encoding
		elif tag == 'meta':
			isContentType = False
			for (attr, value) in attrs:
				if attr == 'http-equiv' and value.lower() == 'content-type':
					isContentType = True
					break
			if isContentType:
				for (attr, value) in attrs:
					if attr == 'content':
						encoding = getEncodingFromContentType(value)
						if encoding:
							self.encodings.append(encoding)
							break

	def handle_data(self, data):
		if self.inTitle:
			self.title += self.decode(data)

	def handle_entityref(self, data):
		if data in name2codepoint:
			try:
				data = unichr(name2codepoint[data])
			except ValueError:
				return

			if self.inTitle:
				self.title += data

	def handle_charref(self, data):
		if len(data):
			if data[0].lower() == 'x':
				try:
					data = unichr(int('0' + data, 16))
				except ValueError:
					return
			else:
				try:
					data = unichr(int(data))
				except ValueError:
					return

			if self.inTitle:
				self.title += data

	def handle_endtag(self, tag):
		if tag == 'title':
			self.inTitle = False

	def decode(self, data):
		for encoding in self.encodings:
			try:
				return data.decode(encoding)
			except UnicodeDecodeError:
				pass
			except LookupError:
				pass

		for encoding in fallbackEncodings:
			try:
				return data.decode(encoding)
			except UnicodeDecodeError:
				pass
			except LookupError:
				pass

def fetch(url, timeout = 10):
	match = None
	try:
		h = httpfetcher.urlopen(url, httpfetcher.RegexChecker(rTitle), timeout)
		if h.status == 200:
			match = h.fetch()
	except socket.timeout:
		return None

	if match:
		titleGetter = TitleGetter()

		encoding = getEncodingFromHeaders(h.headers)
		if encoding:
			titleGetter.encodings.append(encoding)

		try:
			titleGetter.feed(match.group(0))
			titleGetter.close()
		except HTMLParser.HTMLParseError:
			pass

		return titleGetter.title
