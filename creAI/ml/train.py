from creAI.ml.models import VAE, GeneratorNetwork
from creAI.ml.models.dummy import DummyGeneratorNetwork
from creAI.ml.losses import vae_loss, feature_loss
from creAI.ml.losses.test_loss import test_loss
from creAI.ml.data_generators import RandomNoise

from tensorflow.keras.optimizers import Adam

def init_vae(input_dim, latent_dim, vae=None):
    if vae is None:
        #Building variational autoencoder
        vae = VAE(input_dim, latent_dim)
        vae.build()
    vae.model.add_loss(
        vae_loss(
            vae.model.input,
            vae.model.output,
            vae.encoder.output[0],
            vae.encoder.output[1],
        )
    )
    vae.model.compile(optimizer='adam')
    return vae

def init_generator(y_true, input_channels, output_channels, g=None):
    if g is None:
        #Building fully convolutional generator network
        g = GeneratorNetwork(input_channels, output_channels)
        g.build()
    loss = feature_loss(y_true,g.model.output,(5,5,5),512)
    #loss = test_loss(y_true, g.model.output)
    optimizer = Adam(learning_rate=0.1)
    g.model.compile(optimizer=optimizer, loss=loss)
    g.model.summary()
    return g


def train_vae(vae, *args, **kwargs):
    #Training VAE  
    vae.model.fit(*args, **kwargs)

def train_generator(g, *args, **kwargs):
    #Training generator network
    g.model.fit(*args, **kwargs)