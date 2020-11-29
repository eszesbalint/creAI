"""Generator network.
"""

from os import PathLike
from os.path import join
from tensorflow.keras import Model
from tensorflow.keras.layers import Conv3D, Conv3DTranspose, Input, Layer, BatchNormalization, Activation, LeakyReLU
from tensorflow.keras.models import load_model
from tensorflow.keras import Sequential
import tensorflow as tf
tf.compat.v1.disable_eager_execution()


class GeneratorNetwork():
    """Generator network.

    This model uses a series of transposed convolutions to upscale and produce
    an output from a smaller noise tensor.

    Args:
        input_channels (int): The number of channels of the input.
        output_channels (int): The number of channels in output.

    Attributes:
        input_channels (int): The number of channels of the input.
        output_channels (int): The number of channels in output.
        model (Keras.Model): The computational graph representing the model.
    """
    def __init__(self, input_channels=None, output_channels=None):
        self.input_channels = input_channels
        self.output_channels = output_channels

    def build(self):
        """Builds the Keras model for the generator.
        """
        input_shape = (None, None, None, self.input_channels)
        input_ = Input(shape=input_shape)
        x = input_
        #x = DepthwiseSeparableConv3dTranspose(
        #    128, 64, (4,4,4), strides=(2,2,2), activation='relu', 
        #    padding='same', kernel_initializer='he_normal')(x)
        x = Conv3DTranspose(
            128, (3,3,3), strides=(2,2,2), 
            padding='same')(x)
        x = BatchNormalization()(x)
        x = LeakyReLU(alpha=0.01)(x)

        x = Conv3DTranspose(
            64, (3,3,3), strides=(2,2,2), 
            padding='same')(x)
        x = BatchNormalization()(x)
        x = LeakyReLU(alpha=0.01)(x)

        x = Conv3DTranspose(
            32, (3,3,3), strides=(2,2,2), 
            padding='same')(x)
        x = BatchNormalization()(x)
        x = LeakyReLU(alpha=0.01)(x)

        x = Conv3D(self.output_channels, (3,3,3), padding='same', activation=None)(x)
        output = x
        self.model = Model(input_, output)
        

    @classmethod
    def load(cls, pth: PathLike):
        g = cls()
        g.model = load_model(pth, compile=False)
        g.input_channels = g.model.input_shape[-1]
        g.output_channels = g.model.output_shape[-1]
        return g
    
    def save(self, pth: PathLike):
        self.model.save(pth, include_optimizer=False)



#class DepthwiseSeparableConv3d(Layer):
#    def __init__(self, input_channels, filters, kernel_size, 
#                strides=(1, 1, 1), padding='valid', data_format=None, 
#                dilation_rate=(1, 1, 1), groups=1, activation=None, 
#                use_bias=True, kernel_initializer='glorot_uniform', 
#                bias_initializer='zeros', kernel_regularizer=None, 
#                bias_regularizer=None, activity_regularizer=None, 
#                kernel_constraint=None, bias_constraint=None, **kwargs):
#        super(DepthwiseSeparableConv3d, self).__init__(**kwargs)
#        self.input_channels = input_channels
#        self.depthwise_convolutions = [
#            Conv3D(1, kernel_size, strides, padding, data_format=data_format, 
#                dilation_rate=dilation_rate, activation=None, 
#                use_bias=use_bias, kernel_initializer=kernel_initializer, 
#                bias_initializer=bias_initializer, 
#                kernel_regularizer=kernel_regularizer, 
#                bias_regularizer=bias_regularizer, 
#                activity_regularizer=activity_regularizer, 
#                kernel_constraint=kernel_constraint, 
#                bias_constraint=bias_constraint)
#            for _ in range(self.input_channels)
#        ]
#        self.batch_norm1 = BatchNormalization()
#        self.activation1 = Activation(activation=activation)
#        self.poinwise_convolution = Conv3D(
#            filters, (1,1,1), 
#            padding='valid', activation=None
#            )
#        self.batch_norm2 = BatchNormalization()
#        self.activation2 = Activation(activation=activation)
#
#    def call(self, input_):
#        x = input_
#        channels = tf.split(x, num_or_size_splits=self.input_channels, axis=-1)
#        x = [conv(channel) for conv, channel in zip(self.depthwise_convolutions, channels)]
#        x = tf.concat(x, axis=-1)
#        x = self.batch_norm1(x)
#        x = self.activation1(x)
#        x = self.poinwise_convolution(x)
#        x = self.batch_norm2(x)
#        x = self.activation2(x)
#        return x

#class DepthwiseSeparableConv3dTranspose(DepthwiseSeparableConv3d):
#    def __init__(self, input_channels, filters, kernel_size, 
#                strides=(1, 1, 1), padding='valid', data_format=None, 
#                dilation_rate=(1, 1, 1), activation=None, 
#                use_bias=True, kernel_initializer='glorot_uniform', 
#                bias_initializer='zeros', kernel_regularizer=None, 
#                bias_regularizer=None, activity_regularizer=None, 
#                kernel_constraint=None, bias_constraint=None, **kwargs):
#        super(DepthwiseSeparableConv3dTranspose, self).__init__(
#                input_channels, filters, kernel_size, 
#                strides=(1, 1, 1), padding='valid', data_format=None, 
#                dilation_rate=(1, 1, 1), activation=None, 
#                use_bias=True, kernel_initializer='glorot_uniform', 
#                bias_initializer='zeros', kernel_regularizer=None, 
#                bias_regularizer=None, activity_regularizer=None, 
#                kernel_constraint=None, bias_constraint=None, **kwargs)
#        self.depthwise_convolutions = [
#            Conv3DTranspose(1, kernel_size, strides, padding, 
#                data_format=data_format, 
#                dilation_rate=dilation_rate, activation=None, 
#                use_bias=use_bias, kernel_initializer=kernel_initializer, 
#                bias_initializer=bias_initializer, 
#                kernel_regularizer=kernel_regularizer, 
#                bias_regularizer=bias_regularizer, 
#                activity_regularizer=activity_regularizer, 
#                kernel_constraint=kernel_constraint, 
#                bias_constraint=bias_constraint)
#            for _ in range(self.input_channels)
#        ]