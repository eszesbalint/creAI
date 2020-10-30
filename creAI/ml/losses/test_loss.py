import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K

def test_loss(y_true, y_pred):
    y_true = tf.constant((np.array([y_true])))
    def func(y_true, y_pred):
        return K.mean(K.square(y_true - y_pred))

    return func