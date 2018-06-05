INPUT_SIZE = 107
ENCODED_SIZE = 3

import numpy as np

import MinecraftBlock as MB

mbl = MB.MinecraftBlockSetLoader()
mbl.loadFromFile('./Minecraft')

x_train = mbl.toNumpyArray()

from keras.models import Model
from keras.layers import Dense,Input,GaussianNoise
from keras.losses import categorical_crossentropy
from keras.optimizers import SGD

#Implementing the autoencoder
input_vector = Input(shape=(INPUT_SIZE,))
#noise = GaussianNoise(0.01)(input_vector)

encode_1 = Dense(8,activation='relu')(input_vector)
encode_2 = Dense(5,activation='relu')(encode_1)
encoded = Dense(ENCODED_SIZE,activation='relu')(encode_2)

decode_1 = Dense(5,activation='relu')(encoded)
decode_2 = Dense(8,activation='relu')(decode_1)
decoded = Dense(INPUT_SIZE, activation='sigmoid')(decode_2)

autoencoder = Model(input_vector, decoded)
encoder = Model(input_vector, encoded)
encoded_input = Input(shape=(ENCODED_SIZE,))


autoencoder.compile(optimizer=SGD(lr=0.1, momentum=0.9, nesterov=True),loss='mean_squared_error')
autoencoder.fit(x_train,x_train,epochs=1000,batch_size=50)

#Saving the trained model
encoder.save('encoder.h5')
#decoder.save('decoder.h5')



