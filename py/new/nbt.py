# global FULL_CAPS_WITH_UNDERSCORES
# class Capital_Letters_With_Underscores
# def cammelCase()
# var non_capital_with_underscores

import sys
import struct
import gzip

from numpy import fromstring

class TAG(object):
	__slots__ = ('_name','_payload')

	def __init__(self, name="", payload=0):
		self.name = name
		self.payload = payload

	_name = None
	_payload = None

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, new_name):
		self._name = unicode(new_name)

	@property
	def payload(self):
		return self._payload
	
	@payload.setter
	def payload(self, new_payload):
		self._payload = self.payload_type(new_payload)

	def __str__(self):
		return printNBTTree(self)

	@classmethod
	def loadPayload(cls, raw_data, data_offset):
		data = raw_data[data_offset[0]:]
		payload = None
		(payload,) = cls.payload_format.unpack_from(data)
		self = cls(payload=payload)
		data_offset[0] += self.payload_format.size
		return self

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12

class TAG_Byte(TAG):
	tag_type = TAG_BYTE
	payload_type = int
	payload_format = struct.Struct(">B")

class TAG_Short(TAG):
	tag_type = TAG_SHORT
	payload_type = int
	payload_format = struct.Struct(">h")

class TAG_Int(TAG):
	tag_type = TAG_INT
	payload_type = int
	payload_format = struct.Struct(">i")

class TAG_Long(TAG):
	tag_type = TAG_LONG
	payload_type = long
	payload_format = struct.Struct(">q")

class TAG_Float(TAG):
	tag_type = TAG_FLOAT
	payload_type = float
	payload_format = struct.Struct(">f")

class TAG_Double(TAG):
	tag_type = TAG_DOUBLE
	payload_type = float
	payload_format = struct.Struct(">d")

class TAG_Array(TAG):

	def __init__(self, payload=None, name=""):
		if payload is None:
			self.payload = []
		else:
			self.payload = payload
		self.name = name

	@classmethod
	def loadPayload(cls, raw_data, data_offset):
		self = cls()
		size = TAG_Int.loadPayload(raw_data, data_offset).payload
		for i in range(size):
			element =  tag_type_IDs_to_classes[self.element_type].loadPayload(raw_data, data_offset)
			self._payload.append(element)
		return self

	def payload_type(self, payload):
		for item in payload:
			if item is not isinstance(item, tag_type_IDs_to_classes[self.element_type]):
				raise TypeError("TAG_Byte_Array's elements are not integers!")
		return list(payload)

	def __getitem__(self, index):
		return self.payload[index]

class TAG_Byte_Array(TAG_Array):
	tag_type = TAG_BYTE_ARRAY
	element_type = TAG_BYTE

class TAG_Int_Array(TAG_Array):
	tag_type = TAG_INT_ARRAY
	element_type = TAG_INT

class TAG_Long_Array(TAG_Array):
	tag_type = TAG_LONG_ARRAY
	element_type = TAG_LONG

class TAG_String(TAG):
	tag_type = TAG_STRING

	@classmethod
	def loadPayload(cls, raw_data, data_offset):
		payload = loadString(raw_data, data_offset)
		self = cls(payload = payload)
		return self

	def payload_type(self, payload):
		if isinstance(payload, unicode):
			return payload
		else:
			return payload.decode('utf-8')

def loadString(raw_data, data_offset):
	data = raw_data[data_offset[0]:]
	string_length_format = struct.Struct(">H")
	(string_length,) = string_length_format.unpack_from(data)
	data_offset[0] += 2 + string_length
	return data[2:2 + string_length].tostring()

class TAG_Compound(TAG):
	tag_type = TAG_COMPOUND

	def __init__(self, payload=None, name=""):
		if payload is None:
			self.payload = []
		else:
			self.payload = payload
		self.name = name

	@classmethod
	def loadPayload(cls, raw_data, data_offset):
		self = cls()
		while data_offset[0] < len(raw_data):
			tag_type = raw_data[data_offset[0]]

			data_offset[0] += 1

			if tag_type == 0:
				break
			name = loadString(raw_data, data_offset)
			tag = tag_type_IDs_to_classes[tag_type].loadPayload(raw_data, data_offset)
			tag.name = name
			self._payload.append(tag)
		return self

	def payload_type(self, payload):
		for t in payload:
			if t is not isinstance(t, TAG):
				raise TypeError("TAG_Compound's payload is not TAG element!")
		return list(payload)

	def __getitem__(self, name):
		matching_tag = None
		for tag in self.payload:
			if tag.name == name:
				matching_tag = tag
				break
		if matching_tag is None:
			raise KeyError("Tag with name \"{}\" not found in payload".format(str(name)))
		else:
			return matching_tag

class TAG_List(TAG):
	tag_type = TAG_LIST

	def __init__(self, payload=None, name=""):
		if payload is None:
			self.payload = []
		else:
			self.payload = payload
		self.name = name
	
	@classmethod
	def loadPayload(cls, raw_data, data_offset):
		self = cls()
		self.element_type = TAG_Byte.loadPayload(raw_data, data_offset).payload
		size = TAG_Int.loadPayload(raw_data, data_offset).payload
		for i in range(size):
			element =  tag_type_IDs_to_classes[self.element_type].loadPayload(raw_data, data_offset)
			self._payload.append(element)
		return self

	def payload_type(self, payload):
		for item in payload:
			if item is not isinstance(item, tag_type_IDs_to_classes[self.element_type]):
				raise TypeError("TAG_Byte_Array's elements are not integers!")
		return list(payload)

	def __getitem__(self, index):
		return self.payload[index]


tag_type_IDs_to_classes = {}
tag_classes = (TAG_Byte, TAG_Short, TAG_Int, TAG_Long, TAG_Float, TAG_Double, TAG_Byte_Array, TAG_Int_Array, TAG_Long_Array, TAG_String, TAG_Compound, TAG_List)
for class_name in tag_classes:
	tag_type_IDs_to_classes[class_name.tag_type] = class_name

def printNBTTree(root_tag, level=0):
	output_string = ""
	if root_tag.tag_type in [TAG_COMPOUND, TAG_BYTE_ARRAY, TAG_INT_ARRAY, TAG_LONG_ARRAY, TAG_LIST]:
		output_string += "	"*level + "+ [{}] {} :\n".format(str(root_tag.__class__.__name__),root_tag.name)
		for tag in root_tag.payload:
			output_string += printNBTTree(tag, level+1)
	elif root_tag.tag_type in [TAG_BYTE]:
		output_string += "	"*level + "- [{}] {} : {}\n".format(str(root_tag.__class__.__name__),root_tag.name,root_tag.payload)
	else:
		output_string += "	"*level + "- [{}] {} : {}\n".format(str(root_tag.__class__.__name__),root_tag.name,root_tag.payload)
	return output_string

def load(file_name):
	with gzip.open(file_name,"rb") as file:
		raw_data = file.read()
		if isinstance(raw_data, str):
			raw_data = fromstring(raw_data, 'uint8')
		data_offset = [1]
		tag_name = loadString(raw_data, data_offset)
		tag = TAG_Compound.loadPayload(raw_data, data_offset)
		tag.name = tag_name
	return tag

def main():
    tag = load(sys.argv[1])
    print(tag["BlockData"][0:32])
    

if __name__ == '__main__':
    main()