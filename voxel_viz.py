import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import nbt
import sys


if(sys.argv[1].endswith('.schematic')):
	file = nbt.load(sys.argv[1])
	
	x = file.__getitem__(u'Width').value
	y = file.__getitem__(u'Height').value
	z = file.__getitem__(u'Length').value
	
	data = file.__getitem__(u'Blocks').value
	data = data.reshape(y,z,x)
elif(sys.argv[1].endswith('.npy')):
	data = np.load(sys.argv[1])

if(sys.argv[2]=="3d"):
	fig = plt.figure()
	ax = fig.gca(projection='3d')
	ax.voxels(data,edgecolor='k')
	plt.show()
elif(sys.argv[2]=="2d"):
	
	plt.subplot(221)
	plt.imshow(np.count_nonzero(data,0), cmap='Spectral', interpolation='nearest', origin='lower')


	plt.subplot(222)
	plt.imshow(np.count_nonzero(data,1), cmap='Spectral', interpolation='nearest', origin='lower')


	plt.subplot(223)
	plt.imshow(np.count_nonzero(data,2), cmap='Spectral', interpolation='nearest', origin='lower')
	plt.show()













