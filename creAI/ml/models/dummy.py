"""A dummy generator network for testing loss functions.
"""

from os import PathLike
from os.path import join
from tensorflow.keras import Model
from tensorflow.keras.layers import Layer
from tensorflow.keras.models import load_model
from tensorflow.keras import Sequential
import tensorflow as tf
tf.compat.v1.disable_eager_execution()

class TrainableInput(Layer):
    def __init__(self, output_dim, **kwargs):
        self.output_dim = output_dim
        super(TrainableInput, self).__init__(**kwargs)

    def build(self, input_shape):
        self.kernel = self.add_weight(name='kernel',
                                      shape=self.output_dim,
                                      initializer='normal',
                                      trainable=True)
        super(TrainableInput, self).build(input_shape)

    def call(self, x):
        return self.kernel

    def compute_output_shape(self, input_shape):
        return self.output_dim

class DummyGeneratorNetwork():
    def __init__(self, input_channels=None, output_channels=None):
        self.input_channels = input_channels
        self.output_channels = output_channels


    def build(self):
        self.model = Sequential([
            TrainableInput((1,16,16,16,self.output_channels), input_shape=(None, None, None, self.input_channels))
        ])
        

    @classmethod
    def load(cls, pth: PathLike):
        g = cls()
        g.model = load_model(pth, compile=False)
        g.input_channels = g.model.input_shape[-1]
        g.output_channels = g.model.output_shape[-1]
        return g
    
    def save(self, pth: PathLike):
        self.model.save(pth, include_optimizer=False)