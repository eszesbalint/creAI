"""Feature-loss
"""

import numpy as np
from itertools import product

from tensorflow.keras.activations import softmax, relu, tanh
import tensorflow as tf
import tensorflow.keras.backend as K


def feature_loss(y_true: np.ndarray, y_pred, kernel_size, max_filters):
    """Feature loss.

    This loss function calculates the local similarity between two 4D tensors.
    Args:
        y_true (np.ndarray): The example output. This doesn't change during
            training. It is used to create convolution kernels.
        y_pred (tf.Tensor): The output of a model.
        kernel_size (tuple of int): The size of the kernel used in the
            calculation of local similarity.
        max_filters (int): The max number of unique features to extract from
            the example tensor.

    Returns:
        function: The loss function built for y_true.
    """
    def features_from(y_true, kernel_size, max_filters):
        """Extracting all kernel-sized unique features from y_true.

        Args:
            y_true (np.ndarray): The example output. This doesn't change during
                training. It is used to create convolution kernels.
            kernel_size (tuple of int): The size of the kernel used in the
                calculation of local similarity.
            max_filters (int): The max number of unique features to extract from
                the example tensor. 
        """
        #Finding all kernel-sized features of y_true 
        k_w, k_h, k_l = kernel_size
        w, h, l, c = y_true.shape
        #Zero padding
        #padded = np.zeros(shape=(w+k_w//2*2, h+k_h//2*2, l+k_l//2*2, c))
        #padded[k_w//2:-(k_w//2),k_h//2:-(k_h//2),k_l//2:-(k_l//2)] = y_true
        #w, h, l, _ = padded.shape

        iterator = product(range(w-k_w), range(h-k_h), range(l-k_l))
        features = []
        for x, y, z in iterator:
            features.append(y_true[x:x+k_w,y:y+k_h,z:z+k_l])
        
        #Find unique features and count them
        features, counts = np.unique(features, axis=0, return_counts=True)

        #Sort features by counts
        sorted_ = list(zip(features, counts))
        sorted_.sort(key=lambda tuple_: tuple_[1], reverse=True)
        print('{} unique features detected.'.format(len(sorted_)))

        #Get the first max_filters features from sorted list
        max_filters = min(max_filters, len(sorted_))
        features = [f for f, c in sorted_[:max_filters]]
        features = np.array(features)
        features = np.moveaxis(features, 0, -1)
        return features

    def lmse(y_true, kernel_size, max_filters):
        """
        MSE(fp, ft) = mean((fp-ft)^2)

           where fp is a kernel-sized feature of y_pred and 
                 ft is a kernel-sized feature of y_true

        This can be calculated for all features of y_pred as a sum of convolutions:
        LMSE(y_pred, y_true) = 
            (conv(y_pred^2,k1) + conv(1,k2) - 2*conv(y_pred,k3))/kernel_size

           where k1, k2 are the convolution kernels and
                 k1 = 1,
                 k2 = ft^2
                 k3 = ft

        Returns:
            function: Local mean-square error.
        """
        c = y_true.shape[-1]
        y_shape = tf.TensorShape([None, None, None, None, c])
        s = kernel_size[0] * kernel_size[1] * kernel_size[2] * c

        ft = features_from(y_true, kernel_size, max_filters)

        #Init convolution kernels
        k1 = np.ones(shape=ft.shape)
        k2 = ft**2
        k3 = ft

        def func(y_pred):
            ones = tf.ones_like(y_pred)
            conv1 = tf.nn.conv3d(y_pred**2, k1, strides=[1,1,1,1,1], padding='VALID')
            conv2 = tf.nn.conv3d(ones, k2, strides=[1,1,1,1,1], padding='VALID')
            conv3 = tf.nn.conv3d(y_pred, k3, strides=[1,1,1,1,1], padding='VALID')
            return (conv1 + conv2 - 2*conv3) / s

        return func

    def gram_matrix(activations):
        """ Calculates a batch of Gram matrices of filter activations

        Args:
            activations: a batch of filter activations

        Returns:
            tf.Tensor: a batch of Gram matrices
        """
        activations = tf.transpose(activations, perm=[0, 4, 1, 2, 3])  # Channel first
        shape = tf.shape(activations)
        b = shape[0]
        c = shape[1]
        filters = tf.reshape(activations, [ b, c, -1])
        gram = tf.linalg.matmul(filters, filters, transpose_b=True)
        return gram

    # Precalculating the Gram-matrix for the example tensor
    local_mean_square_error = lmse(y_true, kernel_size, max_filters)

    y_true_edge = tf.constant(np.array([y_true]))
    
    lmse_true = local_mean_square_error(y_true_edge)
    activations_true = (1.01-tanh(lmse_true*10)-tanh(lmse_true)/100)/1.01
    #activations_true = 1-tanh(lmse_true)
    s =  tf.shape(activations_true)[-2] \
        *tf.shape(activations_true)[-3] \
        *tf.shape(activations_true)[-4]
    gram_true = gram_matrix(activations_true) / tf.cast(s, tf.float32)
    y_true_mean = K.mean(y_true_edge, axis=[-4,-3,-2])

    # Creating a function that calculates difference between Gram-matrices
    def loss_func(y_true, y_pred):
        lmse_pred = local_mean_square_error(y_pred)
        activations_pred = (1.01-tanh(lmse_pred*10)-tanh(lmse_pred)/100)/1.01
        #activations_pred = 1-tanh(lmse_pred)
        s =  tf.shape(activations_pred)[-2] \
            *tf.shape(activations_pred)[-3] \
            *tf.shape(activations_pred)[-4]
        gram_pred = gram_matrix(activations_pred) / tf.cast(s, tf.float32)
        y_pred_mean = K.mean(y_pred, axis=[-4,-3,-2])
        return K.sum(K.square(gram_pred - gram_true), axis=[-2, -1]) \
               + K.sum(K.square(y_pred_mean - y_true_mean), axis=[-1])*10

    return loss_func

