import os

import numpy as np

from tensorflow.keras import backend as K
from tensorflow.keras.layers import (Dense, GaussianNoise,
                                     Input, Lambda, BatchNormalization, Activation)
from tensorflow.keras.losses import mean_squared_error, binary_crossentropy
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

from kerastuner.tuners import RandomSearch
from kerastuner import HyperModel

from sklearn.manifold import TSNE

import creAI.globals


class VAE_Hyper_Model(HyperModel):
    def __init__(self, input_size, latent_dim):
        self.input_size = input_size
        self.latent_dim = latent_dim

    def build(self, hyper_parameters):
        input_vector = Input(shape=(self.input_size,))
        intermadiate_dim = self.latent_dim * 2

        encode_1 = Dense(intermadiate_dim, use_bias=False)(input_vector)
        encode_1 = BatchNormalization()(encode_1)
        encode_1 = Activation('relu')(encode_1)

        encode_2 = Dense(self.latent_dim, use_bias=False)(encode_1)
        encode_2 = BatchNormalization()(encode_2)
        encode_2 = Activation('relu')(encode_2)

        mean = Dense(self.latent_dim, name='mean',
                     activation='linear')(encode_2)
        log_var = Dense(self.latent_dim, name='log_var',
                        activation='linear')(encode_2)

        latent_vector = Lambda(self._sampling, output_shape=(
            self.latent_dim,), name='z')([mean, log_var])

        latent_input_vector = Input(shape=(self.latent_dim,))
        decode_1 = Dense(intermadiate_dim, use_bias=False)(latent_input_vector)
        decode_1 = BatchNormalization()(decode_1)
        decode_1 = Activation('relu')(decode_1)
        #decode_2 = Dense(256, activation='relu')(decode_1)
        decoded = Dense(self.input_size, use_bias=False)(decode_1)
        decoded = BatchNormalization()(decoded)
        decoded = Activation('sigmoid')(decoded)

        encoder = Model(input_vector, [mean, log_var, latent_vector])
        decoder = Model(latent_input_vector, decoded)
        autoencoder = Model(input_vector, decoder(encoder(input_vector)[2]))

        autoencoder.add_loss(
            self._vae_loss(input_vector, decoder(
                encoder(input_vector)[2]), mean, log_var)
        )
        autoencoder.compile(
            optimizer=Adam(
                hyper_parameters.Choice('lr', values=[0.1, 0.01, 0.001, 0.001])
            ),
            metrics=['accuracy'],
        )

        return autoencoder

    @staticmethod
    def _sampling(args):
        mean, log_var = args
        batch = K.shape(mean)[0]
        dim = K.int_shape(mean)[1]
        epsilon = K.random_normal(shape=(batch, dim), mean=0., stddev=1.)
        return mean + K.exp(log_var / 2) * epsilon

    @staticmethod
    def _kl_divergence(mean, log_var):
        return 0.5 * K.sum(
            K.exp(log_var) + K.square(mean) - 1. - log_var,
            axis=-1,
        )

    def _reconstruction_loss(self, expected_output, output):
        return mean_squared_error(expected_output, output) * self.input_size

    def _vae_loss(self, expected_output, output, mean, log_var):
        return K.mean(self._reconstruction_loss(expected_output, output)
                      + self._kl_divergence(mean, log_var))

    @classmethod
    def train(cls, training_data: np.ndarray, batch_size: int, epochs: int, latent_dim: int):

        input_size = training_data.shape[1]
        np.random.shuffle(training_data)
        training, val = training_data[:80, :], training_data[80:, :]

        hyper_parameter_tuner = RandomSearch(
            cls(input_size, latent_dim),
            objective='val_loss',
            max_trials=20,
            executions_per_trial=1,
            project_name=creAI.globals.gen_rand_id(10),
            directory=model_path,
        )
        hyper_parameter_tuner.search_space_summary()
        # autoencoder.fit(training_data, training_data,
        #                epochs=epochs, batch_size=batch_size)

        hyper_parameter_tuner.search(training, training,
                                     epochs=40, batch_size=batch_size, validation_data=(val, val))
        hyper_parameter_tuner.results_summary()

        tuned_model = hyper_parameter_tuner.get_best_models(num_models=1)[0]
        tuned_model.summary()
        tuned_model.fit(training, training,
                        epochs=epochs, batch_size=batch_size, validation_data=(val, val))

        return tuned_model
