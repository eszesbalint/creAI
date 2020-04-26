import random
import sys

import numpy as np
import tensorflow as tf

np.set_printoptions(threshold=sys.maxsize)

class Random_Data_Generator(tf.keras.utils.Sequence):

    def __init__(self, number_of_samples=1000, batch_size=64, 
                min_shape=[20,20,20], max_shape=[50,50,50], 
                borders=[5,5,5],
                max_num_cuboids=6, min_cuboid_shape=[8,8,8]):
        self.number_of_samples = number_of_samples
        self.batch_size = batch_size
        self.min_shape = min_shape
        self.max_shape = max_shape
        self.borders = borders
        self.max_num_cuboids = max_num_cuboids
        self.min_cuboid_shape = min_cuboid_shape

    def __len__(self):
        return self.number_of_samples // self.batch_size

    def __getitem__(self, index):
        return self.__data_generation()

    def __data_generation(self):
        shape = [
            random.randint(m, M) 
            for m, M in zip(self.min_shape, self.max_shape)
        ]
        batch = np.zeros(shape=[self.batch_size] + shape + [1])
        for x in batch:
            for n in range(random.randint(1, 6)):
                x_1 = random.randint(
                    self.borders[0], 
                    shape[0]-self.min_cuboid_shape[0]-self.borders[0]
                )
                y_1 = 0
                z_1 = random.randint(
                    self.borders[2], 
                    shape[2]-self.min_cuboid_shape[2]-self.borders[2]
                )

                x_2 = random.randint(
                    x_1+self.min_cuboid_shape[0], 
                    shape[0]-self.borders[0]
                )
                y_2 = random.randint(
                    y_1+self.min_cuboid_shape[1], 
                    shape[1]-self.borders[1]
                )
                z_2 = random.randint(
                    z_1+self.min_cuboid_shape[2], 
                    shape[2]-self.borders[2]
                )

                x[x_1:x_2,y_1:y_2,z_1:z_2] = [1]

        return batch, batch
