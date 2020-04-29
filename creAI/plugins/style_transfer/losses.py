import tensorflow as tf
import tensorflow.keras.backend as K
from creAI.plugins.style_transfer.tile_renderer import Tile_Renderer

def tilemap_style_loss(style_reference, content_reference, 
                       style_weight, content_weight, 
                       img_dim, vgg_layer_names):
    """Returns a loss function that calculates style loss + content loss

    Args:
        style_reference: a numpy array or tf.Tensor containing a single vectorized tilemap
        content_reference: a numpy array or tf.Tensor containing multiple vectorized tilemaps
        style_weight: weight of style loss
        content_weight: weight of content loss
        img_dim: output shape of differential rendering
        vgg_layer_names: using these layers' filters to calculate style loss

    Returns:
        function: loss function
    """
    renderer = Tile_Renderer(img_dim, trainable=False)

    def loss_fn(y_true, y_pred):
        nonlocal style_reference
        if not tf.is_tensor(style_reference):
            style_reference = K.constant(style_reference)
        style_reference = K.cast(style_reference, y_pred.dtype)

        nonlocal content_reference
        if not tf.is_tensor(content_reference):
            content_reference = K.constant(content_reference)
        content_reference = K.cast(content_reference, y_pred.dtype)

        generated = y_pred

        # Rendering
        style_img = renderer([style_reference])
        content_img = renderer(content_reference)
        generated_img = renderer(generated)

        # Calculating content loss

        content_loss = K.mean(
            K.square(content_img - generated_img), 
            axis=[-3,-2,-1],
        )

        # Forward pass in VGG net
        vgg_input = tf.concat([style_img, generated_img], axis=0)

        vgg16 = tf.keras.applications.vgg16.VGG16(
            include_top=False,
            weights='imagenet',
            input_tensor=vgg_input,
            input_shape=img_dim[1:],
            pooling=None,
        )
        for layer in vgg16.layers:
            layer.trainable = False
        # Selecting VGG layer outputs
        vgg_layer_outputs = dict(
            [
                (layer.name, layer.output)
                for layer in vgg16.layers
                if layer.name in vgg_layer_names
            ]
        )
        
        # Calculating style loss
        style_loss = 0.
        for layer_output in vgg_layer_outputs.values():
            style_loss += K.mean(
                K.square(
                    gram_matrix(layer_output[:1])     # Style
                    - gram_matrix(layer_output[1:])   # Generated
                ),
                axis=[-2, -1]
            )
        style_loss /= len(vgg_layer_outputs)
        return style_weight*style_loss + content_weight*content_loss
    return loss_fn




def gram_matrix(input_):
    """ Calculates a batch of Gram matrices of filter activations
    
    Args:
        input_: a batch of filter activations

    Returns:
        tf.Tensor: a batch of Gram matrices
    """
    input_ = tf.transpose(input_, perm=[0, 3, 1, 2])  # Channel first
    filters = tf.reshape(
        input_,
        [ tf.shape(input_)[0], tf.shape(input_)[1], -1]
    )
    gram = tf.linalg.matmul(filters, filters, transpose_b=True)
    return gram