import tensorflow as tf
import tensorflow.keras.backend as K
from creAI.plugins.style_transfer.tile_renderer import Tile_Renderer

def style_loss(style_reference, img_dim, vgg_layer_names):
    renderer = Tile_Renderer(img_dim, trainable=False)
    vgg16 = tf.keras.applications.vgg16.VGG16(
        include_top=False,
        weights='imagenet',
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

    @tf.function()
    def loss(y_true, y_pred):
        nonlocal style_reference
        if not tf.is_tensor(style_reference):
            style_reference = K.constant(style_reference)
        style_reference = K.cast(style_reference, y_pred.dtype)
        generated = y_pred
        # Rendering
        style_img = renderer([style_reference])
        generated_img = renderer(generated)
        return K.mean(K.square(style_img-generated_img), axis=-1)

        # Forward pass in VGG net
        vgg_input = tf.concat([[style_img], [generated_img]], axis=0)
        vgg16_output = vgg16(vgg_input)

            

        # Calculating style loss
        style_loss = []
        for layer_output in vgg_layer_outputs.values():
            style_loss += [K.mean(
                K.square(
                    gram_matrix(layer_output[0])     # Style
                    - gram_matrix(layer_output[1])   # Generated
                ),
                [-2, -1]
            )]

        style_loss = K.sum(tf.stack(style_loss), axis=-1)
        print(tf.shape(style_loss))
        return style_loss
    return loss




def gram_matrix(input_):
    input_ = tf.transpose(input_, perm=[ 2, 0, 1])  # Channel first
    filters = tf.reshape(
        input_,
        [ tf.shape(input_)[0], -1]
    )
    gram = tf.linalg.matmul(filters, filters, transpose_b=True)
    return gram