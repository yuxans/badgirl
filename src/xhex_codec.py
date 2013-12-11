import codecs, re
regex = re.compile(r'(?:\\[xX][0-9a-fA-Z]{2}|&#[xX].*[0-9a-fA-Z]{2};?)+')

def xhex_encode(input):
	output = input.encode("hex")
	return (output, len(output))

def xhex_decode(input):
	output = regex.sub(lambda matches: matches.group(0).replace("\\x", "").replace("\\X", "").replace(" ", "").replace("&#x", "").replace("&#X", "").replace(";", "").decode("hex"), input)
	return (output, len(output))

class Codec(codecs.Codec):
	def encode(self, input, errors='strict'):
		return xhex_encode(input, errors)

	def decode(self, input, errors='strict'):
		return xhex_decode(input, errors)

class StreamWriter(Codec, codecs.StreamWriter):
	pass

class StreamReader(Codec, codecs.StreamReader):
	pass

def search_function(encoding):
	if encoding == "xhex":
		return (xhex_encode, xhex_decode, StreamReader, StreamWriter)

	return None

codecs.register(search_function)
