###############################################################
# AutoWiki                                                    #
# Created by: Eszes Balint (ebalint96) 2018                   #
###############################################################

from keras.models import load_model
import sys
import numpy as np
import json

encoder = load_model('encoder.h5')

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
#import mpld3

xs = []
ys = []
zs = []


colors = []

import MinecraftBlock as MB

mbl = MB.MinecraftBlockSetLoader()
mbl.loadFromFile('./Minecraft')

data = mbl.toNumpyArray()
labels = [block.minecraft_id.getID('new')[0] for block in mbl._set]

for i in range(data.shape[0]):
	
	#labels.append(file.read())

	v = encoder.predict(np.asarray([data[i]]))
	colors.append([data[i][0],data[i][1],data[i][2]])
	xs.append(v[0][0])
	ys.append(v[0][1])
	zs.append(v[0][2])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

colors = np.asarray(colors)[:, 0:4]
print colors

ax.scatter(xs,ys,zs,s=5,c=colors)

ax.grid(color='white', linestyle='solid')



#for i, txt in enumerate(labels):
#	if (i%2 == 0):
#		ax.annotate(txt, (xs[i],xs[i]))

plt.show()

#tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
#mpld3.plugins.connect(fig, tooltip)

#mpld3.save_html(fig,'wiki.html')

