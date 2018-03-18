import numpy as np
import nbt
import sys

window_size=(10,10,10)
offset = (int(window_size[0]/2),int(window_size[1]/2),int(window_size[2]/2))
tile_size=(10,10,10)

file = nbt.load(sys.argv[1])

x = file.__getitem__(u'Width').value
y = file.__getitem__(u'Height').value
z = file.__getitem__(u'Length').value

data = file.__getitem__(u'Blocks').value
data = data.reshape(y,z,x)

c=0
for i in range(y-offset[0]*2):
	if(i%tile_size[0]!=0): continue
	for j in range(z-offset[1]*2):
		if(j%tile_size[1]!=0): continue
		for k in range(x-offset[2]*2):
			if(k%tile_size[2]!=0): continue
			feature = data[
				i:i+2*offset[0]+1,
				j:j+2*offset[1]+1,
				k:k+2*offset[2]+1,
				]
			if(not feature.sum()):
				continue
			c+=1
			np.save("{}".format(c),feature)

print(c)

