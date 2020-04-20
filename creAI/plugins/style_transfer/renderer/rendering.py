import math
import numpy as np
import dirt
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()


class Tile_Renderer(tf.keras.layers.Layer):
    """Differentiable tilemap renderer model"""
    def __init__(self, output_dim):
        self.output_dim = output_dim

    def build(self):
        """Builds the computational graph for differentiable rendering
        
        Returns:
            tf.keras.Model
        """

        input_ = tf.keras.layers.Input(shape=(None, None, None, 1))
        camera_angle = tf.keras.layers.Input(shape=(3,))

        output = self._render(input_, camera_angle)
        
        renderer = tf.keras.Model([input_, camera_angle], output)

    def _render():
        

    @staticmethod
    def _geom_from_vec_repr(input_):
        """ Transforms vector representation to vertices, vertex colors and faces.

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

        b = input_.shape[0]         # Batch size
        w = input_.shape[-4]
        h = input_.shape[-3] 
        l = input_.shape[-2]
        e = input_.shape[-1] / 8*3  # Number of axis aligned cuboid elements in a minecraft tile model

        # Reshaping the vector representations of minecraft tiles
        # from (e*8*3,) to (e,8,1,3)
        elements = tf.reshape(input_, [b,w,h,l,e,8,1,3])

        # Extracting the location of the axis aligned boxes' corners
        from_ = elements[:,:,:,:,:,0]
        to = elements[:,:,:,:,:,1]

        # Generating the geometry of a unit cube
        v_cube = [[x, y, z] for z in [0, 1] for y in [0, 1] for x in [0, 1]]
        f_cube = [
            [0, 1, 3, 2], [4, 5, 7, 6],  # back, front
            [1, 5, 4, 0], [2, 6, 7, 3],  # bottom, top
            [4, 6, 2, 0], [3, 7, 5, 1],  # left, right
        ]

        # Transforming the unit cube to match the dimensions defined
        # in from_ and to.
        tf.reshape(v_cube, [1,1,1,1,1,8,3])
        v = v_cube*(to-from_) + from_
        # v's shape is now [b,w,h,l,e,8,3]

        return v, c, f


frame_width, frame_height = 1024, 1024


def orthographic_projection(scaling, near, far, aspect):
    w = scaling
    h = scaling*aspect
    projection_matrix = [
        [2./w, 0., 0., 0.],
        [0., 2./h, 0., 0.],
        [0., 0., -1./(far-near), -near/(far-near)],
        [0., 0., 0., 1.]
    ]
    return tf.transpose(tf.convert_to_tensor(projection_matrix, dtype=tf.float32))


def generate_view_matrices(number_of_views, distance=100.):
    # Fibonacci sphere algorithm
    points = []
    anlges = []
    offset = 2./number_of_views
    increment = math.pi * (3. - math.sqrt(5.))
    for i in range(number_of_views):
    y = ((i * offset) - 1) + (offset / 2)
    r = math.sqrt(1 - pow(y, 2))
    ro = math.atan(y/r)
    phi = ((i + 1) % number_of_views) * increment
    x = math.sin(phi) * r
    z = math.cos(phi) * r
    anlges.append([phi, ro])
    points.append([x, y, z])
    view_matrices = []
    for [x, y, z], [phi, ro] in zip(points, anlges):
    view_matrix = matrices.compose(
        # translate it away from the camera
        matrices.translation([-x*distance, -y*distance, -z*distance]),
        matrices.rodrigues([0., math.pi/2 - phi, 0.]),  # rotate the view
        matrices.rodrigues([math.pi/2 - ro, 0., 0.])  # tilt the view
    )
    view_matrices.append(view_matrix)
    return tf.stack(view_matrices)


def build_cubes(input_tensor, input_shape):
    w, h, l = input_shape
    indicies_array = np.concatenate(np.indices([w, h, l, 1]), 3)[:, :, :, :-1]
    origins = tf.reshape(tf.constant(
        indicies_array, dtype=tf.float32), [w, h, l, 1, 3])
    cube_vertices = np.reshape([[x, y, z] for z in [-1, 1]
                                for y in [-1, 1] for x in [-1, 1]], (1, 1, 1, 8, 3))
    vertices = tf.reshape(origins + tf.reshape(input_tensor[:, :, :, 0], [
                          w, h, l, 1, 1]) * .5 * cube_vertices, [w*h*l*8, 3])
    triangles = np.concatenate(
        np.reshape([
            [0, 1, 3], [3, 2, 0], [4, 5, 7], [7, 6, 4],  # back, front
            [1, 5, 4], [4, 0, 1], [2, 6, 7], [7, 3, 2],  # bottom, top
            [4, 6, 2], [2, 0, 4], [3, 7, 5], [5, 1, 3],  # left, right
        ], (1, 12, 3)) + np.arange(w*h*l).reshape((w*h*l, 1, 1))*8
    )
    vertex_colors = tf.reshape(
        tf.broadcast_to(
            tf.reduce_sum(
                tf.reshape(input_tensor[:, :, :, 1:], [w, h, l, 1, 3, 5]) * np.asarray(
                    [2**(4-n) for n in range(5)]).reshape([1, 1, 1, 1, 1, 5]),
                axis=-1) / 32.,
            [w, h, l, 8, 3]),
        [w*h*l*8, 3])
    return vertices, triangles, vertex_colors


def unit(vector):
    return tf.convert_to_tensor(vector) / tf.norm(vector)


def render(input_tensor, input_shape):
    cube_vertices_object, cube_faces_unsplit, cube_vertex_colors = build_cubes(
        input_tensor, input_shape)
    cube_vertices_object, cube_faces = lighting.split_vertices_by_face(
        cube_vertices_object, cube_faces_unsplit)
    cube_vertex_colors, cube_faces = lighting.split_vertices_by_face(
        cube_vertex_colors, cube_faces_unsplit)

    # Convert vertices to homogeneous coordinates
    cube_vertices_object = tf.concat([
        cube_vertices_object,
        tf.ones_like(cube_vertices_object[:, -1:])
    ], axis=1)

    # Transform vertices from object to world space, by rotating around the vertical axis
    cube_vertices_world = tf.matmul(
        cube_vertices_object, matrices.translation([-32., -32., -32.]))

    # Transform vertices from world to camera space; note that the camera points along the negative-z axis in camera space
    # view_matrix = matrices.compose(
    #	matrices.translation([0., -1.5*100, -3.5*100]),  # translate it away from the camera
    #	matrices.rodrigues([-0.4, 0., 0.])  # tilt the view downwards
    # )
    cube_vertices_camera = tf.matmul(
        cube_vertices_world, generate_view_matrices(100)[9])

    # Transform vertices from camera to clip space

    cube_vertices_clip = tf.matmul(cube_vertices_camera, orthographic_projection(
        scaling=100., near=.1, far=1000., aspect=float(frame_height) / frame_width))

    pixels = dirt.rasterise(
        vertices=cube_vertices_clip,
        faces=cube_faces,
        vertex_colors=cube_vertex_colors,
        background=tf.zeros([frame_height, frame_width, 3]),
        width=frame_width, height=frame_height, channels=3
    )

    return pixels
