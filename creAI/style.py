"""Style module.

This module implements a class that wraps machine learning models into
an abstraction closely related to presistance.
"""
import io
import json
import re
import sys
from os import PathLike, listdir, mkdir, walk, remove, rename
from os.path import abspath, dirname, exists, isdir, isfile, join, relpath
from shutil import rmtree, make_archive
from typing import List
from zipfile import ZipFile
import numpy as np
from PIL import Image

from creAI.exceptions import *
import creAI.mc.version_manager as vm
from creAI.mc import Tile, Tilemap, Schematic


# Creating styles folder
if getattr(sys, 'frozen', False):
    # If creAI is packaged into an executable
    STYLES_PATH = join(sys._MEIPASS, 'styles')
else:
    # If creAI is run from source
    STYLES_PATH = join(dirname(__file__), 'styles')

if not exists(STYLES_PATH):
    mkdir(STYLES_PATH)



class Style(object):
    """Style class.

    The task of the Style class is to wrap machine learning models into an 
    abstraction that is easy for users to interpret, and this abstraction is 
    closely related to persistence. Each style has a compressed file from 
    which the original style object can be generated. In this way, the user 
    can copy, delete, share styles with simple file operations. 
    Styles are identified by file name.

    Args:
        stl_name (str): The name of the style.
        mc_version (str, optional): The Minecraft version of the generated 
            tilemaps.
        icon_pth (os.PathLike, optional): Path to an image file. This will
            be shown in the graphical user interface.
        load_models (bool, optional): Wether or not to load the machine
            learning models from the style file if the style already exists.

    Attributes:
        name (str): Name of the style, should only contain alphanumeric
            characters and underscores.
        file_name (str): The name of the style plus the file extention.
        path (os.PathLike): The full path of the style file.
        tmp_folder (os.PathLike): Temporary folder for exracting and 
            compression.
        icon (PIL.Image): The icon of the style.
        info (StyleInfo): Other information about the style, like the 
            Minecraft version, in a dictionary-like structure.
        palette (StyleInfo): The encoding dictionary of tiles, used in
            generation.
    """

    _extention = 'creai'

    def __init__(self, stl_name: str, mc_version: str = None,
                 icon_pth: PathLike = None, load_models=True):
        self._name = StyleName()(stl_name)
        self._icon = StyleIcon(self, src=icon_pth)
        self.info = StyleInfo(self, 'info')
        self.models = StyleModels(self)
        self.palette = StyleInfo(self, 'palette')
        self.load(load_models)

        if mc_version is not None:
            self.info['mc_version'] = mc_version

    @property
    def name(self):
        return self._name

    @property
    def file_name(self):
        return '{}.{}'.format(self._name, self._extention)

    @property
    def path(self):
        return join(STYLES_PATH, self.file_name)

    @property
    def tmp_folder(self):
        return join(STYLES_PATH, '{}_tmp'.format(self.name))

    @property
    def icon(self):
        return self._icon

    def train(self, vae=True, generator=True,
              schem_pth: PathLike = None, batch_size=128, epochs=100):
        """Training a style for a specific tilemap.

        Training takes place in two steps. First, a variation autoencoder is 
        trained to encode all existing blockstates of a given Minecraft 
        version. Tiles are passed to the model as vectors, and a 
        low-dimensional representation of them is obtained during training. 
        Because the vectors are created based on the properties of the 
        three-dimensional models of the tile, the visually similar blocks in 
        the latent-space are close to each other. Tiles and their associated 
        codes are saved in a dictionary.
        We then teach a convolutional upscaling network (generator) that 
        generates random noise tensors into the latent-space of the 
        variational autoencoder, thus generating tilemaps. The size of the 
        input noise tensor determines its output, the ratio of the two 
        is 1: 8. During training, the size of the input is varied at random, 
        for which the RandomNoise class is responsible. The generator grid is 
        taught to minimize a so-called 'feature-loss'.

        Args:
            vae (bool, optional): Training the VAE part of the model.
            generator (bool, optional): Training the generator part of the
                model.
            schem_pth (os.PathLike, optional): Path to the schematic of the 
                example tilemap.
            batch_size (int, optional): Batch size.
            epochs (int, optional): Number of epochs.

        """
        # Importing Tensorflow libraries
        import tensorflow as tf
        from tensorflow.keras.callbacks import Callback
        tf.compat.v1.disable_eager_execution()
        
        # Importing the the implementation of the different parts of the model
        from creAI.ml.models import VAE, GeneratorNetwork
        from creAI.ml.data_generators import RandomNoise
        from creAI.ml.train import init_generator, init_vae, train_generator, train_vae
        
        # Defining a custom callback function that saves the whole style at
        # the end of each epoch.
        class StyleTrainingCallback(Callback):
            def __init__(self, style: Style):
                self.style = style

            def on_epoch_end(self, epoch, logs=None):
                self.style.save()

        mc_version = self.info['mc_version']

        # Training VAE
        if vae:
            print('Loading training data...')
            # Vectorizing all tiles from the given Minecraft version
            vae_data = Tile.vectorize_all(mc_version)
            # Init VAE
            self.models.vae = init_vae(vae_data.shape[-1], 2, self.models.vae)
            # Train
            train_vae(
                self.models.vae, vae_data,
                batch_size=batch_size, epochs=epochs,
                callbacks=[StyleTrainingCallback(self)]
            )
        
        # Training the generator
        if generator:
            if self.models.vae is None:
                raise VAEModelMissing(self.name)

            # Opening example tilemap
            with open(schem_pth, 'rb') as schem_file:
                tlmp = Schematic.load(schem_file, version=mc_version)
            
            # Encoding the tilemap's palette with the previously trained VAE
            encoded_palette = self.models.vae.encoder.predict(
                tlmp.palette_to_vecs(pad_to=self.models.vae.input_dim)
            )[0]

            # Saving encoding
            for tile, z in zip(tlmp.palette, encoded_palette):
                self.palette[str(tile)] = z.tolist()

            # Mapping codes to the data array of the tilemap, thus creating a
            # 4D tensor.
            mapped = np.array([encoded_palette[idx]
                               for idx in list(tlmp.data.flat)])
            encoded_tlmp = mapped.reshape(
                tlmp.shape+(self.models.vae.latent_dim,))

            # Init generator
            self.models.generator = init_generator(
                encoded_tlmp, 256, self.models.vae.latent_dim, self.models.generator)

            # Creating random training data and validation data.
            data_generator = RandomNoise(
                10000, channels=self.models.generator.input_channels, 
                batch_size=batch_size, min_shape=[2,2,2], max_shape=[3,3,3],
                seed=0)
            validation_data_generator = RandomNoise(
                100, channels=self.models.generator.input_channels, 
                batch_size=batch_size, min_shape=[2,2,2], max_shape=[3,3,3],
                seed=12345)

            # Training
            self.models.generator.model.fit(
                            data_generator, 
                            epochs=epochs,
                            validation_data=validation_data_generator,
                            callbacks=[StyleTrainingCallback(self)])

        
    def generate(self, shape):
        """Generate tilemap with the style.

        Runs the generator part of the model on a random tensor and maps the
        resulting 4D tensor's last dimension to Minecraft tiles, thus creating
        a 3D tilemap.

        Args:
            shape (tuple of int): Size of the generated tilemap.
        """
        # Importing Tensorflow
        import tensorflow as tf

        # Defining input shapes
        in_w, in_h, in_l = (max(s//8, 1) for s in shape)
        c = self.models.generator.input_channels

        # Generating random noise
        random_noise = np.random.normal(size=(1,in_w,in_h,in_l,c))

        # (Re)comping the generator model
        self.models.generator.model.compile(loss=tf.keras.losses.mean_squared_error, optimizer='adam')

        # Run the network on the random noise
        pred = self.models.generator.model.predict(random_noise)
        print(pred)

        w, h, l, latent_dim = pred.shape[1:5]

        palette = list([Tile(id_) for id_ in self.palette.keys()])
        encoded_palette = np.array(list(self.palette.values()))

        #Finding nearest latent vectors for pred
        block_data = np.linalg.norm(
            pred.reshape((1,w,h,l,1,latent_dim)) - encoded_palette.reshape((1,1,1,1,-1,latent_dim)), 
            axis=-1
        ).argmin(axis=-1).reshape((w,h,l))
        print(block_data)

        tlmp = Schematic(data=block_data, palette=palette, 
                         version=self.info['mc_version'])

        return tlmp

    def load(self, load_models=True):
        # Removing temp folder
        rmtree(self.tmp_folder, ignore_errors=True)
        # Recreating temp folder
        mkdir(self.tmp_folder)
        # If style file exists extract it to the temp folder
        if exists(self.path):
            with ZipFile(self.path, 'r') as z_file:
                z_file.extractall(self.tmp_folder)

        # Load different part of the style
        self._icon.load()
        self.info.load()
        if load_models:
            self.palette.load()
            self.models.load()

        # Remove temp folder
        rmtree(self.tmp_folder, ignore_errors=True)

    def save(self):
        # Remove temp folder
        rmtree(self.tmp_folder, ignore_errors=True)
        # Recreate temp folder
        mkdir(self.tmp_folder)

        # Save different parts of the style to temp folder
        self._icon.save()
        self.info.save()
        self.models.save()
        self.palette.save()
        
        # Creating a temporal style file
        make_archive(self.path, 'zip', self.tmp_folder)

        # Remove previous style file
        if exists(self.path):
            remove(self.path)
        
        # Rename temporal style file
        rename(
            self.path+'.zip',
            self.path
        )

        # Remove temp folder
        rmtree(self.tmp_folder, ignore_errors=True)

    @classmethod
    def list_all(cls):
        """Lists all styles in the styles/ folder.

        Returns:
            list of str: List of the names of available styles. 
        """
        stl_list = [d.split('.')[0]
                    for d in listdir(STYLES_PATH)
                    if isfile(join(STYLES_PATH, d))
                    and d.split('.')[-1] == cls._extention]
        return stl_list


class StyleName(object):
    def __call__(self, stl_name):
        stl_name = str(stl_name)
        if re.match(r'^[A-z0-9_]+$', stl_name) is None:
            raise InvalidStyleName(stl_name)

        return stl_name


class StyleIcon(object):
    def __init__(self, parent: Style, src: PathLike = None):
        self.parent = parent
        self._img = None
        self._src = src

    @property
    def image(self):
        return self._img

    def load(self):
        pth = join(self.parent.tmp_folder, 'icon.png')
        if exists(pth) and self._src is None:
            self._img = Image.open(pth)
        elif self._src is not None and exists(self._src):
            self._img = Image.open(self._src)
        elif self._src is not None:
            raise IconFileMissing(self._src)

    def save(self):
        pth = join(self.parent.tmp_folder, 'icon.png')
        if self._img is not None:
            self._img.save(pth, format='PNG')

    def to_byte_array(self):
        if self._img is not None:
            buffer = io.BytesIO()
            self._img.save(buffer, format='PNG')
            return bytearray(buffer.getvalue())
        else:
            return bytearray([])


class StyleInfo(object):
    def __init__(self, parent, name):
        self.parent = parent
        self._name = name
        self._dict = {}

    @property
    def file_name(self):
        return '{}.json'.format(self._name)

    def load(self):
        pth = join(self.parent.tmp_folder, self.file_name)
        if exists(pth):
            with open(pth, 'r') as info_file:
                self._dict = json.load(info_file)

    def save(self):
        pth = join(self.parent.tmp_folder, self.file_name)
        with open(pth, 'w') as info_file:
            json.dump(self._dict, info_file)

    def __getitem__(self, key):
        if key in self._dict.keys():
            return self._dict[key]
        else:
            return None

    def __setitem__(self, key, val):
        self._dict[key] = val

    def items(self):
        return self._dict.items()

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()


class StyleModels(object):
    def __init__(self, parent):
        self.parent = parent
        self.vae = None
        self.generator = None

    def load(self):
        from creAI.ml.models import VAE, GeneratorNetwork

        pth = join(self.parent.tmp_folder, 'models')
        vae_pth = join(pth, 'vae')
        g_pth = join(pth, 'generator')

        self.vae = None
        if exists(vae_pth):
            self.vae = VAE.load(vae_pth)

        self.generator = None
        if exists(g_pth):
            self.generator = GeneratorNetwork.load(g_pth)

    def save(self):
        pth = join(self.parent.tmp_folder, 'models')
        vae_pth = join(pth, 'vae')
        g_pth = join(pth, 'generator')

        if self.vae is not None:
            self.vae.save(vae_pth)

        if self.generator is not None:
            self.generator.save(g_pth)



