import numpy as np

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
	