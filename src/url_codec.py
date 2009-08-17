import urllib, codecs

def encode(input):
	return (urllib.quote(input), len(input))

def decode(input):
	return (urllib.unquote(input), len(input))

def encode_plus(input):
	return (urllib.quote_plus(input), len(input))

def decode_plus(input):
	return (urllib.unquote_plus(input), len(input))

class Codec(codecs.Codec):
	def encode(self, input, errors='strict'):
		return encode(input, errors)

	def decode(self, input, errors='strict'):
		return decode(input, errors)

class StreamWriter(Codec, codecs.StreamWriter):
	pass

class StreamReader(Codec, codecs.StreamReader):
	pass

class Codec_plus(codecs.Codec):
	def encode(self, input, errors='strict'):
		return encode_plus(input, errors)

	def decode(self, input, errors='strict'):
		return decode_plus(input, errors)

class StreamWriter_plus(Codec_plus, codecs.StreamWriter):
	pass

class StreamReader_plus(Codec_plus, codecs.StreamReader):
	pass

def search_function(encoding):
	if encoding == "url":
		return (encode, decode, StreamReader, StreamWriter)

	if encoding == "url+":
		return (encode_plus, decode_plus, StreamReader_plus, StreamWriter_plus)

	return None

codecs.register(search_function)
