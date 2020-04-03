from __future__ import print_function
import nbt
import tensorflow as tf

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense,Input,GaussianNoise
from tensorflow.keras.losses import categorical_crossentropy
from tensorflow.keras.optimizers import SGD

import numpy as np

class TileEncoder:
    def __init__(self, encoded_size):
        if encoded_size:
            self._encoded_size = encoded_size

    def train(self, tile_set):
        
        

        x_train_raw = [tile.toArray() for tile in tile_set]
        max_len = 0
        for x in x_train_raw:
            if len(x) > max_len:
                max_len = len(x)
        

        x_train = np.zeros(shape=(len(x_train_raw),max_len))
        for i, x in enumerate(x_train_raw):
            x_train[i,:len(x)] = x
        print(x_train)

        self._input_size = max_len

        #Implementing the autoencoder
        input_vector = Input(shape=(self._input_size,))
        noise = GaussianNoise(0.01)(input_vector)

        encode_1 = Dense(512,activation='relu')(noise)
        encode_2 = Dense(256,activation='relu')(encode_1)
        encode_3 = Dense(128,activation='relu')(encode_2)
        encoded = Dense(self._encoded_size)(encode_3)

        decode_1 = Dense(128,activation='relu')(encoded)
        decode_2 = Dense(256,activation='relu')(decode_1)
        decode_3 = Dense(512,activation='relu')(decode_2)
        decoded = Dense(self._input_size, activation='sigmoid')(decode_3)

        autoencoder = Model(input_vector, decoded)
        encoder = Model(input_vector, encoded)
        encoded_input = Input(shape=(self._encoded_size,))

        self.autoencoder = autoencoder
        self.encoder = encoder
        self.decoder = None

        self.autoencoder.compile(optimizer='adam',loss='categorical_crossentropy')
        self.autoencoder.fit(x_train,x_train,epochs=1000,batch_size=16)

    def encode(self, x):
        pass
    def decode(self, l):
        pass