import nbt

class IDMapper(object):
	__slots__ = ('_dict')

	def __init__(self, dictionary={}):
		self.dict = dictionary

	@property
	def dict(self):
		return self._dict

	@dict.setter
	def dict(self, dictionary):
		self._dict = dict(dictionary)

	def __getitem__(self, id):
		if id in self._dict:
			return self._dict[id]
		else:
			return self.expand(id)

class IDMapper_Pipeline(IDMapper):
	__slots__ = ('_dict','_pipeline')
	def __init__(self, pipeline, dictionary={}):
		self.dict = dictionary
		if pipeline is not None:
			self.pipeline = pipeline

	@property
	def pipeline(self):
		return self._pipeline

	@pipeline.setter
	def pipeline(self, pipeline):
		self._pipeline = self.checkPipelineType(pipeline)

	def checkPipelineType(self, pipeline):
		for pipe in pipeline:
			if not isinstance(pipe, IDMapper):
				raise TypeError("Pipe must be an IDMapper!")
		return pipeline

	def expand(self, id):
		result = id
		for pipe in self.pipeline:
			result = pipe[result]
		self.dict[id] = result
		return result
	
class PaletteID_To_NamespaceID(IDMapper):
	__slots__ = ('_dict','_palette')
	def __init__(self, palette, dictionary={}):
		self.dict = dictionary
		self.palette = palette

	@property
	def palette(self):
		return self._palette

	@palette.setter
	def palette(self, palette):
		self._palette = self.checkPaletteType(palette)

	def checkPaletteType(self, palette):
		if not isinstance(palette, nbt.TAG_Compound):
			raise TypeError("Palette must be a TAG_Compound tag!")
		return palette

	def expand(self, id):
		for element in self._palette.payload:
			if element.payload == id:
				self._dict[id] = element.name
				return element.name

class NamespaceID_To_NumericID(IDMapper):
	def __init__(self):
		self.dict = {}
		with open("namespace_ids.txt",'r') as namespace_ids:
			with open("numeric_ids.txt",'r') as numeric_ids:
				for i, (name, num) in enumerate(zip(namespace_ids,numeric_ids)):
					self._dict[name.strip()] = int(num)

	def expand(self, id):
		raise KeyError("Namespace ID \"{}\" doesn\'t match any numeric ID!".format(id))