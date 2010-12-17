import hashlib, codecs

def encode_md5(input):
	output = hashlib.md5(input).hexdigest()
	return (output, len(output))

def decode_md5(input):
	output = 'unable to decode md5'
	return (output, len(output))

class Codec_md5(codecs.Codec):
	def encode(self, input, errors='strict'):
		return encode_md5(input, errors)

	def decode(self, input, errors='strict'):
		return decode_md5(input, errors)

class StreamWriter_md5(Codec_md5, codecs.StreamWriter):
	pass

class StreamReader_md5(Codec_md5, codecs.StreamReader):
	pass

def search_function(encoding):
	if encoding == "md5":
		return (encode_md5, decode_md5, StreamReader_md5, StreamWriter_md5)

	return None

def encode_sha1(input):
	output = hashlib.sha1(input).hexdigest()
	return (output, len(output))

def decode_sha1(input):
	output = 'unable to decode sha1'
	return (output, len(output))

class Codec_sha1(codecs.Codec):
	def encode(self, input, errors='strict'):
		return encode_sha1(input, errors)

	def decode(self, input, errors='strict'):
		return decode_sha1(input, errors)

class StreamWriter_sha1(Codec_sha1, codecs.StreamWriter):
	pass

class StreamReader_sha1(Codec_sha1, codecs.StreamReader):
	pass

def encode_sha224(input):
	output = hashlib.sha224(input).hexdigest()
	return (output, len(output))

def decode_sha224(input):
	output = 'unable to decode sha224'
	return (output, len(output))

class Codec_sha224(codecs.Codec):
	def encode(self, input, errors='strict'):
		return encode_sha224(input, errors)

	def decode(self, input, errors='strict'):
		return decode_sha224(input, errors)

class StreamWriter_sha224(Codec_sha224, codecs.StreamWriter):
	pass

class StreamReader_sha224(Codec_sha224, codecs.StreamReader):
	pass

def encode_sha256(input):
	output = hashlib.sha256(input).hexdigest()
	return (output, len(output))

def decode_sha256(input):
	output = 'unable to decode sha256'
	return (output, len(output))

class Codec_sha256(codecs.Codec):
	def encode(self, input, errors='strict'):
		return encode_sha256(input, errors)

	def decode(self, input, errors='strict'):
		return decode_sha256(input, errors)

class StreamWriter_sha256(Codec_sha256, codecs.StreamWriter):
	pass

class StreamReader_sha256(Codec_sha256, codecs.StreamReader):
	pass

def search_function(encoding):
	if encoding == "sha256":
		return (encode_sha256, decode_sha256, StreamReader_sha256, StreamWriter_sha256)

	return None

def encode_sha384(input):
	output = hashlib.sha384(input).hexdigest()
	return (output, len(output))

def decode_sha384(input):
	output = 'unable to decode sha384'
	return (output, len(output))

class Codec_sha384(codecs.Codec):
	def encode(self, input, errors='strict'):
		return encode_sha384(input, errors)

	def decode(self, input, errors='strict'):
		return decode_sha384(input, errors)

class StreamWriter_sha384(Codec_sha384, codecs.StreamWriter):
	pass

class StreamReader_sha384(Codec_sha384, codecs.StreamReader):
	pass

def encode_sha384(input):
	output = hashlib.sha384(input).hexdigest()
	return (output, len(output))

def decode_sha384(input):
	output = 'unable to decode sha384'
	return (output, len(output))

class Codec_sha384(codecs.Codec):
	def encode(self, input, errors='strict'):
		return encode_sha384(input, errors)

	def decode(self, input, errors='strict'):
		return decode_sha384(input, errors)

class StreamWriter_sha384(Codec_sha384, codecs.StreamWriter):
	pass

class StreamReader_sha384(Codec_sha384, codecs.StreamReader):
	pass

def encode_sha512(input):
	output = hashlib.sha512(input).hexdigest()
	return (output, len(output))

def decode_sha512(input):
	output = 'unable to decode sha512'
	return (output, len(output))

class Codec_sha512(codecs.Codec):
	def encode(self, input, errors='strict'):
		return encode_sha512(input, errors)

	def decode(self, input, errors='strict'):
		return decode_sha512(input, errors)

class StreamWriter_sha512(Codec_sha512, codecs.StreamWriter):
	pass

class StreamReader_sha512(Codec_sha512, codecs.StreamReader):
	pass

def search_function(encoding):
	if encoding == "md5":
		return (encode_md5, decode_md5, StreamReader_md5, StreamWriter_md5)
	if encoding == "sha1":
		return (encode_sha1, decode_sha1, StreamReader_sha1, StreamWriter_sha1)
	if encoding == "sha224":
		return (encode_sha224, decode_sha224, StreamReader_sha224, StreamWriter_sha224)
	if encoding == "sha384":
		return (encode_sha384, decode_sha384, StreamReader_sha384, StreamWriter_sha384)
	if encoding == "sha512":
		return (encode_sha512, decode_sha512, StreamReader_sha512, StreamWriter_sha512)

	return None

codecs.register(search_function)
