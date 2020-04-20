import tensorflow as tf

class Random_Data_Generator(tf.keras.utils.Sequence):

    def __init__(self, number_of_samples, batch_size, min_shape, max_shape):
        self.number_of_samples = number_of_samples
        self.batch_size = batch_size
        self.min_shape = min_shape
        self.max_shape = max_shape

    def __len__():
        return self.number_of_samples // self.batch
    def __data_generation(self):