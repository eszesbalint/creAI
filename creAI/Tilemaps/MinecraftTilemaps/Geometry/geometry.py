from creAI.Tilemaps.MinecraftTilemaps import *
import numpy as np
import copy
from PIL import Image

blockstates_folder_path = os.path.join(
	os.path.dirname(os.path.abspath(__file__)),
	'models', 
	'1.14.2',
	'1.14.2',
	'assets',
	'minecraft',
	'blockstates'
)
blockmodels_folder_path = os.path.join(
	os.path.dirname(os.path.abspath(__file__)),
	'models', 
	'1.14.2',
	'1.14.2',
	'assets',
	'minecraft',
	'models',
	'block'
)
blocktextures_folder_path = os.path.join(
	os.path.dirname(os.path.abspath(__file__)),
	'models', 
	'1.14.2',
	'1.14.2',
	'assets',
	'minecraft',
	'textures',
	'block'
)

def get_model_json(tile):
	
	
	name = tile.id_object.value[0].split(':')[1]
	variant = tile.id_object.value[1]
	json_data = open(os.path.join(blockstates_folder_path, name + '.json')).read()
	data = json.loads(json_data)
	modelname = ''
	if 'multipart' in data:
		if isinstance(data['multipart'][0]['apply'], list):
			modelname = data['multipart'][0]['apply'][0]['model'].split('/')[-1]
		elif isinstance(data['multipart'][0]['apply'], dict):
			modelname = data['multipart'][0]['apply']['model'].split('/')[-1]
	elif 'variants' in data:
		#Find the coresponding variant in json file
		#for v in data['variants']:
		#    if v == variant:
		#        if isinstance(data['variants'][v], list):
		#            modelname = data['variants'][v][0]['model'].split('/')[-1]
		#        elif isinstance(data['variants'][v], dict):
		#            modelname = data['variants'][v]['model'].split('/')[-1]

		#Find the coresponding variant in json file, allows imperfect matches
		max_matching_arguments = 0
		max_key = ''
		for v in data['variants']:
			matching_arguments = 0
			for arg in v.split(','):
				if arg in variant.split(','):
					matching_arguments += 1
			if matching_arguments > max_matching_arguments:
				max_matching_arguments = matching_arguments
				max_key = v

		if isinstance(data['variants'][max_key], list):
			modelname = data['variants'][max_key][0]['model'].split('/')[-1]
		elif isinstance(data['variants'][max_key], dict):
				modelname = data['variants'][max_key]['model'].split('/')[-1]

	modelpath = os.path.join(blockmodels_folder_path, modelname + '.json')
	json_model_data = open(modelpath).read()
	model_data = json.loads(json_model_data)
 
	#for i in model_data['textures']:
	#    texturepath = path + TEXTURES + model_data['textures'][i] + '.png'
	#    self._textures.append(misc.imread(texturepath,mode='RGBA'))
	textures = {}
	if 'textures' in model_data:
		textures = model_data['textures']
	while 'elements' not in model_data:
		if 'parent' in model_data:
			modelname = model_data['parent'].split('/')[-1]
			modelpath = os.path.join(blockmodels_folder_path, modelname + '.json')
			json_model_data = open(modelpath).read()
			model_data = json.loads(json_model_data)
			if 'textures' in model_data:
				for key, value in model_data['textures'].items():
					textures[key] = value
					if '#' in value:
						textures[key] = textures[value[1:]]
		else:
			return None
			break

	model_data['textures'] = textures
	#print(model_data)
	return model_data


def get_box_geometry(from_, to, face_colors):
	v = [None		,
		[to[0]		, to[1]		, to[2]		],
		[to[0]		, from_[1]	, to[2]		],
		[to[0]		, to[1]		, from_[2]		],
		[to[0]		, from_[1]	, from_[2]		],
		[from_[0]	, to[1]		, to[2]		],
		[from_[0]	, from_[1]	, to[2]		],
		[from_[0]	, to[1]		, from_[2]		],
		[from_[0]	, from_[1]	, from_[2]		]
	]
	f = [
		[v[1], v[3], v[5]],
		[v[4], v[8], v[3]],
		[v[8], v[6], v[7]],
		[v[6], v[8], v[2]],
		[v[2], v[4], v[1]],
		[v[6], v[2], v[5]],
		[v[3], v[7], v[5]],
		[v[8], v[7], v[3]],
		[v[6], v[5], v[7]],
		[v[8], v[4], v[2]],
		[v[4], v[3], v[1]],
		[v[2], v[1], v[5]]
	]
	n = [None,
		[0.0000, 1.0000, 0.0000],
		[0.0000, 0.0000, 1.0000],
		[-1.0000, 0.0000, 0.0000],
		[0.0000, -1.0000, 0.0000],
		[1.0000, 0.0000, 0.0000],
		[0.0000, 0.0000, -1.0000]
	]
	fn = [
		[n[1], n[1], n[1]],
		[n[2], n[2], n[2]],
		[n[3], n[3], n[3]],
		[n[4], n[4], n[4]],
		[n[5], n[5], n[5]],
		[n[6], n[6], n[6]],
		[n[1], n[1], n[1]],
		[n[2], n[2], n[2]],
		[n[3], n[3], n[3]],
		[n[4], n[4], n[4]],
		[n[5], n[5], n[5]],
		[n[6], n[6], n[6]]
	]
	c = [None,
		face_colors['up'],
		face_colors['south'],
		face_colors['west'],
		face_colors['down'],
		face_colors['east'],
		face_colors['north'],
	]
	fc = [
		[c[1], c[1], c[1]],
		[c[2], c[2], c[2]],
		[c[3], c[3], c[3]],
		[c[4], c[4], c[4]],
		[c[5], c[5], c[5]],
		[c[6], c[6], c[6]],
		[c[1], c[1], c[1]],
		[c[2], c[2], c[2]],
		[c[3], c[3], c[3]],
		[c[4], c[4], c[4]],
		[c[5], c[5], c[5]],
		[c[6], c[6], c[6]]
	]

	return np.array([f, fn, fc, np.zeros(shape = np.array(f).shape)])

def tile_to_geometry(tile):

	model = get_model_json(tile)
	if model is None:
		return None
	geometries = []
	for element in model['elements']:
		from_ = np.array(element['from']) / 16
		to = np.array(element['to']) / 16

		face_colors = {'up':[1,1,1],'down':[1,1,1],'east':[1,1,1],'west':[1,1,1],'north':[1,1,1],'south':[1,1,1]}
		for face in element['faces']:
			texture_id = element['faces'][face]['texture'][1:]
			texture_path = os.path.join(blocktextures_folder_path, model['textures'][texture_id].split('/')[1] + '.png')
			img = Image.open(texture_path).convert('RGB')
			face_colors[face] = np.average(img, axis = (0, 1))[:3]/256

		geometries += [get_box_geometry(from_, to, face_colors)]
		
	geometries = np.concatenate(geometries, axis = 1)
	return geometries

def tilemap_to_geometry(tilemap):
	palette = list(set(tilemap.flat))
	tile_geometries = dict(zip(palette, [tile_to_geometry(tile) for tile in palette]))
	air = MinecraftTile(MinecraftID(('minecraft:air','')))

	geometries = [
		tile_geometries[t] + np.array([i,[0,0,0],[0,0,0],[0,0,0]]).reshape(4,1,1,3) 
		for i, t in np.ndenumerate(tilemap) 
		if t != air and tile_geometries[t] is not None
	]

	return np.concatenate(geometries, axis = 1)
	
	


