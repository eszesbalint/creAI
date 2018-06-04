import re

def variantToDict(variant):
	if isinstance(variant, basestring):
		return dict(re.findall(r'([a-z]+)=?([a-z0-9]*)', variant))
	elif isinstance(variant, dict):
		return variant

def compareVariants(variant1,variant2):
	unmatched_flags = set(variantToDict(variant1).items()) ^ set(variantToDict(variant2).items())
	return (len(unmatched_flags) == 0)

class MinecraftBlockID:
	def __init__(self, id = None, data = None, name = None, variant = None):
		if isinstance(name, basestring) and variant is not None:
			self.name = name
			if isinstance(variant, dict):
				self.variant = variant
			elif isinstance(variant, basestring):
				self.variant = variantToDict(variant)
		elif isinstance(id, int) and isinstance(data, int):
			if id == 0:
				self.name = "air"
				self.variant = {'normal': ''}
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
				self.variant = {'normal': ''}
			if id == 2:
				self.name = "grass"
				self.variant = {'normal': ''}
			if id == 3:
				self.name = [
					"dirt",
					"coarse_dirt",
					"podzol"
				][data]
				self.variant = {'normal': ''}
			if id == 4:
				self.name = "cobblestone"
				self.variant = {'normal': ''}
			if id == 5:
				self.name = [
					"oak_planks",
					"spurce_planks",
					"birch_planks",
					"jungle_planks",
					"acacia_planks",
					"dark_oak_planks"
				][data]
				self.variant = {'normal': ''}
			if id == 6:
				self.name = [
					"oak_sapling",
					"spurce_sapling",
					"birch_sapling",
					"jungle_sapling",
					"acacia_sapling",
					"dark_oak_sapling"
				][data]
				self.variant = {'normal': ''}
			if id == 7:
				self.name = "bedrock"
				self.variant = {'normal': ''}
			if id == 12:
				self.name = [
					"sand",
					"red_sand"
				][data]
				self.variant = {'normal': ''}
			if id == 13:
				self.name = "gravel"
				self.variant = {'normal': ''}
			if id == 14:
				self.name = "gold_ore"
				self.variant = {'normal': ''}
			if id == 15:
				self.name = "iron_ore"
				self.variant = {'normal': ''}
			if id == 16:
				self.name = "coal_ore"
				self.variant = {'normal': ''}
			if id == 17:
				if (int(format(data,'04b')[-4:-2],2) < 3):
					self.name = [
						"oak_log",
						"spurce_log",
						"birch_log",
						"jungle_log"
					][int(format(data,'04b')[-2:],2)]
					self.variant = [
						{"axis":"y"},
						{"axis":"z"},
						{"axis":"x"}
					][int(format(data,'04b')[-4:-2],2)]
				else:
					self.name = [
						"oak_bark",
						"spurce_bark",
						"birch_bark",
						"jungle_bark"
					][int(format(data,'04b')[-2:],2)]
					self.variant = {'normal': ''}
			if id == 18:
				self.name = [
					"oak_leaves",
					"spurce_leaves",
					"birch_leaves",
					"jungle_leaves"
				][int(format(data,'04b')[-2:],2)]
				self.variant = {'normal': ''}
			if id == 19:
				self.name = [
					"sponge",
					"wet_sponge"
				][data]
				self.variant = {'normal': ''}
			if id == 20:
				self.name = "glass"
				self.variant = {'normal': ''}
			if id == 21:
				self.name = "lapis_ore"
				self.variant = {'normal': ''}
			if id == 22:
				self.name = "lapis_block"
				self.variant = {'normal': ''}
			if id == 23:
				self.name = "dispenser"
				self.variant = [
					{"facing":"down"},
					{"facing":"up"},
					{"facing":"north"},
					{"facing":"south"},
					{"facing":"west"},
					{"facing":"east"}
				][int(format(data,'04b')[-3:],2)]
			if id == 24:
				self.name = [
					"sandstone",
					"chiseled_sandstone",
					"smooth_sandstone"
				][data]
				self.variant = {'normal': ''}
			if id == 25:
				self.name = 'noteblock'
				self.variant = {'normal': ''}

	def getID(self,version = 'new'):
		if version == 'new':
			return (self.name,self.variant)
		elif version == 'old':
			return None

