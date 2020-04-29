import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import (Activation, BatchNormalization, Conv3D,
                                     Conv3DTranspose, Dropout, Layer, Flatten,
                                     Reshape, Lambda)
from tensorflow.keras.models import Model
import tensorflow.keras.backend as K



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


    def call(self, inputs):
        output = inputs

        for block in self.blocks:
            output = block(output)

        return output


  
