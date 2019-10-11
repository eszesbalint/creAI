import tensorflow as tf
import schematic
import os
import sys

def schematics_to_tfrecords(input_folder, output_folder):
	for f in os.listdir(input_folder):
		data = schematic.load(os.path.join(input_folder,f)).asNumpyArray() 

		output_filename = os.path.join(output_folder, f + ".tfrecord")
		writer = tf.io.TFRecordWriter(output_filename)
		
		def float_feature(value):
			return tf.train.Feature(float_list=tf.train.FloatList(value=value))

		def int64_feature(value):
			return tf.train.Feature(int64_list=tf.train.Int64List(value=value))
	
		feature_dict = {
			'size': int64_feature(data.shape),
			'data': int64_feature(tf.cast(tf.reshape(data,[data.size,]), tf.int64)),
		}
	
		example = tf.train.Example(features=tf.train.Features(feature=feature_dict))
	
		writer.write(example.SerializeToString())


def main():
	schematics_to_tfrecords(sys.argv[1],sys.argv[2])
	

if __name__ == '__main__':
	main()
