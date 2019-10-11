import sys
import nbt
import id_mapper
import numpy as np 

NAME_TO_NUM = id_mapper.NamespaceID_To_NumericID()

class Schematic(nbt.TAG_Compound):


	@classmethod
	def loadFromNumpyArray(cls, array):
		pass

	def asNumpyArray(self):
		h = self["Height"].payload
		l = self["Length"].payload
		w = self["Width"].payload

		block_data = self["BlockData"].payload
		block_numeric_ids = np.zeros((w,h,l)).astype(np.uint16)
		data_offset = 0

		for block in range(h*l*w):
			bytess = []
			numeric_id = 0
			id_length = 0
			while True:
				next_byte = block_data[data_offset].payload
				next_byte -= next_byte & 128
				numeric_id = numeric_id | (next_byte<< id_length*7)
				id_length += 1
				if id_length > 5:
					raise Exception("id_length too big! (Possibly corrupted data)")
				if ((block_data[data_offset].payload & 128) != 128):
					data_offset += 1
					break

				data_offset += 1
			
			y = block / (w * l)
			z = (block % (w * l)) / w
			x = (block % (w * l)) % w

			block_numeric_ids[x,y,z] = numeric_id 

			if numeric_id > self["PaletteMax"].payload:
				raise ValueError("Palette ID {} at {} is bigger than PaletteMax {}".format(numeric_id, (x,y,z), self["PaletteMax"].payload))

		pipeline = id_mapper.IDMapper_Pipeline(
			pipeline=[
				id_mapper.PaletteID_To_NamespaceID(self["Palette"]),
				NAME_TO_NUM
				]
			)
		#mapper_1 = id_mapper.PaletteID_To_NamespaceID(self["Palette"])
		#mapper_2 = id_mapper.NamespaceID_To_NumericID()
		mapper = lambda x: pipeline[int(x)]
		mapping = np.vectorize(mapper)
		block_numeric_ids = mapping(block_numeric_ids)
		return block_numeric_ids.astype(np.uint16)

def load(file_name):
	root_tag = nbt.load(file_name)
	schem = Schematic()
	schem.name = root_tag.name
	schem._payload = root_tag.payload
	return schem

def main():
    schem = load(sys.argv[1])
    h,l,w = schem.asNumpyArray().shape
    np.set_printoptions(suppress=True, threshold=sys.maxsize)
    print np.unpackbits(schem.asNumpyArray().reshape((h,l,w,1)).byteswap().view(np.uint8), axis=-1)
    

if __name__ == '__main__':
    main()