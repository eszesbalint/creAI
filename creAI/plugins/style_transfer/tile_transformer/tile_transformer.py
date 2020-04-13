import numpy as np

import tensorflow as tf
import kerastuner as kt

class Transformer_Hyper_Model(kt.HyperModel):
    def __init__(self):
        pass
    def build(self, hyper_parameters):
        #Parameters
        num_conv_blocks = hyper_parameters.Int(
            'conv_blocks', 
            min_value=3, 
            max_value=8, 
            step=1
            )
        num_res_blocks = hyper_parameters.Int(
            'conv_blocks', 
            min_value=3, 
            max_value=8, 
            step=1
            )

        #Architecture
        input_ = tf.keras.layers.Input(shape=(None,None,None,1))
        for _ in range(num_conv_blocks):
            input_ = self._conv_block(input_)
        for _ in range(num_res_blocks):
            input_ = _res_block(input_)
        for _ in range(num_conv_blocks):
            input_ = _conv_trans_block(input_)

    @staticmethod
    def _conv_block(input_, filters, kernel_size, strides=1, 
                    padding='valid', activation=None, 
                    dropout_rate=0.):
        conv = tf.keras.layers.Conv3D(
            filters=filters, 
            kernel_size=kernel_size, 
            strides=strides,
            padding=padding,
            )(input_)
        drop = tf.keras.layers.Dropout(dropout_rate)(conv)
        norm = tf.keras.layers.BatchNormalization()(drop)
        act = tf.keras.layers.Activation('relu')(norm)
        return act

    @staticmethod
    def _conv_trans_block(input_, filters, kernel_size, strides=1, 
                            padding='valid', activation=None, 
                            dropout_rate=0.):
        conv = tf.keras.layers.Conv3D(
            filters=filters, 
            kernel_size=kernel_size, 
            strides=strides,
            padding=padding,
            )(input_)
        drop = tf.keras.layers.Dropout(dropout_rate)(conv)
        norm = tf.keras.layers.BatchNormalization()(drop)
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
        conv_3 = cls._conv_block(conv_3, filters=num_in_fil, kernel_size=1, 
                                strides=1, padding='same', activation='relu', 
                                dropout_rate=0.01)
        return conv_3 + input_

    @classmethod
    def train(cls):
        hyper_param_tuner = kt.tuners.RandomSearch(
            cls(),
            objective = 'val_loss',
            max_trials = 20,
            executions_per_trial = 1,
            project_name = creAI.globals.gen_rand_id(10),
            directory = model_path,
        )
        hyper_param_tuner.search_space_summary()
        #autoencoder.fit(training_data, training_data,
        #                epochs=epochs, batch_size=batch_size)

        hyper_param_tuner.search(training, training,
                        epochs=40, batch_size=batch_size, validation_data = (val, val))
        hyper_param_tuner.results_summary()