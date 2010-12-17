import urllib, codecs

def url_encode(input):
	output = urllib.quote(input)
	return (output, len(output))

def url_decode(input):
	output = urllib.unquote(input)
	return (output, len(output))

def encode_plus(input):
	output = urllib.quote_plus(input)
	return (output, len(output))

def decode_plus(input):
	output = urllib.unquote_plus(input)
	return (output, len(output))

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
		return encode_plus(input, errors)

	def decode(self, input, errors='strict'):
		return decode_plus(input, errors)

class StreamWriter_plus(Codec_plus, codecs.StreamWriter):
	pass

class StreamReader_plus(Codec_plus, codecs.StreamReader):
	pass

def search_function(encoding):
	if encoding == "url":
		return (url_encode, url_decode, StreamReader, StreamWriter)

	if encoding == "url+":
		return (encode_plus, decode_plus, StreamReader_plus, StreamWriter_plus)

	return None

codecs.register(search_function)
