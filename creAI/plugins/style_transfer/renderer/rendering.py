import math
import numpy as np
import dirt
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()


class Renderer():
    def __init__(self, ):

    def build():

    @classmethod
    def _geom_from_vec_repr(input_):
        v_cube = [[x, y, z] for z in [-1, 1] for y in [-1, 1] for x in [-1, 1]]
        q_cube = [
            [0, 1, 3, 2], [4, 5, 7, 6],  # back, front
            [1, 5, 4, 0], [2, 6, 7, 3],  # bottom, top
            [4, 6, 2, 0], [3, 7, 5, 1],  # left, right
        ]


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
