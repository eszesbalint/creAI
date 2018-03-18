import numpy as np
import nbt
import sys

window_size=(5,5,5)
offset = (int(window_size[0]/2),int(window_size[1]/2),int(window_size[2]/2))

file = nbt.load(sys.argv[1])

x = file.__getitem__(u'Width').value
y = file.__getitem__(u'Height').value
z = file.__getitem__(u'Length').value

data = file.__getitem__(u'Blocks').value
data = data.reshape(y,z,x)

c=0
for i in range(y-offset[0]*2):
	for j in range(z-offset[1]*2):
		for k in range(x-offset[2]*2):
			feature = data[
				i:i+2*offset[0]+1,
				j:j+2*offset[1]+1,
				k:k+2*offset[2]+1,
				]
			if(feature.sum()):
				c+=1

print(c)

