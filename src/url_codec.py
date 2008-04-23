import urllib, codecs

__all__ = ['encode', 'decode']

def url_encode(input):
	return (urllib.quote(input), len(input))

def url_decode(input):
	return (urllib.unquote(input), len(input))

def url_encode_plus(input):
	return (urllib.quote_plus(input), len(input))

def url_decode_plus(input):
	return (urllib.unquote_plus(input), len(input))

class Codec(codecs.Codec):
	def encode(self, input, errors='strict'):
		return url_encode(input, errors)

	def decode(self, input, errors='strict'):
		return url_decode(input, errors)

class StreamWriter(Codec, codecs.StreamWriter):
	pass

class StreamReader(Codec, codecs.StreamReader):
	pass

class Codec_plus(codecs.Codec):
	def encode(self, input, errors='strict'):
		return url_encode_plus(input, errors)

	def decode(self, input, errors='strict'):
		return url_decode_plus(input, errors)

class StreamWriter_plus(Codec_plus, codecs.StreamWriter):
	pass

class StreamReader_plus(Codec_plus, codecs.StreamReader):
	pass

def search_function(encoding):
	if encoding == "url":
		return (url_encode, url_decode, StreamReader, StreamWriter)

	if encoding == "url+":
		return (url_encode_plus, url_decode_plus, StreamReader_plus, StreamWriter_plus)

	return None

codecs.register(search_function)
