"""Random noise generator module.

This module implement a data generator that produces random noise tensors of
random size.
"""

from tensorflow.keras.utils import Sequence
import numpy as np
from random import randint, seed


class RandomNoise(Sequence):
    """Random noise generator.

    Data generator that produces noise tensors of random size.

    Args:
        number_of_samples (int, optional): Number of training samples to generate i.e.
            the length of the training set.
        channels (int, optional): Length of the last dimension.
        batch_size (int, optional): Batch size.
        min_shape (tuple of int, optional): The smallest tensor possible.
        max_shape (tuple of int, optional): The largest tensor possible.
        seed (int): The random generation seed.
    """
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
        """Generates a batch of random tensors.

        Each tensor has the same shape inside a batch.

        Args:
            index (int): Index of the batch. This is used in the randomization
                process.
        """
        seed(self.seed+index)
        np.random.seed(self.seed+index)
        
        b = self.batch_size
        c = self.channels
        w, h, l = [randint(a, b) for a, b in zip(self.min_shape, self.max_shape)]
        batch = np.random.normal(size=(b,w,h,l,c))

        return batch, None