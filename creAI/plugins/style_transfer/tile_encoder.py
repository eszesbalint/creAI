import os

import numpy as np

import tensorflow as tf

from tensorflow.keras import backend as K
from tensorflow.keras.layers import (Layer, Dense)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam


import creAI.globals


class Tile_Encoder(Layer):
    def __init__(self, input_dim, output_dim=8, intermediate_dim=16,
                 name='tile_encoder', **kwargs):
        super(Tile_Encoder, self).__init__(name=name, **kwargs)
        self.intermediate_layer = Dense(intermediate_dim, input_shape=(input_dim,), activation='relu')
        self.mean = Dense(output_dim)
        self.log_var = Dense(output_dim)

    def call(self, inputs):
        output = self.intermediate_layer(inputs)
        mean = self.mean(output)
        log_var = self.log_var(output)
        return mean, log_var, self._sampling([mean, log_var])

    @staticmethod
    def _sampling(args):
        mean, log_var = args
        batch = tf.shape(mean)[0]
        dim = tf.shape(mean)[1]
        epsilon = K.random_normal(shape=(batch, dim), mean=0., stddev=1.)
        return mean + tf.exp(log_var / 2) * epsilon


class Tile_Decoder(Layer):
    def __init__(self, input_dim, output_dim, intermediate_dim=16,
                 name='tile_decoder', **kwargs):
        super(Tile_Decoder, self).__init__(name=name, **kwargs)
        self.intermediate_layer = Dense(intermediate_dim, input_shape=(input_dim,), activation='relu')
        self.output_layer = Dense(output_dim, input_shape=(intermediate_dim,), activation='sigmoid')

    def call(self, inputs):
        output = self.intermediate_layer(inputs)
        return self.output_layer(output)


class Tile_VAE(Model):

    def __init__(self, output_dim, intermediate_dim=64, latent_dim=32,
                 name='tile_vae', **kwargs):
        super(Tile_VAE, self).__init__(name=name, **kwargs)
        self.output_dim = output_dim
        self.latent_dim = latent_dim
        self.encoder = Tile_Encoder(output_dim, output_dim=latent_dim,
                                    intermediate_dim=intermediate_dim)
        self.decoder = Tile_Decoder(latent_dim, output_dim,
                                    intermediate_dim=intermediate_dim)

    def call(self, inputs):
        mean, log_var, code = self.encoder(inputs)
        kl_divergence = 0.5 * tf.reduce_mean(
            tf.exp(log_var) + tf.square(mean) - 1. - log_var
        )
        self.add_loss(kl_divergence)
        return self.decoder(code)


