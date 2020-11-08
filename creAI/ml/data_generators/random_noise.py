from tensorflow.keras.utils import Sequence
import numpy as np
from random import randint, seed


class RandomNoise(Sequence):

    def __init__(self, number_of_samples=1000, channels=1, batch_size=64, 
                min_shape=[20,20,20], max_shape=[50,50,50], seed=0):
        self.number_of_samples = number_of_samples
        self.batch_size = batch_size
        self.min_shape = min_shape
        self.max_shape = max_shape
        self.channels = channels
        self.seed = seed

    def __len__(self):
        return self.number_of_samples // self.batch_size

    def __getitem__(self, index):
        if index:
            seed(self.seed)
            np.random.seed(self.seed)
        
        b = self.batch_size
        c = self.channels
        w, h, l = [randint(a, b) for a, b in zip(self.min_shape, self.max_shape)]
        batch = np.random.normal(size=(b,w,h,l,c))

        return batch, None