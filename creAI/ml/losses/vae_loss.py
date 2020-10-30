import tensorflow.keras.backend as K
from tensorflow.keras.losses import mean_squared_error
import tensorflow as tf

def vae_loss(y_true, y_pred, z_mean, z_log_var):
    reconstruction_loss = mean_squared_error(y_true, y_pred)
    reconstruction_loss *= tf.cast(tf.shape(y_true)[-1], tf.float32)

    kl_loss = - 0.5 * K.sum(1 
                            + z_log_var 
                            - K.square(z_mean) 
                            - K.exp(z_log_var), 
                            axis=-1)
        
    return K.mean(reconstruction_loss + kl_loss)