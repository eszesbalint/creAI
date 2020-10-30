from os import PathLike
from os.path import join
import tensorflow as tf
from tensorflow.keras.layers import Layer, Dense
from tensorflow.keras.models import load_model
from tensorflow.keras import Model, Input, Sequential
import tensorflow.keras.backend as K
tf.compat.v1.disable_eager_execution()

class Sampling(Layer):
    def call(self, inputs):
        z_mean, z_log_var = inputs
        batch = tf.shape(z_mean)[0]
        dim = tf.shape(z_mean)[1]
        epsilon = tf.keras.backend.random_normal(shape=(batch, dim))
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon

class VAE():
    def __init__(self, input_dim=None, latent_dim=None):
        self.input_dim = input_dim
        self.latent_dim = latent_dim

    def build(self):
        encoder_input = Input(self.input_dim)

        x = encoder_input
        #x = Dense(256,         activation='relu')(x)
        #x = Dense(128,         activation='relu')(x)
        #x = Dense(64,          activation='relu')(x)
        x = Dense(self.latent_dim,  activation='relu')(x)

        z_mean = Dense(self.latent_dim)(x)
        z_log_var = Dense(self.latent_dim)(x)
        z = Sampling()([z_mean, z_log_var])
        
        decoder_input = Input(self.latent_dim)

        x = decoder_input
        #x = Dense(64,         activation='relu')(x)
        #x = Dense(128,        activation='relu')(x)
        #x = Dense(256,        activation='relu')(x)
        x = Dense(self.input_dim,  activation='sigmoid')(x)

        decoder_output = x

        self.encoder = Model(encoder_input, [z_mean, z_log_var, z])
        self.decoder = Model(decoder_input, decoder_output)
        self.model = Model(encoder_input, self.decoder(self.encoder(encoder_input)))

    @classmethod
    def load(cls, pth: PathLike):
        vae = cls()
        vae.encoder = load_model(join(pth, 'encoder'))
        vae.decoder = load_model(join(pth, 'decoder'))
        vae.model = Model(vae.encoder.input, vae.decoder(vae.encoder(vae.encoder.input)))
        vae.input_dim = vae.encoder.input_shape[-1]
        vae.latent_dim = vae.decoder.input_shape[-1]
        return vae
    
    def save(self, pth: PathLike):
        self.encoder.save(join(pth, 'encoder'))
        self.decoder.save(join(pth, 'decoder'))




