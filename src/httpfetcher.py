
import urlparse
import select
import socket
import time
import errno

__all__ = ["RegexChecker", "urlopen"]

class HttpFetcherException(Exception):
	pass

class UnimplementedFileNode(HttpFetcherException):
	pass

class UnimplementedProtocol(HttpFetcherException):
	pass

class BadResponse(HttpFetcherException):
	pass

class FakeSocket:
	class _closedsocket:
		def __getattr__(self, name):
			raise error(9, 'Bad file descriptor')

	def __init__(self, sock, ssl):
		self._sock = sock
		self._ssl = ssl

	def close(self):
		self._sock.close()
		self._sock = self.__class__._closedsocket()

	def makefile(self, mode, bufsize=None):
		raise UnimplementedFileMode()

	def send(self, stuff, flags = 0):
		return self._ssl.write(stuff)

	sendall = send

	def recv(self, len = 1024, flags = 0):
		return self._ssl.read(len)

	def __getattr__(self, attr):
		return getattr(self._sock, attr)

class RegexChecker:
	def __init__(self, regex):
		self.regex = regex

	def __call__(self, buffer):
		match = self.regex.search(buffer)
		if match:
			return match

class Fetcher:
	def __init__(self, checker, timeout):
		self.checker = checker
		self.timeout = timeout
		self.timeouttime = time.time() + timeout
		self.buffer = ""

	def connectSocket(self):
		sock = socket.socket()
		# not supported by tsocks
		# sock.settimeout(self.timeout)
		#err = errno.EAGAIN
		#while err == errno.EAGAIN:
		err = sock.connect_ex((self.host, self.port or self.defaultPort))
		if err not in (0, errno.EISCONN, errno.EAGAIN):
			raise socket.error, (err, errno.errorcode[err])
		return sock

	def waitSocket(self, sock):
		fileno = sock.fileno()
		n = 0
		while not n:
			if time.time() >= self.timeouttime:
				raise socket.timeout("timed out")
			n = select.select([fileno], (), (), self.timeouttime - time.time())

	def timedRead(self):
		self.waitSocket(self.sock)
		buf = self.sock.recv(8192)
		return buf

	def fetch(self):
		while True:
			ret = self.checker(self.buffer)
			if ret is not None:
				return ret

			buf = self.timedRead()
			if not buf:
				break
			self.buffer += buf

class HttpFetcher(Fetcher):
	version = "HttpFetcher/1.0"
	defaultPort = 80

	def __init__(self, host, port, uri, checker, timeout = 120):
		Fetcher.__init__(self, checker, timeout)
		self.uri = uri
		self.host = host
		self.port = port
		self.status = 0
		self.connect()
		self.sendRequest()
		self.headers = self.readHeaders()

	def connect(self):
		self.sock = self.connectSocket()

	def sendRequest(self):
		self.sock.send(
				("GET %s HTTP/1.0\r\n" % self.uri) +
				("Host: %s%s\r\n" % (self.host, self.port and (":" + str(self.port)) or "")) +
				("User-Agent: %s\r\n" % self.version) +
				"Connection: closed\r\n"
				"\r\n"
				)

	def readHeaders(self):
		while True:
			buf = self.timedRead()
			if not buf:
				break
			self.buffer += buf
			if self.buffer.find("\r\n\r\n") != 0:
				headers, self.buffer = self.buffer.split("\r\n\r\n", 1)
				return self.parseHeaders(headers)

	def parseHeaders(self, headers):
		statusLine, headers = headers.split("\r\n", 1)
		statusLine = statusLine.split(' ', 2)
		if len(statusLine) != 3:
			raise BadResponse(statusLine)
		self.status = int(statusLine[1])

		parsedHeaders = {}
		for i in headers.split("\r\n"):
			i = i.split(":", 1)
			if len(i) != 2:
				raise BadResponse(i)
			field, value = i
			field = field.strip()
			value = value.strip()
			parsedHeaders[field.lower()] = value

		return parsedHeaders

class HttpsFetcher(HttpFetcher):
	defaultPort = 443
	def connect(self):
		self._sock = self.connectSocket()
		self.ssl = socket.ssl(self._sock)
		self.sock = FakeSocket(self._sock, self.ssl)

def urlopenNonRecursive(url, checker, timeout = 10):
	url = urlparse.urlparse(url)
	uri = url.path or '/'
	if url.query:
		uri += '?' + url.query

	if url.scheme == 'http':
		return HttpFetcher(url.hostname, url.port, uri, checker, timeout)
	elif url.scheme == 'https':
		return HttpsFetcher(url.hostname, url.port, uri, checker, timeout)
	else:
		raise UnimplementedProtocol(url.scheme)

def urlopen(url, checker, timeout = 10):
	recursiveCount = 10
	fetcher = None
	while True:
		fetcher = urlopenNonRecursive(url, checker, timeout)
		if fetcher.status == 301 or fetcher.status == 302:
			if 'location' in fetcher.headers:
				url = fetcher.headers['location']
				recursiveCount -= 1
				if recursiveCount > 0:
					continue
		break

	return fetcher

def urlopen2(url, checker, timeout = 10):
	match = None
	error = None
	try:
		fetcher = urlopen(url, checker, timeout)
		match = fetcher.fetch()
	except socket.timeout:
		error = "timeout"
	return (match, error)
