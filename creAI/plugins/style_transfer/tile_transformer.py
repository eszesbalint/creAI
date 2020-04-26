import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import (Activation, BatchNormalization, Conv3D,
                                     Conv3DTranspose, Dropout, Layer, Flatten,
                                     Reshape, Lambda)
from tensorflow.keras.models import Model
import tensorflow.keras.backend as K

from creAI.plugins.style_transfer.tile_encoder import Tile_VAE
from creAI.plugins.style_transfer.tile_renderer import Tile_Renderer

tf.keras.backend.set_image_data_format('channels_last')



class Convolutional_Block(Layer):
    def __init__(self, dropout_rate=0., batch_normalization=True,
                 activation='relu', name='conv_block', **kwargs):
        super(Convolutional_Block, self).__init__(name=name)
        self.conv_layer = Conv3D(**kwargs)
        self.dropout_layer = Dropout(dropout_rate)
        if batch_normalization:
            self.batch_norm_layer = BatchNormalization()
        else:
            self.batch_norm_layer = None
        self.activation_layer = Activation(activation)

    def call(self, inputs):
        output = self.conv_layer(inputs)
        drop = self.dropout_layer(output)
        if self.batch_norm_layer is not None:
            norm = self.batch_norm_layer(drop)
            output = self.activation_layer(norm)
        else:
            output = self.activation_layer(drop)
        return output


class Transposed_Convolutional_Block(Layer):
    def __init__(self, dropout_rate=0., batch_normalization=True,
                 activation='relu', name='conv_block',**kwargs):
        super(Transposed_Convolutional_Block,
              self).__init__(name=name)
        self.conv_layer = Conv3DTranspose(**kwargs)
        self.dropout_layer = Dropout(dropout_rate)
        if batch_normalization:
            self.batch_norm_layer = BatchNormalization()
        else:
            self.batch_norm_layer = None
        self.activation_layer = Activation(activation)

    def call(self, inputs):
        output = self.conv_layer(inputs)
        drop = self.dropout_layer(output)
        if self.batch_norm_layer is not None:
            norm = self.batch_norm_layer(drop)
            output = self.activation_layer(norm)
        else:
            output = self.activation_layer(drop)
        return output


class Residual_Block(Layer):
    def __init__(self, filters, name='residual_block', **kwargs):
        super(Residual_Block, self).__init__(name=name, **kwargs)
        self.conv_1 = Convolutional_Block(activation='relu', dropout_rate=0.01,
                                     filters=128, kernel_size=1, strides=1,
                                     padding='same')
        self.conv_2 = Convolutional_Block(activation='relu', dropout_rate=0.01,
                                     filters=128, kernel_size=3, strides=1,
                                     padding='same')
        self.conv_3 = Convolutional_Block(activation='relu', dropout_rate=0.01,
                                     filters=filters, kernel_size=1, strides=1,
                                     padding='same')

    def call(self, inputs):
        output = self.conv_1(inputs)
        output = self.conv_2(output)
        output = self.conv_3(output)
        return inputs + output


class Tile_Transformer(Layer):
    def __init__(self, channels, name='tile_transformer', **kwargs):
        super(Tile_Transformer, self).__init__(name=name, **kwargs)
        #self.style_reference = style_reference
        #self.vae = Tile_VAE(output_dim=output_shape[-1])
        #self.reshape_layer1 = Reshape((-1, self.vae.latent_dim))
        #self.decode_layer = Lambda(lambda x: tf.map_fn(lambda t: self.vae.decoder(t), x))
        #self.reshape_layer2 = Reshape(output_shape)

        num_conv_blocks = 3
        num_res_blocks = 3
        num_filters = [channels, 32, 64, 128, 256, 512]
        kernel_sizes = [9, 3, 3, 3, 3, 3]

        self.blocks = []
        # Convolutional blocks
        for l in range(num_conv_blocks):
            self.blocks += [Convolutional_Block(
                dropout_rate=0.1,
                batch_normalization=True,
                activation='relu',
                filters=num_filters[l+1],
                kernel_size=kernel_sizes[l],
                strides=3,
                padding='same',
            )]
        # Residual blocks
        for _ in range(num_res_blocks):
            self.blocks += [Residual_Block(
                filters=num_filters[num_conv_blocks]
            )]
        # Transposed convolutional blocks
        for k in range(num_conv_blocks):
            self.blocks += [Transposed_Convolutional_Block(
                dropout_rate=0.1,
                batch_normalization=True,
                activation='relu',
                filters=num_filters[num_conv_blocks-k-1],
                kernel_size=kernel_sizes[num_conv_blocks-k-1],
                strides=3,
                padding='same',
            )]

        
        
        #img_dim = [256, 256, 3]  # Rendered image size
        #self.renderer = Tile_Renderer(img_dim, trainable=False)
        #self.vgg16 = tf.keras.applications.vgg16.VGG16(
        #    include_top=False,
        #    weights='imagenet',
        #    input_shape=img_dim,
        #    pooling=None,
        #)
        #for layer in self.vgg16.layers:
        #    layer.trainable = False

    def call(self, inputs):
        output = inputs

        for block in self.blocks:
            output = block(output)

        # Decoding
        #output = self.reshape_layer1(output)  # Flattening
        #output = self.decode_layer(output)
        #output = self.reshape_layer2(output)

        #loss = self._style_loss(
        #    [
        #        'block1_conv1', 'block2_conv1',
        #        'block3_conv1', 'block4_conv1',
        #        'block5_conv1'
        #    ]
        #)
        #self.add_loss(loss(self.style_reference, output))

        return output

    def _style_loss(self, vgg_layer_names):
        # Selecting VGG layer outputs
        vgg_layer_outputs = dict(
            [
                (layer.name, layer.output)
                for layer in self.vgg16.layers
                if layer.name in vgg_layer_names
            ]
        )

        @tf.function()
        def loss(y_true, y_pred):
            if not tf.is_tensor(self.style_reference):
                style_reference = K.constant(self.style_reference)
            style_reference = K.cast(style_reference, y_pred.dtype)
            generated = y_pred
            # Rendering
            style_img = self.renderer([style_reference])
            generated_img = self.renderer(generated)
            return K.mean(K.square(style_img-generated_img), axis=-1)

            # Forward pass in VGG net
            vgg_input = tf.concat([[style_img], [generated_img]], axis=0)
            vgg16_output = self.vgg16(vgg_input)

            

            # Calculating style loss
            style_loss = []
            for layer_output in vgg_layer_outputs.values():
                style_loss += [K.mean(
                    K.square(
                        self._gram_matrix(layer_output[0])     # Style
                        - self._gram_matrix(layer_output[1])   # Generated
                    ),
                    [-2, -1]
                )]

            style_loss = K.sum(tf.stack(style_loss), axis=-1)
            print(tf.shape(style_loss))
            return style_loss
        return loss

    def _content_loss(self, content, generated):
        pass

    @staticmethod
    def _gram_matrix(input_):
        input_ = tf.transpose(input_, perm=[ 2, 0, 1])  # Channel first
        filters = tf.reshape(
            input_,
            [ tf.shape(input_)[0], -1]
        )
        gram = tf.linalg.matmul(filters, filters, transpose_b=True)
        return gram
  
