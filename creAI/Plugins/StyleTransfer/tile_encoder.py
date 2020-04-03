
x_train = None

from keras.models import Model
from keras.layers import Dense,Input,GaussianNoise
from keras.losses import categorical_crossentropy
from keras.optimizers import SGD

#Implementing the autoencoder
input_vector = Input(shape=(INPUT_SIZE,))
noise = GaussianNoise(0.01)(input_vector)

encode_1 = Dense(512,activation='relu')(noise)
encode_2 = Dense(256,activation='relu')(encode_1)
encode_3 = Dense(128,activation='relu')(encode_2)
encoded = Dense(ENCODED_SIZE,activation='sigmoid')(encode_3)

decode_1 = Dense(128,activation='relu')(encoded)
decode_2 = Dense(256,activation='relu')(decode_1)
decode_3 = Dense(512,activation='relu')(decode_2)
decoded = Dense(INPUT_SIZE, activation='softmax')(decode_3)

autoencoder = Model(input_vector, decoded)
encoder = Model(input_vector, encoded)
encoded_input = Input(shape=(ENCODED_SIZE,))


autoencoder.compile(optimizer=SGD(lr=0.1, momentum=0.9, nesterov=True),loss='categorical_crossentropy')
autoencoder.fit(x_train,x_train,epochs=1000,batch_size=1000)

#Saving the trained model
encoder.save('encoder.h5')
decoder.save('decoder.h5')


