# -*- coding:utf-8 -*-

import codecs, StringIO

def reverse(input):
	output = StringIO.StringIO()
	for i in range(1, len(input)+1):
		output.write(input[-i])
	return output.getvalue()

def encode(input):
	return (reverse(input), len(input))

def decode(input):
	return (reverse(input), len(input))

class Codec(codecs.Codec):
	def encode(self, input, errors='strict'):
		return encode(input, errors)

	def decode(self, input, errors='strict'):
		return decode(input, errors)

class StreamWriter(Codec, codecs.StreamWriter):
	pass

class StreamReader(Codec, codecs.StreamReader):
	pass

def search_function(encoding):
	if encoding == "reverse":
		return (encode, decode, StreamReader, StreamWriter)

	return None

codecs.register(search_function)

