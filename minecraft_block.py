from tile import Tile, TileSetLoader
import json
import glob
import os
from scipy import misc

class MinecraftBlock(Tile):
	# id - Numeric block id
	# data - Data value specifying a variant
	# name - The block's name in the new format
	# variant - A dictionary specifying the variant with key-value pairs, None is the default (normal) variant
	def __init__(self, id = None, data = None, name = None, variant = None, color, volume):
		self._color = None
		self._volume = None

		if name is not None and variant is not None:
			self.name = name
			self.variant = variant
		elif id is not None and data is not None:
			if id == 0:
				self.name = "air"
				self.variant = None
			if id == 1:
				self.name = [
					"stone",
					"granite",
					"polished_granite",
					"diorite",
					"polished_diorite",
					"andesite",
					"polished_andesite"
				][data]
				self.variant = None
			if id == 2:
				self.name = "grass"
				self.variant = None
			if id == 3:
				self.name = [
					"dirt",
					"coarse_dirt",
					"podzol"
				][data]
				self.variant = None
			if id == 4:
				self.name = "cobblestone"
				self.variant = None
			if id == 5:
				self.name = [
					"oak_planks",
					"spurce_planks",
					"birch_planks",
					"jungle_planks",
					"acacia_planks",
					"dark_oak_planks"
				][data]
				self.variant = None
			if id == 6:
				self.name = [
					"oak_sapling",
					"spurce_sapling",
					"birch_sapling",
					"jungle_sapling",
					"acacia_sapling",
					"dark_oak_sapling"
				][data]
				self.variant = None
			if id == 7:
				self.name = "bedrock"
				self.variant = None
			if id == 12:
				self.name = [
					"sand",
					"red_sand"
				][data]
				self.variant = None
			if id == 13:
				self.name = "gravel"
				self.variant = None
			if id == 14:
				self.name = "gold_ore"
				self.variant = None
			if id == 15:
				self.name = "iron_ore"
				self.variant = None
			if id == 16:
				self.name = "coal_ore"
				self.variant = None
			if id == 17:
				if (int(bin(data)[-4:-2],2) < 3):
					self.name = [
						"oak_log",
						"spurce_log",
						"birch_log",
						"jungle_log"
					][int(bin(data)[-2:-1],2)]
					self.variant = [
						{"axis":"y"},
						{"axis":"z"},
						{"axis":"x"}
					][int(bin(data)[-4:-2],2)]
				else:
					self.name = [
						"oak_bark",
						"spurce_bark",
						"birch_bark",
						"jungle_bark"
					][int(bin(data)[-2:-1],2)]
					self.variant = None
			if id == 18:
				self.name = [
					"oak_leaves",
					"spurce_leaves",
					"birch_leaves",
					"jungle_leaves"
				][int(bin(data)[-2:-1],2)]
				self.variant = None
			if id == 19:
				self.name = [
					"sponge",
					"wet_sponge"
				][data]
				self.variant = None
			if id == 20:
				self.name = "glass"
				self.variant = None
			if id == 21:
				self.name = "lapis_ore"
				self.variant = None
			if id == 22:
				self.name = "lapis_block"
				self.variant = None
			if id == 23:
				self.name = "dispenser"
				self.variant = [
					{"facing":"down"},
					{"facing":"up"},
					{"facing":"north"},
					{"facing":"south"},
					{"facing":"west"},
					{"facing":"east"}
				][int(bin(data)[-3:-1],2)]
			if id == 24:
				self.name = [
					"sandstone",
					"chiseled_sandstone",
					"smooth_sandstone"
				][data]
				self.variant = None
		else:
			
	def 
	def toNumpyArray(self):
		path = './Minecraft/assets/minecraft/blockstates/'
		filename = glob.glob(os.path.join(path, self.name+'.json')):
			try:
				json_data = open(filename).read()
				data = json.loads(json_data);
		
				for i in data["variants"]:
					features = [0,0,0,0,0,0]
					modelname = data["variants"][i]["model"]
					if ("top" in i):
						features[0] = 1
					if ("bottom" in i):
						features[1] = 1
					if ("north" in i):
						features[2] = 1
					if ("east" in i):
						features[3] = 1
					if ("south" in i):
						features[4] = 1
					if ("west" in i):
						features[5] = 1
		
					print("{} : {}".format(modelname, features))
					modelpath = "./Minecraft/assets/minecraft/models/block/" + modelname + ".json"
					json_model_data = open(modelpath).read()
				
					model_data = json.loads(json_model_data);
		
					for i in model_data["textures"]:
						texturepath = "./Minecraft/assets/minecraft/textures/{}.png".format(model_data["textures"][i])
						print(misc.imread(texturepath).mean(axis=(0,1))/256)
		
			except:
				pass

class MinecraftBlockSetLoader(TileSetLoader):
	def __init__(self,)