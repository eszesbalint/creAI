import json
import glob
import os
from scipy import misc

path = './Minecraft/assets/minecraft/blockstates/'
for filename in glob.glob(os.path.join(path, '*.json')):
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

