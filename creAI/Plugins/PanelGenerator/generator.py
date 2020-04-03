from creAI.Tilemaps.MinecraftTilemaps import *
import random
import numpy as np
import os


class Symbol():
	def __init__(self, name, x1, y1, z1, x2, y2, z2, **kwargs):
		self.name = name

		self.x1 = x1
		self.y1 = y1
		self.z1 = z1
		self.x2 = x2
		self.y2 = y2
		self.z2 = z2

		self.property = kwargs

	def __repr__(self):
		return "<{} [{} {} {}] [{} {} {}]>\n".format(self.name, self.x1, self.y1, self.z1, self.x2, self.y2, self.z2)

	def __eq__(self, other):
		return (self.name == other.name) and (self.x1 == other.x1)  and (self.y1 == other.y1)  and (self.z1 == other.z1) and (self.x2 == other.x2)  and (self.y2 == other.y2)  and (self.z2 == other.z2)

def is_overlapping(a, b, tangent = False):
	if tangent:
		return (a.x1 <= b.x2 and b.x1 <= a.x2 and a.y1 <= b.y2 and b.y1 <= a.y2 and a.z1 <= b.z2 and b.z1 <= a.z2)
	else:
		return (a.x1 < b.x2 and b.x1 < a.x2 and a.y1 < b.y2 and b.y1 < a.y2 and a.z1 < b.z2 and b.z1 < a.z2)

def is_overlapping_2d(a, b, tangent = False):
	if tangent:
		return (a.x1 <= b.x2 and b.x1 <= a.x2 and a.y1 <= b.y2 and b.y1 <= a.y2 )
	else:
		return (a.x1 < b.x2 and b.x1 < a.x2 and a.y1 < b.y2 and b.y1 < a.y2 )


def generate():
	elements_folder = os.path.join(os.path.dirname(__file__), "elements")
	pos_x = Schematic.load(os.path.join(elements_folder, "elements_+x.schem"))
	neg_x = Schematic.load(os.path.join(elements_folder, "elements_-x.schem"))
	pos_z = Schematic.load(os.path.join(elements_folder, "elements_+z.schem"))
	neg_z = Schematic.load(os.path.join(elements_folder, "elements_-z.schem"))
	elements = {
		"large_window" : {
			"+x" : [pos_x[0:2,0:4,0:5], (-2,0,0)],
			"-x" : [neg_x[2:4,0:4,0:5], (1,0,0)],
			"+z" : [pos_z[12:17,0:4,0:2], (0,0,-2)],
			"-z" : [neg_z[12:17,0:4,2:4], (0,0,1)]
		},
		"small_window" : {
			"+x" : [pos_x[0:2,0:4,5:9], (-2,0,0)],
			"-x" : [neg_x[2:4,0:4,5:9], (1,0,0)],
			"+z" : [pos_z[8:12,0:4,0:2], (0,0,-2)],
			"-z" : [neg_z[8:12,0:4,2:4], (0,0,1)]
		},
		"balcony" : {
			"+x" : [pos_x[0:4,0:4,12:17], (-2,0,0)],
			"-x" : [neg_x[0:4,0:4,12:17], (-1,0,0)],
			"+z" : [pos_z[0:5,0:4,0:4], (0,0,-2)],
			"-z" : [neg_z[0:5,0:4,0:4], (0,0,-1)]
		},
		"vent" : {
			"+x" : [pos_x[0:2,0:4,9:12], (-2,0,0)],
			"-x" : [neg_x[2:4,0:4,9:12], (1,0,0)],
			"+z" : [pos_z[5:8,0:4,0:2], (0,0,-2)],
			"-z" : [neg_z[5:8,0:4,2:4], (0,0,1)]
		},

	}


	width = random.randint(100, 200)
	length = random.randint(100, 200)
	tilemap = np.empty((width,40,length), dtype=object)
	tilemap[:,:,:] = MinecraftTile(MinecraftID(('minecraft:air','')))

	symbols = [Symbol('start', 0, 0, 0, tilemap.shape[0], tilemap.shape[1], tilemap.shape[2])]
	new_symbols = []
	removed_symbols = []

	floor_plans = []

	def rule1():
		nonlocal new_symbols
		nonlocal removed_symbols
		removed_symbols += [s]
		free_space = Symbol('free_space_1', s.x1, s.y1, s.z1, s.x2, s.y2, s.z2, axis = 'x', level = 0)
		new_symbols += [free_space]

	def rule2():
		nonlocal new_symbols
		nonlocal removed_symbols
		nonlocal floor_plans
		removed_symbols += [s]
		if (s.x2-s.x1 > 16) and (s.z2-s.z1 > 16):
			if s.property['axis'] == 'x':
				z1 = random.randint(s.z1, s.z2-16)
				x1 = s.x1
				z2 = z1 + 16
				x2 = s.x2
				floor_plan = Symbol('floor_plan', x1, 0, z1, x2, 0, z2, height = (10-s.property['level'])*4)
				new_symbols += [floor_plan]
				floor_plans += [floor_plan]
				free_space1 = Symbol('free_space', s.x1+16, 0, s.z1, x2-16, 0, z1, axis = 'z', level = s.property['level']+1)
				free_space2 = Symbol('free_space', x1+16, 0, z2, s.x2-16, 0, s.z2, axis = 'z', level = s.property['level']+1)
				new_symbols += [free_space1, free_space2]
			if s.property['axis'] == 'z':
				x1 = random.randint(s.x1, s.x2-16)
				z1 = s.z1
				x2 = x1 + 16
				z2 = s.z2
				floor_plan = Symbol('floor_plan', x1, 0, z1, x2, 0, z2, height = (10-s.property['level'])*4)
				floor_plans += [floor_plan]
				new_symbols += [floor_plan]
				free_space1 = Symbol('free_space', s.x1, 0, s.z1+16, x1, 0, z2-16, axis = 'x', level = s.property['level']+1)
				free_space2 = Symbol('free_space', x2, 0, z1+16, s.x2, 0, s.z2-16, axis = 'x', level = s.property['level']+1)
				new_symbols += [free_space1, free_space2]

	def rule3():
		nonlocal new_symbols
		nonlocal removed_symbols
		removed_symbols += [s]

	def rule4():
		nonlocal new_symbols
		nonlocal removed_symbols
		removed_symbols += [s]
		bottom_height = 5
		bottom = Symbol('bottom', s.x1, 0, s.z1, s.x2, bottom_height, s.z2)
		middle_height = bottom_height + ((s.property['height']-bottom_height)//4)*4
		middle = Symbol('middle', s.x1, bottom_height, s.z1, s.x2, middle_height, s.z2)

		new_symbols += [middle, bottom]

	def rule5():
		nonlocal new_symbols
		nonlocal removed_symbols
		nonlocal floor_plans
		removed_symbols += [s]
		if s.x2-s.x1 > s.z2-s.z1:
			facade1 = Symbol('facade', s.x1, s.y1, s.z1 - 1, s.x2, s.y2, s.z1, axis = 'z', facing = '-')
			facade2 = Symbol('facade', s.x1, s.y1, s.z2, s.x2, s.y2, s.z2 + 1, axis = 'z', facing = '+')
		else:
			facade1 = Symbol('facade', s.x1 - 1, s.y1, s.z1, s.x1, s.y2, s.z2, axis = 'x', facing = '-')
			facade2 = Symbol('facade', s.x2, s.y1, s.z1, s.x2 + 1, s.y2, s.z2, axis = 'x', facing = '+')

		new_symbols += [facade1, facade2]

	def rule6():
		nonlocal new_symbols
		nonlocal removed_symbols
		nonlocal floor_plans
		removed_symbols += [s]

		wall_strips = ['large_window_strip','balcony_strip','small_window_strip','vent_strip']
		wall_strip_widths = [5, 5, 4, 3]
		pattern = [random.choice(list(zip(wall_strips, wall_strip_widths))) for i in range(random.randint(3,8))]

		if s.property['axis'] == 'z':
			i = 0
			delta = 0
			while True:
				next_strip = pattern[i % len(pattern)]
				name = next_strip[0]
				width = next_strip[1]
				x1 = s.x1 + delta
				x2 = s.x1 + delta + width
				strip = Symbol(name, x1, s.y1, s.z1, x2, s.y2, s.z2, axis = 'z', facing = s.property['facing'])

				i += 1
				delta += width

				if x2 > s.x2:
					break

				is_not_overlapping = True
				for floor_plan in floor_plans:
					if is_overlapping_2d(strip, floor_plan):
						is_not_overlapping = False
				if is_not_overlapping:
					new_symbols += [strip]
		elif s.property['axis'] == 'x':
			i = 0
			delta = 0
			while True:
				next_strip = pattern[i % len(pattern)]
				name = next_strip[0]
				width = next_strip[1]
				z1 = s.z1 + delta
				z2 = s.z1 + delta + width
				strip = Symbol(name, s.x1, s.y1, z1, s.x2, s.y2, z2, axis = 'x', facing = s.property['facing'])

				i += 1
				delta += width

				if z2 > s.z2:
					break

				is_not_overlapping = True
				for floor_plan in floor_plans:
					if is_overlapping_2d(strip, floor_plan):
						is_not_overlapping = False
				if is_not_overlapping:
					new_symbols += [strip]

	def rule7():
		nonlocal new_symbols
		nonlocal removed_symbols
		nonlocal tilemap
		removed_symbols += [s]

		element = elements[s.name[:-6]][s.property['facing']+s.property['axis']]
		offset = np.array(element[1])
		parent_pos = np.array([s.x1, s.y1, s.z1])
		element_tilemap = element[0]

		for i in range(0, s.y2 - s.y1 - 4, 4):
			location = offset + parent_pos + np.array([0,i,0])
			x1 = location[0]
			y1 = location[1]
			z1 = location[2]
	
			x2 = x1 + element_tilemap.shape[0]
			y2 = y1 + element_tilemap.shape[1]
			z2 = z1 + element_tilemap.shape[2]
			tilemap[x1:x2,y1:y2,z1:z2] = element_tilemap

	def rule8():
		nonlocal new_symbols
		nonlocal removed_symbols
		nonlocal tilemap
		removed_symbols += [s]

		tilemap[s.x1:s.x2,s.y1:s.y2,s.z1:s.z2] = MinecraftTile(MinecraftID(('minecraft:stone','')))


	grammar = {
		"start" : [[1.0, rule1]],
		"free_space_1" : [[0.7, rule2]],
		"free_space" : [[0.7, rule2],[0.3, rule3]],
		"floor_plan" : [[1.0, rule4]],
		"middle" : [[1.0, rule5]],
		"facade" : [[1.0, rule6]],
		"large_window_strip" : [[1.0, rule7]],
		"balcony_strip" : [[1.0, rule7]],
		"small_window_strip" : [[1.0, rule7]],
		"vent_strip" : [[1.0, rule7]],
		"bottom" : [[1.0, rule8]]
	}

	

	
	while len(symbols):
		print(symbols)
		new_symbols = []
		removed_symbols = []
		for i, s in enumerate(symbols):
			rules = grammar[s.name]
			candidates = [rule[1] for rule in rules]
			probabilities = [rule[0] for rule in rules]
			picked_rule = np.random.choice(candidates, 1, probabilities)[0]
			picked_rule()
				
		
		for r_s in removed_symbols:
			symbols.remove(r_s)

		symbols += new_symbols

	return tilemap





