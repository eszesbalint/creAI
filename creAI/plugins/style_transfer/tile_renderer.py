
import numpy as np

import tensorflow as tf
from tensorflow.keras.layers import Layer

try:
    import dirt
    import dirt.matrices
except ModuleNotFoundError:
    raise NotImplementedError(
        "Differential rendering without GPU support is not implemented yet! "
        "Make sure to install the necessary dependencies to use this feature!"
        )


class Tile_Renderer(Layer):
    """Differentiable tilemap renderer layer"""

    def __init__(self, output_dim, name='tile_renderer', **kwargs):
        super(Tile_Renderer, self).__init__(name=name, **kwargs)
        self.output_dim = output_dim

    def call(self, inputs):
        """Builds the computational graph for differentiable rendering"""

        input_ = inputs
        b = tf.shape(input_)[0]         # Batch size
        v, c, f = self._geom_from_vec_repr(input_)

        # Convert vertices to homogeneous coordinates
        v = tf.concat([
            v,
            tf.ones_like(v[:, :, -1:])
        ], axis=-1)

        # Transforming vertices from object space to world space
        v_world = tf.matmul(
            v, dirt.matrices.translation([-25., -20., -25.]))

        # Transforming vertices from world space to camera space
        view_matrix = dirt.matrices.compose(
            # translate it away from the camera
            dirt.matrices.translation([0., 0., 0.]),
            dirt.matrices.rodrigues([ -0.7853982, 0., 0.]),
            dirt.matrices.rodrigues([ 0., 0.7853982, 0.]),
            dirt.matrices.rodrigues([ 0., 0., 0.7853982]),
        )
        v_camera = tf.matmul(v_world, view_matrix)

        # Transforming vertices from camera space to clip space
        v_clip = tf.matmul(
            v_camera,
            self._ortho(
                scaling=100.,
                near=.1,
                far=1000.,
                aspect=self.output_dim[-2] / self.output_dim[-3]
            )
        )

        output = dirt.rasterise_batch(
            vertices=v_clip,
            faces=f,
            vertex_colors=c,
            background=tf.zeros(shape=[b]+self.output_dim[-3:]),
        )

        return output

    @staticmethod
    def _geom_from_vec_repr(input_):
        """Transforms vector representation to vertices, vertex colors and faces.

        Args:
            input_: a batch of 3D tensors of 1D vector representations, 5D in total

        Returns:
            v: vertices of the tilemap
            c: vertex colors of the tilemap
            f: faces of the tilemap, defined by indices of vertices

        Each vector represents the geometric shape and color of each
        tile in the tilemap.
        The geometric shape of a tile is defined by axis aligned boxes (cuboids).
        The cuboids are defined by two coordinates (from, to) and 6 RGB colors,
        8 float vectors of length 3 in total. The values are clamped between 
        0 and 1.

        Each tile has the same number of cuboids, but some of the cuboids
        will have negligibly small sizes:
        to - from ~ 0.
        """
        input_ = tf.cast(input_, dtype=tf.float32)

        b = tf.shape(input_)[0]         # Batch size
        w = tf.shape(input_)[-4]
        h = tf.shape(input_)[-3]
        l = tf.shape(input_)[-2]
        # Number of axis aligned cuboid elements in a minecraft tile model
        e = tf.math.floordiv(tf.shape(input_)[-1], 8*3)

        # Reshaping the vector representations of minecraft tiles
        # from (e*8*3,) to (e,8,1,3)
                                       #[1, 1, 1, 1, 1, 6, 2, 3, 3]
        elements = tf.reshape(input_,   [b, w*h*l, e, 8, 1, 1, 3])

        # Extracting the location of the axis aligned boxes' corners
                        #[1,42,60,51, 2, 1, 1, 3]
        from_ = elements[ :, :, :, 0:1]
        to = elements[ :, :, :, 1:2]

        colors = elements[ :, :, :, 2:]

        # Generating the geometry of a unit cube
        v_cube = [
            [x, y, z]
            for z in [0., 1.]
            for y in [0., 1.]
            for x in [0., 1.]
        ]
        v_cube = [
            [[v_cube[0], v_cube[1], v_cube[3]],
                [v_cube[3], v_cube[2], v_cube[0]]],  # back
            [[v_cube[4], v_cube[5], v_cube[7]],
                [v_cube[7], v_cube[6], v_cube[4]]],  # front
            [[v_cube[1], v_cube[5], v_cube[4]],
                [v_cube[4], v_cube[0], v_cube[1]]],  # bottom
            [[v_cube[2], v_cube[6], v_cube[7]],
                [v_cube[7], v_cube[3], v_cube[2]]],  # top
            [[v_cube[4], v_cube[6], v_cube[2]],
                [v_cube[2], v_cube[0], v_cube[4]]],  # left
            [[v_cube[3], v_cube[7], v_cube[5]],
                [v_cube[5], v_cube[1], v_cube[3]]],  # right
        ]

        # Transforming the unit cube to match the dimensions defined
        # in from_ and to.
        v_cube = tf.reshape(v_cube, [1, 1, 1, 6, 2, 3, 3])
        v = v_cube*(to-from_) + from_
        # v's shape is now [b,w,h,l,e,6,2,3,3]

        # Generating the origins of each tile
        x = tf.reshape(
            tf.range(0., tf.cast(w, dtype=tf.float32)),
            [w, 1, 1, 1]
        )
        x = tf.broadcast_to(x, [w, h, l, 1])
        y = tf.reshape(
            tf.range(0., tf.cast(h, dtype=tf.float32)),
            [1, h, 1, 1]
        )
        y = tf.broadcast_to(y, [w, h, l, 1])
        z = tf.reshape(
            tf.range(0., tf.cast(l, dtype=tf.float32)),
            [1, 1, l, 1]
        )
        z = tf.broadcast_to(z, [w, h, l, 1])

        o = tf.concat([x, y, z], axis=-1)
        o = tf.reshape(o, [1, w*h*l, 1, 1, 1, 1, 3])
        o = tf.broadcast_to(o, [b, w*h*l, e, 6, 2, 3, 3])

        # Translating vertices by origins
        v = v + o

        # Generating vertex colors
        c = tf.reshape(colors, [b, w*h*l, e, 6, 1, 1, 3])
        c = tf.broadcast_to(c, [b, w*h*l, e, 6, 2, 3, 3])

        # Flattening vertex tensor
        v = tf.reshape(v, [b, w*h*l*e*6*2*3, 3])

        # Flattening vertex color tensor
        c = tf.reshape(c, [b, w*h*l*e*6*2*3, 3])

        # Generating face indices
        f = tf.range(0, b*w*h*l*e*6*2*3, dtype=tf.int32)
        f = tf.reshape(f, [b, w*h*l*e*6*2, 3])
        f = tf.broadcast_to(f, [b, w*h*l*e*6*2, 3])

        return v, c, f

    @staticmethod
    def _ortho(scaling, near, far, aspect):
        w = scaling
        h = scaling*aspect
        projection_matrix = [
            [2./w, 0., 0., 0.],
            [0., 2./h, 0., 0.],
            [0., 0., -1./(far-near), -near/(far-near)],
            [0., 0., 0., 1.]
        ]
        return tf.transpose(
            tf.convert_to_tensor(projection_matrix, dtype=tf.float32)
        )
