import numpy as np
import nbt

def getCells(input_array, cell_size):
	offset = (int(cell_size[0]/2),int(cell_size[1]/2),int(cell_size[2]/2))
	x,y,z = input_array.shape
	output_array = []
	for i in range(x-offset[0]*2):
		#if(i%cell_size[0]!=0): continue

		for j in range(y-offset[1]*2):
			#if(j%cell_size[1]!=0): continue

			for k in range(z-offset[2]*2):
				#if(k%cell_size[2]!=0): continue
				cell = input_array[
					i:i+2*offset[0]+1,
					j:j+2*offset[1]+1,
					k:k+2*offset[2]+1,
					]
				#if(not cell.sum()): continue
				output_array.append(cell)

	return np.asarray(output_array)

def getVaeTrainingDataFromSchematic(filename):
	filename = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'training_data', filename)
	file = nbt.load(filename)

	x = file.__getitem__(u'Width').value
	y = file.__getitem__(u'Height').value
	z = file.__getitem__(u'Length').value

	blocks = file.__getitem__(u'Blocks').value
	blocks = blocks.reshape(y,z,x)
	print len(blocks)

	data = file.__getitem__(u'Data').value
	data = data.reshape(y,z,x)
	print len(data)

	sliced_blocks = prep.getCells(blocks,(5,5,5))
	sliced_data = prep.getCells(data,(5,5,5))
	print sliced_data.shape,sliced_blocks.shape

	x_train = np.zeros((sliced_blocks.shape[0],sliced_blocks.shape[1],sliced_blocks.shape[2],sliced_blocks.shape[3],2,256))

	for n in range(sliced_blocks.shape[0]):
	  for i in range(sliced_blocks.shape[1]):
	    for j in range(sliced_blocks.shape[2]):
	      for k in range(sliced_blocks.shape[3]):
	        x_train[n,i,j,k,0,sliced_blocks[n,i,j,k]] = 1
	        x_train[n,i,j,k,1,sliced_data[n,i,j,k]] = 1
	return x_train

def getTransTrainingDataCuboids(num, shape):
	
