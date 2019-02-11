import sys
#sys.path.insert(0, '/content/drive/My Drive/creAI')
#import tensorflow as tf
#from keras.layers import Lambda, Input, Dense, Flatten, Reshape, Conv3D, Conv3DTranspose, Activation
#from keras.models import Model
#from keras.losses import mse, binary_crossentropy, categorical_crossentropy
#from keras.activations import softmax
#from keras import backend as K
#from keras.optimizers import Adagrad, RMSprop, Adam

import numpy as np

from tilemaptransmodel import CreAITileMapTransformationModel

class CreAIModel(object):
    def __init__(self):
        self.model = CreAITileMapTransformationModel()

    def generate(self):
        return self.model.generate()
