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


import creAI.mc.version_manager as vm
from creAI.mc import Tile, Tilemap, Schematic


if getattr(sys, 'frozen', False):
    STYLES_PATH = join(sys._MEIPASS, 'styles')
else:
    STYLES_PATH = join(dirname(__file__), 'styles')

if not exists(STYLES_PATH):
    mkdir(STYLES_PATH)



class Style(object):
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
        import tensorflow as tf
        from tensorflow.keras.callbacks import Callback
        tf.compat.v1.disable_eager_execution()
        

        from creAI.ml.models import VAE, GeneratorNetwork
        from creAI.ml.data_generators import RandomNoise
        from creAI.ml.train import init_generator, init_vae, train_generator, train_vae
        

        class StyleTrainingCallback(Callback):
            def __init__(self, style: Style):
                self.style = style

            def on_epoch_end(self, epoch, logs=None):
                self.style.save()

        mc_version = self.info['mc_version']

        if vae:
            # Training VAE
            print('Loading training data...')
            vae_data = Tile.vectorize_all(mc_version)
            self.models.vae = init_vae(vae_data.shape[-1], 2, self.models.vae)
            train_vae(
                self.models.vae, vae_data,
                batch_size=batch_size, epochs=epochs,
                callbacks=[StyleTrainingCallback(self)]
            )
            


        if generator:
            if self.models.vae is None:
                raise FileNotFoundError(
                    'You have to train the VAE model first for {}'.format(self._name))


            

            # Training generator network
            with open(schem_pth, 'rb') as schem_file:
                tlmp = Schematic.load(schem_file, version=mc_version)


            encoded_palette = self.models.vae.encoder.predict(
                tlmp.palette_to_vecs(pad_to=self.models.vae.input_dim)
            )[0]

            
            for tile, z in zip(tlmp.palette, encoded_palette):
                self.palette[str(tile)] = z.tolist()

            mapped = np.array([encoded_palette[idx]
                               for idx in list(tlmp.data.flat)])
            encoded_tlmp = mapped.reshape(
                tlmp.shape+(self.models.vae.latent_dim,))
            self.models.generator = init_generator(
                encoded_tlmp, 128, self.models.vae.latent_dim, self.models.generator)

            data_generator = RandomNoise(
                1000, channels=self.models.generator.input_channels, 
                batch_size=batch_size, min_shape=[2,2,2], max_shape=[4,4,4],
                seed=0)
            validation_data_generator = RandomNoise(
                100, channels=self.models.generator.input_channels, 
                batch_size=batch_size, min_shape=[2,2,2], max_shape=[4,4,4],
                seed=1)
            self.models.generator.model.fit(
                            data_generator, 
                            epochs=epochs,
                            validation_data=validation_data_generator,
                            callbacks=[StyleTrainingCallback(self)])

        

    def generate(self, shape):
        import tensorflow as tf
        

        in_w, in_h, in_l = (max(s//8, 1) for s in shape)
        c = self.models.generator.input_channels
        
        random_noise = np.random.normal(size=(1,in_w,in_h,in_l,c))
        self.models.generator.model.compile(loss=tf.keras.losses.mean_squared_error, optimizer='adam')
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
        rmtree(self.tmp_folder, ignore_errors=True)
        mkdir(self.tmp_folder)
        if exists(self.path):
            with ZipFile(self.path, 'r') as z_file:
                z_file.extractall(self.tmp_folder)

        self._icon.load()
        self.info.load()
        if load_models:
            self.palette.load()
            self.models.load()

        rmtree(self.tmp_folder, ignore_errors=True)

    def save(self):
        rmtree(self.tmp_folder, ignore_errors=True)
        mkdir(self.tmp_folder)

        self._icon.save()
        self.info.save()
        self.models.save()
        self.palette.save()

        make_archive(self.path, 'zip', self.tmp_folder)
        if exists(self.path):
            remove(self.path)
        rename(
            self.path+'.zip',
            self.path
        )
        rmtree(self.tmp_folder, ignore_errors=True)

    @classmethod
    def list_all(cls):
        stl_list = [d.split('.')[0]
                    for d in listdir(STYLES_PATH)
                    if isfile(join(STYLES_PATH, d))
                    and d.split('.')[-1] == cls._extention]
        return stl_list


class StyleName(object):
    def __call__(self, stl_name):
        stl_name = str(stl_name)
        if re.match(r'^[A-z0-9_]+$', stl_name) is None:
            raise ValueError('Style names should only contain alphanumeric '
                             'characters and underscores. \'{}\' is an invalid '
                             'name.'.format(stl_name))

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



