import tensorflow as tf


from creAI.plugins.style_transfer.tile_transformer import Transformer_Model
from creAI.plugins.style_transfer.tile_encoder import VAE_Model
from creAI.plugins.style_transfer.tile_renderer import Tile_Renderer
from creAI.plugins.style_transfer.data_preprocessing import generate_training_data

# Generating training data for the variational autoencoder
vae_training_data = generate_training_data()

# Length of the vector representation of a tile, and the
# latent representation
v_l = vae_training_data.shape[-1]
z_l = 8

# Creating and training the VAE model
vae, encoder, decoder = VAE_Model(vae_training_data.shape[-1], 8)
vae.fit(vae_training_data, vae_training_data, batch_size = 32, epochs=10)




input_ = tf.keras.layers.Input(shape=(None, None, None, 1))
b = tf.shape(input_)[0]         # Batch size
w = tf.shape(input_)[-4]
h = tf.shape(input_)[-3]
l = tf.shape(input_)[-2]


output = Transformer_Model()(input_)
output = tf.reshape(output, [b*w*h*l,z_l])
output = encoder(output)
output = tf.reshape(output, [b,w,h,l,v_l])

img_size = (256, 256, 3)
output = Tile_Renderer([b]+img_size)(output)
vgg16 = keras.applications.vgg16.VGG16(
    include_top=False, 
    weights='imagenet', 
    input_tensor=output, 
    input_shape=img_size, 
    pooling=None, 
    )