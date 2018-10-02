from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from keras.layers import Lambda, Input, Dense
from keras.models import Model
from keras.datasets import mnist
from keras.losses import mse, binary_crossentropy
from keras import backend as K
from keras.optimizers import Adagrad, RMSprop, Adam

import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

from PIL import Image
from Preprocessing import getCells


# reparameterization trick
# instead of sampling from Q(z|X), sample eps = N(0,I)
# z = z_mean + sqrt(var)*eps
def sampling(args):
    """Reparameterization trick by sampling fr an isotropic unit Gaussian.

    # Arguments:
        args (tensor): mean and log of variance of Q(z|X)

    # Returns:
        z (tensor): sampled latent vector
    """

    z_mean, z_log_var = args
    batch = K.shape(z_mean)[0]
    dim = K.int_shape(z_mean)[1]
    # by default, random_normal has mean=0 and std=1.0
    epsilon = K.random_normal(shape=(batch, dim))
    return z_mean + K.exp(0.5 * z_log_var) * epsilon


image = Image.open('bitmap.bmp')
data = np.asarray( image, dtype="float32" )[:,:,0].reshape((32,32,1))/256
cell_size = (5,5,1)
x_train = getCells(data,cell_size)


image_size = x_train.shape[1]
original_dim = image_size * image_size
x_train = np.reshape(x_train, [-1, original_dim])

# network parameters
input_shape = (original_dim, )
intermediate_dim = 16
batch_size = 6
latent_dim = 4
epochs = 1000

# VAE model = encoder + decoder
# build encoder model
inputs = Input(shape=input_shape, name='encoder_input')
x = Dense(intermediate_dim, activation='relu')(inputs)
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
outputs = Dense(original_dim, activation='sigmoid')(x)

# instantiate decoder model
decoder = Model(latent_inputs, outputs, name='decoder')
decoder.summary()


# instantiate VAE model
outputs = decoder(encoder(inputs)[2])
vae = Model(inputs, outputs, name='vae_mlp')


grid_size = (10,10,1)
grid_inputs = [[[Input(shape=(latent_dim,)) for i in range(grid_size[2])] for j in range(grid_size[1])] for k in range(grid_size[0])]
grid_outputs = [[[decoder(grid_inputs[k][j][i]) for i in range(grid_size[2])] for j in range(grid_size[1])] for k in range(grid_size[0])]
overlapping_model = Model([grid_inputs[k][j][i] for i in range(grid_size[2]) for j in range(grid_size[1]) for k in range(grid_size[0])],[grid_outputs[k][j][i] for i in range(grid_size[2]) for j in range(grid_size[1]) for k in range(grid_size[1])], name='overlapping_model')




def plot_results(model,cell_data):

    


    filename = "digits_over_latent.png"
    # display a 30x30 2D manifold of digits
    n = 10
    digit_size = 3
    figure = np.zeros((digit_size * n, digit_size * n,3))
    # linearly spaced coordinates corresponding to the 2D plot
    # of digit classes in the latent space
    grid_x = np.linspace(-3, 3, n)
    grid_y = np.linspace(-3, 3, n)[::-1]
    cells = np.asarray(model.predict(cell_data)).reshape((grid_size[0],grid_size[1],grid_size[2],cell_size[0],cell_size[1],cell_size[2]))
    for i,j,k in grid_iterator(grid_size):
            x_decoded = cells[j][i][k]
            digit = x_decoded[1:4,1:4,0].reshape(digit_size, digit_size,1)*np.ones((digit_size,digit_size,3))
            figure[i * digit_size: (i + 1) * digit_size,
                   j * digit_size: (j + 1) * digit_size,:] = digit

    plt.figure(figsize=(10, 10))
    start_range = digit_size // 2
    end_range = n * digit_size + start_range + 1
    pixel_range = np.arange(start_range, end_range, digit_size)
    sample_range_x = np.round(grid_x, 1)
    sample_range_y = np.round(grid_y, 1)
    plt.xticks(pixel_range, sample_range_x)
    plt.yticks(pixel_range, sample_range_y)
    plt.xlabel("z[0]")
    plt.ylabel("z[1]")
    plt.imshow(figure, cmap='Greys_r')
    plt.savefig(filename)
    plt.show()

def calc_overlapping_area(cell_size,direction,offset):
    direction_vec = [d * o for d, o in zip(direction,offset)]
    ax1, ay1, az1 = (0, 0, 0)
    ax2, ay2, az2 = cell_size
    bx1, by1, bz1 = direction_vec
    bx2, by2, bz2 = [c + d for c, d in zip(cell_size,direction_vec)]
    #calculate starting indicies
    x = max(ax1, bx1)
    y = max(ay1, by1)
    z = max(az1, bz1)
    #calculate size
    sx = min(ax2, bx2) - max(ax1, bx1)
    sy = min(ay2, by2) - max(ay1, by1)
    sz = min(az2, bz2) - max(az1, bz1)

    #returning starting indicies and size
    return ((x,y,z),(sx,sy,sz))

def calc_overlapping_area_both(cell_size,direction,offset):
    return (calc_overlapping_area(cell_size,direction,offset), calc_overlapping_area(cell_size,(-direction[0],-direction[1],-direction[2]),offset))

def direction_generator(index,grid_size):
    i, j, k = index
    return [(a-1,b-1,c-1) for c in range(3) if 0<=k+c-1<grid_size[2] for b in range(3) if 0<=j+b-1<grid_size[1] for a in range(3) if (a-1 or b-1 or c-1) and 0<=i+a-1<grid_size[0]]

def grid_iterator(grid_size):
    return [(i,j,k) for k in range(grid_size[2]) for j in range(grid_size[1]) for i in range(grid_size[0])]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    help_ = "Load h5 model trained weights"
    parser.add_argument("-w", "--weights", help=help_)
    help_ = "Use mse loss instead of binary cross entropy (default)"
    parser.add_argument("-m",
                        "--mse",
                        help=help_, action='store_true')
    args = parser.parse_args()
    models = (encoder, decoder, overlapping_model)

    # VAE loss = mse_loss or xent_loss + kl_loss
    if args.mse:
        reconstruction_loss = mse(inputs, outputs)
    else:
        reconstruction_loss = binary_crossentropy(inputs,
                                                  outputs)

    reconstruction_loss *= original_dim
    kl_loss = 1 + z_log_var - K.square(z_mean) - K.exp(z_log_var)
    kl_loss = K.sum(kl_loss, axis=-1)
    kl_loss *= -0.5
    vae_loss = K.mean(reconstruction_loss + kl_loss)
    vae.add_loss(vae_loss)
    vae.compile(optimizer=Adam(lr=0.001))
    vae.summary()

    offset = (3,3,3)
    overlapping_loss = 0
    mean_loss = 0
    for i,j,k in grid_iterator(grid_size):
        for direction in direction_generator((i,j,k),grid_size):
            (a_start, a_size), (b_start, b_size) = calc_overlapping_area_both(cell_size,direction,offset)
            l, m, n = (i+direction[0],j+direction[1],k+direction[2])
            overlapping_loss += K.mean(
                    K.square(
                        tf.slice(K.reshape(grid_outputs[i][j][k],(image_size,image_size,1)),a_start,a_size) - 
                        tf.slice(K.reshape(grid_outputs[l][m][n],(image_size,image_size,1)),b_start,b_size)
                    )
                )
        mean_loss += grid_inputs[i][j][k]
    mean_loss /= len(grid_inputs)
    mean_loss = K.mean(K.square(mean_loss))

    grid_loss = overlapping_loss + mean_loss

    overlapping_model.add_loss(grid_loss)
    overlapping_model.compile(optimizer=Adam(lr=0.001))
    overlapping_model.summary()

    if args.weights:
        vae = vae.load_weights(args.weights)
    else:
        # train the autoencoder
        vae.fit(x_train,
                epochs=epochs,
                batch_size=batch_size)
        vae.save_weights('vae_mlp_mnist.h5')

    test_input = [np.asarray([np.random.normal() for n in range(latent_dim)]).reshape((1,latent_dim)) for i in range(grid_size[0]*grid_size[1]*grid_size[2])]
    plot_results(overlapping_model, test_input)
    grad = K.gradients(grid_loss,overlapping_model.input)
    grad_fn = K.function(overlapping_model.input, grad)
    loss_fn = K.function(overlapping_model.input, [grid_loss])

    generation_steps = 10000
    lr = 0.01
    for n in range(generation_steps):
        grads = grad_fn(test_input)
        losses = loss_fn(test_input)
        test_input = [i - g * lr for i, g in zip(test_input,grads)]
        print('Step: {} Loss: {}'.format(n,losses))
    plot_results(overlapping_model, test_input)
    #print(grad_fn(test_input))
    #print(grad_fn(test_input))
    #print(grad_fn(test_input))
    
