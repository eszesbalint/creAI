from abc import ABCMeta, abstractmethod
class Tile:
	__metaclass__ = ABCMeta
	@abstractmethod
	def __init__(self):
		pass

	@abstractmethod
	def toNumpyArray(self):
		pass

class TileSetLoader:
	__metaclass__ = ABCMeta
	@abstractmethod
	def __init__(self):
		pass

	@abstractmethod
	def toNumpyArray(self):
		pass