import sys, os 
CURRENT_DIR = os.path.dirname(__file__)
sys.path.insert(0, CURRENT_DIR)
import nbt
import Preprocessing as prep

import tensorflow as tf
from keras.layers import Lambda, Input, Dense, Flatten, Reshape, Conv3D, Conv3DTranspose, Activation
from keras.models import Model
from keras.losses import mse, binary_crossentropy, categorical_crossentropy
from keras.activations import softmax
from keras import backend as K
from keras.optimizers import Adagrad, RMSprop, Adam

import numpy as np

##############################################
# Variational autoencoder part               #
##############################################

#x_train = np.zeros((sliced_blocks.shape[0],sliced_blocks.shape[1],sliced_blocks.shape[2],sliced_blocks.shape[3],2,256))

x_train = prep.getVaeTrainingDataFromSchematic("middelshus.schematic")

print x_train.shape
original_dim = (x_train.shape[1],x_train.shape[2],x_train.shape[3],x_train.shape[4],x_train.shape[5])

flattened_dim = x_train.shape[1]*x_train.shape[2]*x_train.shape[3]*x_train.shape[4]*x_train.shape[5]

def sampling(args):
    z_mean, z_log_var = args
    batch = K.shape(z_mean)[0]
    dim = K.int_shape(z_mean)[1]
    # by default, random_normal has mean=0 and std=1.0
    epsilon = K.random_normal(shape=(batch, dim))
    return z_mean + K.exp(0.5 * z_log_var) * epsilon
  
def softMaxAxis5(x):
    return softmax(x,axis=5)
  
# network parameters
input_shape = (x_train.shape[1],x_train.shape[2],x_train.shape[3],x_train.shape[4],x_train.shape[5], )
intermediate_dim = 64
batch_size = 64
latent_dim = 16
epochs = 1000

# VAE model = encoder + decoder
# build encoder model
inputs = Input(shape=input_shape, name='encoder_input')

x = Reshape(((x_train.shape[1],x_train.shape[2],x_train.shape[3],x_train.shape[4]*x_train.shape[5], )))(inputs)
x = Conv3D(64, (3,3,3), input_shape = (x_train.shape[1],x_train.shape[2],x_train.shape[3],x_train.shape[4]*x_train.shape[5]))(x)

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

#vae.fit(x_train, epochs=epochs, batch_size=batch_size)
#vae.save_weights('/content/drive/My Drive/creAI/vae.h5')
vae = vae.load_weights('/content/drive/My Drive/creAI/vae.h5')

##############################################
# Transformer part                           #
##############################################


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