from Tile import Tile, TileSetLoader
from MinecraftBlockIDSystem import MinecraftBlockID, variantToDict, compareVariants
import json
import glob
import os
import re
import numpy as np
from scipy import misc

BLOCKSTATES = '/assets/minecraft/blockstates/'
BLOCKMODELS = '/assets/minecraft/models/block/' 
MODELS = '/assets/minecraft/models/' 
TEXTURES = '/assets/minecraft/textures/'

class MinecraftBlock(Tile):

	def __init__(self, minecraft_id):
		self.minecraft_id = minecraft_id
		self._textures = []
		self._model = None

	def loadFromFile(self,path):
		name_id = self.minecraft_id.getID('new')[0]
		variant_id = self.minecraft_id.getID('new')[1]

		json_data = open(path + BLOCKSTATES + name_id + '.json').read()
		data = json.loads(json_data)

		#Find the coresponding variant in json file
		for v in data['variants']:
			if compareVariants(variant_id,v):
				#Loading block model
				modelname = ''
				if isinstance(data['variants'][v], list):
					modelname = data['variants'][v][0]['model']
				elif isinstance(data['variants'][v], dict):
					modelname = data['variants'][v]['model']

				modelpath = path + BLOCKMODELS + modelname + '.json'
				json_model_data = open(modelpath).read()
				model_data = json.loads(json_model_data);

				for i in model_data['textures']:
					texturepath = path + TEXTURES + model_data['textures'][i] + '.png'
					self._textures.append(misc.imread(texturepath))

				while 'parent' in model_data:
				#if 'parent' in model_data:
					modelname = model_data['parent']
					modelpath = path + MODELS + modelname + '.json'
					json_model_data = open(modelpath).read()
					model_data = json.loads(json_model_data);
				self._model = model_data.get('elements')
				
				break

	def toNumpyArray(self):
		color = np.asarray([texture for texture in self._textures]).mean(axis=(0,1,2))/256.

		volume = np.sum(np.prod(
			np.asarray([element['to'] for element in self._model]) - np.asarray([element['from'] for element in self._model]),
			axis=1)).reshape((1,))/(16**3)

		orientation = np.asarray([
			variant_id.get('facing') == 'down' or variant_id.get('axis') == 'y',
			variant_id.get('facing') == 'up' or variant_id.get('axis') == 'y',
			variant_id.get('facing') == 'north' or variant_id.get('axis') == 'x',
			variant_id.get('facing') == 'south' or variant_id.get('axis') == 'x',
			variant_id.get('facing') == 'west' or variant_id.get('axis') == 'z',
			variant_id.get('facing') == 'east' or variant_id.get('axis') == 'z'
			])

		return np.concatenate((color,volume,orientation))

class MinecraftBlockSetLoader(TileSetLoader):
	def __init__(self):
		self._set = set()

	def loadFromFile(self,path):

		for file_path in glob.glob(os.path.join(path + BLOCKSTATES, '*.json')):
			json_data = open(file_path).read()
			data = json.loads(json_data)
			print file_path
			name_id = re.findall(r'([a-z_]*).json$',file_path)[0]
			for variant_id in data['variants']:
				block = MinecraftBlock(MinecraftBlockID(name = name_id,variant = variant_id))
				block.loadFromFile(path)
				self._set.add(block)


	def toNumpyArray(self):
		print self._set
		#block_element_set = Set([(element['from'],element['to']) for element in block._model for block in self._set])
		return np.asarray([block.toNumpyArray() for block in self._set])