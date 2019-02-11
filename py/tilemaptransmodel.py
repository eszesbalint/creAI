import sys
import os
#sys.path.insert(0, '/content/drive/My Drive/creAI')

from Preprocessing import getVaeTrainingDataFromSchematic

import tensorflow as tf
from keras.layers import Lambda, Input, Dense, MaxPooling3D, Reshape, Conv3D, Conv3DTranspose, Activation
from keras.models import Model
from keras.losses import mse, binary_crossentropy, categorical_crossentropy
from keras.activations import softmax
from keras import backend as K
from keras.optimizers import Adagrad, RMSprop, Adam

import numpy as np

from vaemodel import CreAIVaeModel

class CreAITileMapTransformationModel(object):
    def __init__(self, weights_src = 'trans.h5', training_data_shape = (None,5,5,5,2,256)):
        weights_src = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'trained_models', weights_src)
        vae_model = CreAIVaeModel()
        decoder = vae_model.models['decoder']
        latent_dim = vae_model.latent_dim

        input_shape = (10, 10, 10, 1)

        input = Input(shape=input_shape, name='transformation_input')
        x = Conv3D(16, (2,2,2), padding='same', activation='relu')(input)
        x = Conv3D(32, (5,5,5), padding='same', activation='relu')(x)
        x = Conv3D(64, (5,5,5), padding='same', strides=5, activation='relu')(x)
        x = Conv3D(16, (2,2,2), padding='same', activation='relu')(x)
        #x = Conv3DTranspose(latent_dim, (5,5,5), strides=5, activation='relu')(x)
        x = Lambda(
            lambda x: tf.map_fn(
                lambda x: tf.concat(
                    tf.unstack(
                        tf.map_fn(
                            lambda x: tf.concat(
                                tf.unstack(
                                    tf.map_fn(
                                        lambda x: tf.concat(
                                            tf.unstack(
                                                decoder(x)
                                            ),
                                        -3),
                                    x)
                                ),
                            -4),
                        x)
                    ),
                -5),
            x), name='apply_decoder')(x)

        #x = Lambda(lambda x: tf.concat(tf.unstack(tf.concat(tf.unstack(tf.concat(tf.unstack(x),-2)),-3)),-4))(x)
        #output = decoder(x)

        trans = Model(input, x, name='tilemap_transformation_model')
        trans.summary(line_length=150)

        predict = K.function([input], [x], updates=trans.state_updates)
        #result = predict([np.zeros((1,50,50,50,1))])

        #print(np.asarray(result).shape)
        self.models={'trans':trans}
        self.eval = predict

    #def train(self, training_data_filename, batch_size = 64, epochs = 1000):
    #    training_data = getVaeTrainingDataFromSchematic(training_data_filename)
    #    self.models['vae'].fit(training_data, epochs=epochs, batch_size=batch_size)
    #    self.models['vae'].save_weights('/content/drive/My Drive/creAI/vae.h5')

    def generate(self):
        return np.argmax(self.eval([np.zeros((1,10,10,10,1))]),axis=-1)[0][0].tolist()
