import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import (Activation, BatchNormalization, Conv3D,
                                     Conv3DTranspose, Dropout, Layer)
from tensorflow.keras.models import Model

from creAI.plugins.style_transfer.tile_encoder import Tile_VAE
from creAI.plugins.style_transfer.tile_renderer import Tile_Renderer


class Convolutional_Block(Layer):
    def __init__(self, dropout_rate=0., batch_normalization=True,
                 activation='relu', name='conv_block', **kwargs):
        super(Convolutional_Block, self).__init__(name=name, **kwargs)
        self.conv_layer = Conv3D(**kwargs)
        self.dropout_rate = dropout_rate
        self.batch_normalization = batch_normalization
        self.activation = activation

    def call(self, inputs):
        output = self.conv_layer(inputs)
        drop = Dropout(self.dropout_rate)(output)
        if self.batch_normalization:
            norm = BatchNormalization()(drop)
            output = Activation(self.activation)(norm)
        else:
            output = Activation(self.activation)(norm)
        return output


class Transposed_Convolutional_Block(Layer):
    def __init__(self, dropout_rate=0., batch_normalization=True,
                 activation='relu', name='conv_block', **kwargs):
        super(Transposed_Convolutional_Block,
              self).__init__(name=name, **kwargs)
        self.conv_layer = Conv3DTranspose(**kwargs)
        self.dropout_rate = dropout_rate
        self.batch_normalization = batch_normalization
        self.activation = activation

    def call(self, inputs):
        output = self.conv_layer(inputs)
        drop = Dropout(self.dropout_rate)(output)
        if self.batch_normalization:
            norm = BatchNormalization()(drop)
            output = Activation(self.activation)(norm)
        else:
            output = Activation(self.activation)(norm)
        return output


class Residual_Block(Layer):
    def __init__(self, name='residual_block', **kwargs):
        super(Residual_Block, self).__init__(name=name, **kwargs)

    def call(self, inputs):
        num_in_fil = inputs.get_shape()[-1]
        conv_1 = Convolutional_Block(activation='relu', dropout_rate=0.01,
                                     filters=128, kernel_size=1, strides=1,
                                     padding='same')(inputs)
        conv_2 = Convolutional_Block(activation='relu', dropout_rate=0.01,
                                     filters=128, kernel_size=3, strides=1,
                                     padding='same')(conv_1)
        conv_3 = Convolutional_Block(activation='relu', dropout_rate=0.01,
                                     filters=num_in_fil, kernel_size=1, strides=1,
                                     padding='same')(conv_2)

        return conv_3 + inputs


class Tile_Transformer(Model):
    def __init__(self, style_reference, name='tile_transformer', **kwargs):
        super(Tile_Transformer, self).__init__(name=name, **kwargs)
        self.style_reference = style_reference
        self.vae = Tile_VAE(output_dim=tf.shape(style_reference)[-1])

    def call(self, inputs):
        # Parameters
        b = tf.shape(inputs)[0]         # Batch size
        w = tf.shape(inputs)[-4]        # Width
        h = tf.shape(inputs)[-3]        # Height
        l = tf.shape(inputs)[-2]        # Length

        v_l = self.vae.output_dim  # Decoder output size
        z_l = self.vae.latent_dim  # Decoder input size

        num_conv_blocks = 2
        num_res_blocks = 3
        num_filters = [3, 32, 64, 128, 256, 512]
        kernel_sizes = [9, 3, 3, 3, 3, 3]

        # Architecture
        #input_ = tf.keras.layers.Input(shape=(None, None, None, 1))
        output = inputs
        # Convolutional blocks
        for l in range(num_conv_blocks):
            output = Convolutional_Block(
                dropout_rate=0.01,
                batch_normalization=True,
                activation='relu',
                filters=num_filters[l+1],
                kernel_size=kernel_sizes[l],
                strides=1,
                padding='valid',
            )(output)
        # Residual blocks
        for _ in range(num_res_blocks):
            output = Residual_Block()(output)
        # Transposed convolutional blocks
        for k in range(num_conv_blocks):
            output = Transposed_Convolutional_Block(
                dropout_rate=0.01,
                batch_normalization=True,
                activation='relu',
                filters=num_filters[num_conv_blocks-k-1],
                kernel_size=kernel_sizes[num_conv_blocks-k-1],
                strides=1,
                padding='valid',
            )(output)

        # Decoding
        output = tf.reshape(output, [b*w*h*l, z_l])  # Flattening
        output = self.vae.decoder(output)
        output = tf.reshape(output, [b, w, h, l, v_l])

        loss = self._style_loss(
            output,
            [
                'block1_conv1', 'block2_conv1',
                'block3_conv1', 'block4_conv1',
                'block5_conv1'
            ]
        )
        self.add_loss(loss)

        return output

    def _style_loss(self, generated, vgg_layer_names):
        b = tf.shape(generated)[0]  # Batch size
        img_dim = [b, 256, 256, 3]  # Rendered image size

        # Rendering
        style_img = Tile_Renderer(img_dim)([self.style_reference])
        generated_img = Tile_Renderer(img_dim)(generated)

        # Forward pass in VGG net
        vgg_input = tf.concat([style_img, generated_img], axis=0)
        vgg16 = tf.keras.applications.vgg16.VGG16(
            include_top=False,
            weights='imagenet',
            input_tensor=vgg_input,
            input_shape=img_dim[1:],
            pooling=None,
        )

        # Selecting VGG layer outputs
        vgg_layer_outputs = dict(
            [
                (layer.name, layer.output)
                for layer in vgg16.layers
                if layer.name in vgg_layer_names
            ]
        )

        # Calculating style loss
        style_loss = 0.
        for layer_output in vgg_layer_outputs.items():
            style_loss += tf.reduce_sum(
                tf.square(
                    self._gram_matrix(layer_output[:1])     # Style
                    - self._gram_matrix(layer_output[1:])   # Generated
                )
            ) / tf.cast(tf.shape(layer_output)[-1]**2, tf.float32)

        style_loss /= tf.cast(
            len(vgg_layer_outputs) * img_dim[1]*img_dim[2]**2,
            tf.float32
        )
        return style_loss

    def _content_loss(content, generated):
        pass

    @staticmethod
    def _gram_matrix(input_):
        input_ = tf.transpose(input_, perm=[0, 4, 1, 2, 3])  # Channel first
        filters = tf.reshape(
            input_,
            [tf.shape(input_)[0], tf.shape(input_)[1], -1]
        )
        gram = tf.linalg.matmul(filters, filters, transpose_b=True)
        return gram
  
