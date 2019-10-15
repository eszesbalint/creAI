# This is a simple example rendering a 3D cube in Dirt

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

import dirt
import dirt.matrices as matrices
import dirt.lighting as lighting

import numpy as np


frame_width, frame_height = 640, 480


def build_cubes(input_tensor, input_shape):
	w, h, l = input_shape
	indicies_array = np.concatenate(np.indices([w,h,l,1]),3)[:,:,:,:-1]
	origins = tf.reshape(tf.constant(indicies_array, dtype=tf.float32), [w,h,l,1,3])
	cube_vertices = np.reshape([[x, y, z] for z in [-1, 1] for y in [-1, 1] for x in [-1, 1]], (1,1,1,8,3))
	vertices = tf.reshape(origins + tf.reshape(input_tensor[:,:,:,-1], [w,h,l,1,1]) * .5 * cube_vertices, [w*h*l*8, 3] )
	triangles = np.concatenate(
		np.reshape([
			[0, 1, 3], [3, 2, 0], [4, 5, 7], [7, 6, 4],  # back, front
			[1, 5, 4], [4, 0, 1], [2, 6, 7], [7, 3, 2],  # bottom, top
			[4, 6, 2], [2, 0, 4], [3, 7, 5], [5, 1, 3],  # left, right
		], (1,12,3)) + np.arange(w*h*l).reshape((w*h*l,1,1))*8
	)
	return vertices, triangles


def unit(vector):
	return tf.convert_to_tensor(vector) / tf.norm(vector)


def render(input_tensor, input_shape):

	# Build the scene geometry, which is just an axis-aligned cube centred at the origin in world space
	# We replicate vertices that are shared, so normals are effectively per-face instead of smoothed

	cube_vertices_object, cube_faces = build_cubes(input_tensor, input_shape)
	#cube_vertices_object = tf.constant(cube_vertices_object, dtype=tf.float32)
	cube_vertices_object, cube_faces = lighting.split_vertices_by_face(cube_vertices_object, cube_faces)
	cube_vertex_colors = tf.ones_like(cube_vertices_object)

	# Convert vertices to homogeneous coordinates
	cube_vertices_object = tf.concat([
		cube_vertices_object,
		tf.ones_like(cube_vertices_object[:, -1:])
	], axis=1)

	# Transform vertices from object to world space, by rotating around the vertical axis
	cube_vertices_world = tf.matmul(cube_vertices_object, matrices.rodrigues([0., 0.5, 0.]))

	# Calculate face normals; pre_split implies that no faces share a vertex
	cube_normals_world = lighting.vertex_normals_pre_split(cube_vertices_world, cube_faces)

	# Transform vertices from world to camera space; note that the camera points along the negative-z axis in camera space
	view_matrix = matrices.compose(
		matrices.translation([0., -1.5*100, -3.5*100]),  # translate it away from the camera
		matrices.rodrigues([-0.4, 0., 0.])  # tilt the view downwards
	)
	cube_vertices_camera = tf.matmul(cube_vertices_world, view_matrix)

	# Transform vertices from camera to clip space
	projection_matrix = matrices.perspective_projection(near=0.1, far=1000., right=0.05, aspect=float(frame_height) / frame_width)
	cube_vertices_clip = tf.matmul(cube_vertices_camera, projection_matrix)

	# Calculate lighting, as combination of diffuse and ambient
	vertex_colors_lit = lighting.diffuse_directional(
		cube_normals_world, cube_vertex_colors,
		light_direction=[1., 0., 0.], light_color=[1., 1., 1.]
	) * 0.8 + cube_vertex_colors * 0.2

	pixels = dirt.rasterise(
		vertices=cube_vertices_clip,
		faces=cube_faces,
		vertex_colors=vertex_colors_lit,
		background=tf.zeros([frame_height, frame_width, 3]),
		width=frame_width, height=frame_height, channels=3
	)

	return pixels


