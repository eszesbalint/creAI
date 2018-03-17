import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import nbt
import sys


file = nbt.load(sys.argv[1])

x = file.__getitem__(u'Width').value
y = file.__getitem__(u'Height').value
z = file.__getitem__(u'Length').value

data = file.__getitem__(u'Blocks').value
data = data.reshape(y,z,x)







#fig = plt.figure()
#ax = fig.gca(projection='3d')
#ax.voxels(data,edgecolor='k')




plt.subplot(131)
plt.imshow(np.average(data,0), cmap='hot', interpolation='nearest', origin='lower')


plt.subplot(132)
plt.imshow(np.average(data,1), cmap='hot', interpolation='nearest', origin='lower')


plt.subplot(133)
plt.imshow(np.average(data,2), cmap='hot', interpolation='nearest', origin='lower')
plt.show()

