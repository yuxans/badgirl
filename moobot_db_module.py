#!/usr/bin/env python

import moobot_module

class MooBotDBModule(MooBotModule):
	"Base class for all MooBot modules using DB access"
	class MooBotDBModuleException(MooBotModuleException): pass

	def escape_slashes(str):
		"Simply replaces single and double-slashes with escaped versions"
		import string
		str = string.replace(str, "\\", "\\\\")
		str = string.replace(str, "\"", "\\\"")
		return str

	def strip_words(str, num):
		"Strips a certain number of words from the beginning of a string"
		import string
		str = string.join(str.split()[num:])
		return str
		
	def strip_punctuation(str):
		"Strips ?s and !s from the end of a string"
		while len(str) > 1 and (str[-1] == "!" or str[-1] == "?"):
			str = str[:-1]
		return str	

