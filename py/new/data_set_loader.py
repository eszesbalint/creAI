import tensorflow as tf
import schematic

def int_to_bin_vec(x):
    return tf.bitwise.bitwise_and(
        x,
        [32768,16384,8192,4096,2048,1024,512,256,128,64,32,16,8,4,2,1]
        )

def tensor_to_bin(t):
    return tf.cast(
            tf.map_fn(
                lambda x: tf.map_fn(
                    lambda y: tf.map_fn(
                        lambda z: int_to_bin_vec(z)
                        ,y)
                    ,x)
                , elems = t)
            , dtype=tf.bool
        )

def crop_rand(T, size=(64,64,64,16), n=512):
    T_crops = [tf.image.random_crop(T, size=size)]
    #for tensor in T:
    for i in range(n-1):
        cropped_tensor = tf.image.random_crop(T, size=size)
        T_crops = tf.concat([T_crops,[cropped_tensor]], 0)
    return T_crops

def parse_fn(example):

  example_fmt = {
    'size': tf.io.FixedLenFeature([3], tf.int64),
    'data': tf.io.VarLenFeature(tf.int64),
  }
  parsed = tf.io.parse_single_example(example, example_fmt)
  data = tf.sparse.to_dense(parsed['data'])
  data = tf.reshape(data,parsed['size'])
  data = tf.image.random_crop(tensor_to_bin(data),size=(64,64,64,16))
  data = tf.cast(data, tf.bool)
  return data, data

def input_fn():
  files = tf.data.Dataset.list_files("./training_data/*.tfrecord")
  dataset = files.interleave(tf.data.TFRecordDataset,cycle_length=1)
  dataset = dataset.shuffle(buffer_size=10000)
  dataset = dataset.map(map_func=parse_fn)
  dataset = dataset.batch(batch_size=128)
  return dataset

input_fn()

#def tfdata_generator(images, labels, is_training, batch_size=128):
#    '''Construct a data generator using tf.Dataset'''
#
#    def preprocess_fn(image, label):
#        '''A transformation function to preprocess raw data
#        into trainable input. '''
#        x = tf.reshape(tf.cast(image, tf.float32), (28, 28, 1))
#        y = tf.one_hot(tf.cast(label, tf.uint8), _NUM_CLASSES)
#        return x, y
#
#    dataset = tf.data.Dataset.from_tensor_slices((images, labels))
#    if is_training:
#        dataset = dataset.shuffle(1000)  # depends on sample size
#
#    # Transform and batch data at the same time
#    dataset = dataset.apply(tf.contrib.data.map_and_batch(
#        preprocess_fn, batch_size,
#        num_parallel_batches=4,  # cpu cores
#        drop_remainder=True if is_training else False))
#    dataset = dataset.repeat()
#    dataset = dataset.prefetch(tf.contrib.data.AUTOTUNE)
#
#    return dataset

