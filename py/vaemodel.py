import sys
import os
#sys.path.insert(0, '/content/drive/My Drive/creAI')
import nbt
from Preprocessing import getVaeTrainingDataFromSchematic

import tensorflow as tf
from keras.layers import Lambda, Input, Dense, Flatten, Reshape, Conv3D, Conv3DTranspose, Activation
from keras.models import Model
from keras.losses import mse, binary_crossentropy, categorical_crossentropy
from keras.activations import softmax
from keras import backend as K
from keras.optimizers import Adagrad, RMSprop, Adam

import numpy as np



def sampling(args):
    z_mean, z_log_var = args
    batch = K.shape(z_mean)[0]
    dim = K.int_shape(z_mean)[1]
    # by default, random_normal has mean=0 and std=1.0
    epsilon = K.random_normal(shape=(batch, dim))
    return z_mean + K.exp(0.5 * z_log_var) * epsilon

def softMaxAxis5(x):
    return softmax(x,axis=5)

class CreAIVaeModel(object):
    def __init__(self, weights_src = 'vae.h5', training_data_shape = (None,5,5,5,2,256)):
        weights_src = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'trained_models', weights_src)
        # network parameters
        original_dim = (training_data_shape[1],training_data_shape[2],training_data_shape[3],training_data_shape[4],training_data_shape[5])

        flattened_dim = training_data_shape[1]*training_data_shape[2]*training_data_shape[3]*training_data_shape[4]*training_data_shape[5]

        input_shape = (training_data_shape[1],training_data_shape[2],training_data_shape[3],training_data_shape[4],training_data_shape[5], )
        intermediate_dim = 64

        latent_dim = 16


        # VAE model = encoder + decoder
        # build encoder model
        inputs = Input(shape=input_shape, name='encoder_input')

        x = Reshape(((training_data_shape[1],training_data_shape[2],training_data_shape[3],training_data_shape[4]*training_data_shape[5])))(inputs)
        x = Conv3D(64, (3,3,3), input_shape = (training_data_shape[1],training_data_shape[2],training_data_shape[3],training_data_shape[4]*training_data_shape[5]))(x)

        shape = K.int_shape(x)
        print K.int_shape(x), "<-----------------------"

        x = Flatten()(x)
        x = Dense(intermediate_dim, activation='relu')(x)
        z_mean = Dense(latent_dim, name='z_mean')(x)
        z_log_var = Dense(latent_dim, name='z_log_var')(x)

        # use reparameterization trick to push the sampling out as input
        # note that "output_shape" isn't necessary with the TensorFlow backend
        z = Lambda(sampling, output_shape=(latent_dim,), name='z')([z_mean, z_log_var])

        # instantiate encoder model
        encoder = Model(inputs, [z_mean, z_log_var, z], name='encoder')
        encoder.summary()


        # build decoder model
        latent_inputs = Input(shape=(latent_dim,), name='z_sampling')
        x = Dense(intermediate_dim, activation='relu')(latent_inputs)
        x = Dense(shape[1] * shape[2] * shape[3] * shape[4], activation='relu')(x)
        x = Reshape((shape[1], shape[2], shape[3], shape[4]))(x)
        x = Conv3DTranspose(64, (3,3,3), activation='relu', padding='same')(x)
        x = Conv3DTranspose(2*256, (3,3,3), activation='relu', padding='valid', )(x)
        print K.int_shape(x), "<-----------------------"
        #x = Dense(flattened_dim, activation=softMaxAxis5)(x)
        x = Reshape(input_shape)(x)
        outputs = Activation(softMaxAxis5)(x)

        # instantiate decoder model
        decoder = Model(latent_inputs, outputs, name='decoder')
        decoder.summary()


        # instantiate VAE model
        outputs = decoder(encoder(inputs)[2])
        vae = Model(inputs, outputs, name='vae_mlp')

        reconstruction_loss = categorical_crossentropy(inputs, outputs)

        kl_loss = 1 + z_log_var - K.square(z_mean) - K.exp(z_log_var)
        kl_loss = K.sum(kl_loss, axis=-1)
        kl_loss *= -0.5
        vae_loss = K.mean(K.sum(reconstruction_loss, axis=[1,2,3,4]) + kl_loss)

        vae.add_loss(vae_loss)
        vae.compile(optimizer=Adam(lr=0.001))
        vae.summary()


        vae = vae.load_weights(weights_src)
        self.models = {'decoder':decoder,'encoder':encoder,'vae':vae}
        self.latent_dim = latent_dim

    def train(self, training_data_filename, batch_size = 64, epochs = 1000):
        training_data = getVaeTrainingDataFromSchematic(training_data_filename)
        self.models['vae'].fit(training_data, epochs=epochs, batch_size=batch_size)
        self.models['vae'].save_weights('/content/drive/My Drive/creAI/vae.h5')

    def generate(self):
        return np.argmax(self.models['decoder'].predict(np.asarray([np.random.normal() for n in range(self.latent_dim)]).reshape((1,self.latent_dim))),axis=-1)[0].tolist()
