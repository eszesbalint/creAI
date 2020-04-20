import creAI.globals
import numpy as np

import tensorflow as tf


class Transformer_Model():
    def __init__(self, vae_model):
        self.vae_model = vae_model

    def build(self,):
        # Parameters
        num_conv_blocks = 2
        num_res_blocks = 3
        num_filters = [3, 32, 64, 128, 256, 512]
        kernel_sizes = [9, 3, 3, 3, 3, 3]

        # Architecture
        input_ = tf.keras.layers.Input(shape=(None, None, None, 1))
        output = input_
        # Convolutional blocks
        for l in range(num_conv_blocks):
            output = self._conv_block(
                output,
                filters=num_filters[l+1],
                kernel_size=kernel_sizes[l],
                strides=1,
                padding='valid',
                activation='relu',
                dropout_rate=0.01,
                batch_normalization=True
            )
        # Residual blocks
        for _ in range(num_res_blocks):
            output = self._res_block(output)
        # Transposed convolutional blocks
        for k in range(num_conv_blocks):
            output = self._conv_trans_block(
                output,
                filters=num_filters[num_conv_blocks-k-1],
                kernel_size=kernel_sizes[num_conv_blocks-k-1],
                strides=1,
                padding='valid',
                activation='relu',
                dropout_rate=0.01,
                batch_normalization=True
            )

        transformer_model = tf.keras.models.Model(
            input_,
            self._decoder(output),
        )

        return transformer_model

    @staticmethod
    def _conv_block(input_, filters, kernel_size, strides=1,
                    padding='valid', activation=None,
                    dropout_rate=0.,  batch_normalization=True):
        conv = tf.keras.layers.Conv3D(
            filters=filters,
            kernel_size=kernel_size,
            strides=strides,
            padding=padding,
            data_format='channels_last'
        )(input_)
        drop = tf.keras.layers.Dropout(dropout_rate)(conv)
        if batch_normalization:
            norm = tf.keras.layers.BatchNormalization()(drop)
            act = tf.keras.layers.Activation('relu')(norm)
        else:
            act = tf.keras.layers.Activation('relu')(norm)
        return act

    @staticmethod
    def _conv_trans_block(input_, filters, kernel_size, strides=1,
                          padding='valid', activation=None,
                          dropout_rate=0., batch_normalization=True):
        conv = tf.keras.layers.Conv3DTranspose(
            filters=filters,
            kernel_size=kernel_size,
            strides=strides,
            padding=padding,
            data_format='channels_last'
        )(input_)
        drop = tf.keras.layers.Dropout(dropout_rate)(conv)
        if batch_normalization:
            norm = tf.keras.layers.BatchNormalization()(drop)
            act = tf.keras.layers.Activation('relu')(norm)
        else:
            act = tf.keras.layers.Activation('relu')(norm)
        return act

    @classmethod
    def _res_block(cls, input_):
        num_in_fil = input_.get_shape()[4]
        conv_1 = cls._conv_block(input_, filters=128, kernel_size=1, strides=1,
                                 padding='same', activation='relu',
                                 dropout_rate=0.01)
        conv_2 = cls._conv_block(conv_1, filters=128, kernel_size=3, strides=1,
                                 padding='same', activation='relu',
                                 dropout_rate=0.01)
        conv_3 = cls._conv_block(conv_2, filters=num_in_fil, kernel_size=1,
                                 strides=1, padding='same', activation='relu',
                                 dropout_rate=0.01)
        return conv_3 + input_

    def _decoder(self, input_):
        for layer in self.vae_model.layers:
            layer.trainable = False
        decoder = self.vae_model.get_layer('model_1')
        output = tf.keras.layers.Lambda(
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
                                            -2),
                                        x)
                                ),
                                -3),
                            x)
                    ),
                    -4),
                x),
            name='decoder'
        )(input_)
        return output

    @classmethod
    def train(cls, vae_model, renderer, perceptual_model):

        model = cls(vae_model, renderer, perceptual_model).build()
