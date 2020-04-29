import sys

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Reshape, Lambda, Conv3D
tf.compat.v1.disable_eager_execution()

import numpy as np

from creAI.plugins.file_manager.formats.tilemaps.minecraft_tilemaps import (
    Minecraft_Tilemap, Schematic)
from creAI.plugins.style_transfer.data_generator import Random_Data_Generator
from creAI.plugins.style_transfer.data_preprocessing import vectorize_tilemap
from creAI.plugins.style_transfer.tile_transformer import Tile_Transformer
from creAI.plugins.style_transfer.tile_encoder import Tile_VAE, Tile_Decoder
from creAI.plugins.style_transfer.tile_renderer import Tile_Renderer
from creAI.plugins.style_transfer.losses import tilemap_style_loss
from creAI.plugins.style_transfer.model_manager import get_full_path

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  # Restrict TensorFlow to only allocate 1GB of memory on the first GPU
  try:
    tf.config.experimental.set_virtual_device_configuration(
        gpus[0],
        [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=4096)])
    logical_gpus = tf.config.experimental.list_logical_devices('GPU')
    print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
  except RuntimeError as e:
    # Virtual devices must be set before GPUs have been initialized
    print(e)

def train(tilemap: Minecraft_Tilemap, model_name: str):
    
    batch_size=1
    input_shape = (50, 40, 50, 1)

    # Generating training data
    style_reference, palette = vectorize_tilemap(tilemap)
    vae_data = np.array(list(palette.values()))[:32]
    generator = Random_Data_Generator(batch_size=batch_size, min_shape=input_shape[:-1], max_shape=input_shape[:-1])

    latent_dim = 8
    intermediate_dim = 32
    
    output_shape = (50, 40, 50, style_reference.shape[-1])

    # Pre-training the VAE part of the model
    vae = Tile_VAE(output_shape[-1], intermediate_dim=intermediate_dim, latent_dim=latent_dim)
    vae_loss = tf.keras.losses.MeanSquaredError()
    vae_optimizer = tf.keras.optimizers.Adam(learning_rate=1e-3)
    vae.compile(optimizer=vae_optimizer, loss=vae_loss)
    vae.fit(vae_data, vae_data, 
                        batch_size=16, epochs=100)

    # Initializing model
    input_ = Input(input_shape)
    transformer = Tile_Transformer(channels=latent_dim)(input_)

    decode_layer = transformer
    for layer in [vae.decoder.intermediate_layer, vae.decoder.output_layer]:
        W, b = layer.get_weights()
        in_dim = layer.get_weights()[0].shape[0]
        out_dim = layer.get_weights()[1].shape[0]
        W = W.reshape((1, 1, 1, in_dim, out_dim))
        decode_layer = Conv3D(
            filters=out_dim, 
            kernel_size=1, 
            strides=1,
            weights=[W, b]
            )(decode_layer)

    model = Model(input_, decode_layer)

    
    tf.keras.utils.plot_model(model, to_file='model.png', show_shapes=True)

    filler = np.zeros([batch_size]+list(input_shape[:-1])+[style_reference.shape[-1]])
    filler[:,:,:,:,3:8*3] = 1.
    content_reference = input_ * filler
    # Training model
    loss = tilemap_style_loss(
        style_reference=style_reference,
        content_reference=content_reference,
        style_weight=1.,
        content_weight=1.,
        img_dim=[batch_size+1, 200, 200, 3],
        vgg_layer_names=[
            'block1_conv1', 'block2_conv1',
            'block3_conv1', 'block4_conv1',
            'block5_conv1'
        ]
    )
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
    model.compile(optimizer=optimizer, loss=loss)
    model.fit(generator, epochs=1)

    # Rendering test
    #render_input = Input(style_reference.shape)
    rendered = Tile_Renderer([batch_size, 400, 400, 3], trainable=False)(decode_layer)
    render_test_model = Model(input_, rendered)
    imgs_arr = render_test_model.predict(generator[0])
    img = tf.keras.preprocessing.image.array_to_img(imgs_arr[0])
    tf.keras.preprocessing.image.save_img('rendered.png', img)
    
    model.save(get_full_path(model_name))


if __name__ == '__main__':
    tilemap = Schematic.load(sys.argv[1])
    model_name = sys.argv[2]
    train(tilemap, model_name)
