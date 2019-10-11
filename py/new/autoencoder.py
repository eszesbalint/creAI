import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense,Input,Conv3D,MaxPooling3D,Conv3DTranspose,UpSampling3D,Flatten,Reshape
from tensorflow.keras.losses import categorical_crossentropy
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.utils import plot_model
import data_set_loader as loader

INPUT_SHAPE = (64,64,64,16,)
ENCODED_SIZE = 128

#Implementing the autoencoder
input_tensor = Input(shape=INPUT_SHAPE)

conv_1 = Conv3D(64, (3,3,3), padding='same')(input_tensor)
maxpool_1 = MaxPooling3D(pool_size=(2, 2, 2), padding='same')(conv_1)

conv_2 = Conv3D(128, (3,3,3), padding='same')(maxpool_1)
maxpool_2 = MaxPooling3D(pool_size=(2, 2, 2), padding='same')(conv_2)

conv_3 = Conv3D(256, (3,3,3), padding='same')(maxpool_2)
maxpool_3 = MaxPooling3D(pool_size=(2, 2, 2), padding='same')(conv_3)

conv_4 = Conv3D(512, (3,3,3), padding='same')(maxpool_3)
maxpool_4 = MaxPooling3D(pool_size=(2, 2, 2), padding='same')(conv_4)


flatten_1 = Flatten()(maxpool_4)

dense_1 = Dense(256,activation='relu')(flatten_1)
dense_2 = Dense(ENCODED_SIZE,activation='sigmoid')(dense_1)
dense_3 = Dense(256,activation='relu')(dense_2)

reshape_1 = Reshape((4,4,4,512,))(dense_3)

upsample_1 = UpSampling3D(size=(2, 2, 2))(reshape_1)
deconv_1 = Conv3DTranspose(256, (3,3,3), padding='same')(upsample_1)

upsample_2 = UpSampling3D(size=(2, 2, 2))(deconv_1)
deconv_2 = Conv3DTranspose(128, (3,3,3), padding='same')(upsample_2)

upsample_3 = UpSampling3D(size=(2, 2, 2))(deconv_2)
deconv_3 = Conv3DTranspose(64, (3,3,3), padding='same')(upsample_3)

upsample_4 = UpSampling3D(size=(2, 2, 2))(deconv_3)
deconv_4 = Conv3DTranspose(16, (3,3,3), padding='same')(upsample_4)


encoded = dense_2
decoded = deconv_4

autoencoder = Model(input_tensor, decoded)
encoder = Model(input_tensor, encoded)

autoencoder.summary()
#plot_model(autoencoder, to_file='autoencoder.png', show_shapes=True, show_layer_names=True)

x_train = loader.input_fn()

autoencoder.compile(optimizer=SGD(lr=0.1, momentum=0.9, nesterov=True),loss='binary_crossentropy')
autoencoder.fit(x_train,epochs=1000)

#Saving the trained model
#encoder.save('encoder.h5')
#decoder.save('decoder.h5')


