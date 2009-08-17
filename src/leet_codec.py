# -*- coding:utf-8 -*-

import codecs, StringIO

_leetCharMap={"A":"/_\\", "B":"b", "C":"(", "D":"|)", "E":"e",
              "F":"F", "G":"6", "H":"|-|", "I":"eye", "J":"j",
              "K":"|{", "L":"L", "M":"|\\/|", "N":"|\\|",
              "O":"()", "P":"P", "Q":"q", "R":"R", "S":"$",
              "T":"7", "U":"|_|", "V":"\\/", "W":"\\/\\/",
              "X":"><", "Y":"y", "Z":"z", "a":"4", "b":"8",
              "c":"(", "d":"d", "e":"3", "f":"f", "g":"6",
              "h":"h", "i":"1", "j":"j", "k":"k", "l":"|",
              "m":"m", "n":"N", "o":"0", "p":"p", "q":"q",
              "r":"r", "s":"5", "t":"7", "u":"U", "v":"V",
              "w":"w", "x":"X", "y":"y", "z":"Z", " ":" "}
_leetWordMap={"you":"j00", "the":"teh", "your":"j00r",
              "ever":"evar", "sucks":"soxz", "rocks":"roxz"}

def leet(input):
	output = StringIO.StringIO()
	for word in input.split(" "):
		if word in _leetWordMap:
			output.write(_leetWordMap[word])
		else:
			for char in word:
				if char in _leetCharMap:
					output.write(_leetCharMap[char])
				else:
					output.write(char)
		output.write(' ')
	return output.getvalue()

def encode(input):
	output = leet(input)
	return (output, len(output))

def decode(input):
	output = "LEET decode wasn't implemented yet"
	return (output, len(output))

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
	if encoding == "1337" or encoding == "leet":
		return (encode, decode, StreamReader, StreamWriter)

	return None

codecs.register(search_function)

