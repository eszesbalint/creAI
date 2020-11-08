"""Minecraft tile module.

This module implements a flexible tile representation for 
Minecraft tiles (blocks).
"""

from os import listdir
from os.path import join, isdir, isfile, dirname, exists
import json
import re
from PIL import Image
import numpy as np
from typing import List

from creAI.mc import version_manager
from creAI.mc.exceptions import *

class Tile(object):
    """Minecraft tile class."""


    _id_regex = re.compile(r'^minecraft:([a-z0-9_]+)'
                           r'(\[[A-z0-9_]+\=[A-z0-9_]+(?:\,(?:[A-z0-9_]+\=[A-z0-9_]+))*\])?$')

    def __init__(self, id_: str, version: str = None):
        if self._id_regex.match(id_) is not None:
            self._id = id_
        else:
            raise InvalidMinecraftNamespaceID(id_)
        self._mc_vers = version


    @property
    def id(self):
        """str: The namespace id of the tile with data values.

        Examples:
            "minecraft:namespace_id[data_value_1=value,...,data_value_n=value]"
            "minecraft:namespace_id"
        """
        return self._id

    @property
    def name(self):
        """str: The namespace id of the tile."""
        return self._id_regex.match(self._id).group(1)

    @property
    def data_values(self):
        """:obj:`list` of :obj:`str`: A list of the data values extracted from the namespace id."""
        d_v = self._id_regex.match(self._id).groups(1)[-1]
        if isinstance(d_v, str):
            return d_v[1:-1].split(',')
        else:
            return ['']

    @property
    def version(self):
        """str: The tile's Minecraft version"""
        return self._mc_vers

    @version.setter
    def version(self, version):
        self._mc_vers = str(version)

    @property
    def model_3d(self):
        """dict: A json serializable object that contains the shape and
            texture paths of the tile.

        Raises:
            ModelLoadingWithUndefinedMinecraftVersion: If the version attribute
                is not defined.
        """
        if self.version is None:
            raise ModelLoadingWithUndefinedMinecraftVersion(self)

        return self.__load_mdl()


    @property
    def textures(self):
        """dict: Texture ids and their corresponding image files."""
        return self.__load_txtrs()


    def __load_mdl(self):
        """Loads the shape and texture of the tile recursively."""

        #Finding the corresponding json file in the Minecraft version's directory.
        pth = version_manager.get_path(self._mc_vers)
        bs_pth = join(pth, 'assets', 'minecraft', 'blockstates')
        mdl_pth = join(pth, 'assets', 'minecraft', 'models', 'block')
        bs = join(bs_pth, self.name+'.json')
        if not exists(bs):
            raise NoMatchFoundInBlockstates(self)
        #Load the json
        with open(bs, 'r') as bs_json:
            bs_data = json.load(bs_json)

        def truncate(s):
            """Splits string by the ``/`` character."""
            if '/' in s:
                return s.split('/')[-1]
            else:
                return s

        def sel_mdl_from(d):
            """Selects exactly one model file.

            Tiles can have multiple models which are selected randomly in-game.
            """
            if isinstance(d, list):
                return truncate(d[0]['model'])
            elif isinstance(d, dict):
                return truncate(d['model'])
            elif isinstance(d, str):
                return truncate(d)

        def trav_tree_rec(*mdl_names):
            """Traverse the model dependency tree from top to bottom.

            Tile models can have so-called parent models, from which they
            inherit their shape. A model can have multiple parents, and 
            parents can have their own parents. If we want to retrieve the 
            tile's full 3D model, we have to traverse this dependency tree,
            and combine the shapes along the way.

            Args:
                mdl_names (str): One or multiple model names.
            """
            #Textures and shapes found
            txtrs = {}
            elems = []
            for mdl_name in mdl_names:
                #Load models
                with open(join(mdl_pth, mdl_name+'.json'), 'r') as mdl_json:
                    mdl_data = json.load(mdl_json)
                #Append to textures
                if 'textures' in mdl_data:
                    txtrs.update(mdl_data['textures'])
                #Append to shapes
                if 'elements' in mdl_data:
                    elems += mdl_data['elements']
                #If the model has a parent, traverse its tree too
                elif 'parent' in mdl_data:
                    prnt_mdl_names = [sel_mdl_from(mdl_data['parent'])]
                    prnt_txtrs, prnt_elems = trav_tree_rec(*prnt_mdl_names)
                    txtrs.update(prnt_txtrs)
                    elems += prnt_elems

            return (txtrs, elems)

        #Select a single model
        if 'multipart' in bs_data:
            mdl_names = [
                sel_mdl_from(bs_data['multipart'][i]['apply'])
                for i in range(len(bs_data['multipart']))
            ]

        #Find the model that matches the most data values of the tile.
        #This makes the code compatible with a wider range of Minecraft
        #versions
        elif 'variants' in bs_data:
            max_arg = 0
            max_key = ''
            for v in bs_data['variants']:
                m_args = 0
                for arg in v.split(','):
                    if arg in self.data_values:
                        m_args += 1
                if m_args > max_arg:
                    max_arg = m_args
                    max_key = v

            if not max_arg:
                raise NoMatchFoundInBlockstates(self)

            mdl_names = [sel_mdl_from(bs_data['variants'][max_key])]

        txtrs, elems = trav_tree_rec(*mdl_names)
        if txtrs and elems:
            return {'textures': txtrs, 'elements': elems}
        else:
            return None

    def __load_txtrs(self):
        """Loading the tile's textures as images"""
        mdl = self.model_3d
        if mdl is None:
            return None
        
        pth = version_manager.get_path(self._mc_vers)
        txtrs_pth = join(pth, 'assets', 'minecraft', 'textures')
        txtrs = {}
        for name, f_pth in mdl['textures'].items():
            if f_pth[0] == '#':
                continue

            txtrs[name] = Image.open(join(txtrs_pth, f_pth+'.png'))

        return txtrs

    def to_vec(self) -> np.ndarray:
        """Returns a vectorized representation of the tile.

        The vector is created based on the tile's shape and average texture
        color.

        Returns:
            np.ndarray: The vector representation of the tile.
        """
        mdl = self.model_3d
        txtrs = self.textures
        #If the tile has no model (minecraft:air for example), then return zeros.
        if mdl is None:
            return np.zeros(2*3 + 6*3)
        
        #Create separate vectors for each shape the tile model is composed of.
        bx_vecs = []
        for elem in mdl['elements']:
            #The shape's bounding box coordinates
            from_ = np.array(elem['from']) / 16
            to = np.array(elem['to']) / 16
            #Init each faces' average color to black
            f_cols = {
                'up':   np.array([0., 0., 0.]),
                'down': np.array([0., 0., 0.]),
                'east': np.array([0., 0., 0.]),
                'west': np.array([0., 0., 0.]),
                'north': np.array([0., 0., 0.]),
                'south': np.array([0., 0., 0.])
            }
            #Get the average texture color for each face
            for face in elem['faces']:
                txtr_id = elem['faces'][face]['texture'][1:]
                while txtr_id not in txtrs:
                    txtr_id = mdl['textures'][txtr_id]
                    if '#' in txtr_id:
                        txtr_id = txtr_id[1:]

                img = txtrs[txtr_id].convert('RGB')
                f_cols[face] = np.average(img, axis=(0, 1))[:3]/256

            bx_vec = np.concatenate([from_, to] + list(f_cols.values()))
            bx_vecs.append(bx_vec)

        #Concatenating shape vectors
        tile_vec = np.concatenate(bx_vecs)
        return tile_vec

    @classmethod
    def list_all(cls, version: str):
        """List all possible tiles in a Minecraft version.

        This method parses all json files in the Minecraft version's
        ``blockstates/`` directory, to determine all possible tile ids.

        Args:
            version (str): Minecraft version.

        Returns:
            :obj:`list` of :obj:`Tile`: List of all tiles.
        """
        pth = version_manager.get_path(version)
        bs_pth = join(pth, 'assets', 'minecraft', 'blockstates')

        tile_names = [f.split('.')[0] for f in listdir(bs_pth) if isfile(join(bs_pth, f))]

        tile_list = []
        for name in tile_names:
            with open(join(bs_pth, name+'.json'), 'r') as bs_json:
                bs_data = json.load(bs_json)
            if 'variants' in bs_data:
                for v in bs_data['variants'].keys():
                    if v != '':
                        tile_list.append(
                            cls('minecraft:{}[{}]'.format(
                                name, v), version)
                        )
                    else:
                        tile_list.append(
                            cls('minecraft:{}'.format(name), version)
                        )
            else:
                tile_list.append(
                    cls('minecraft:{}'.format(name), version)
                )

        return tile_list

    def __eq__(self, o):
        return self.id == o.id

    def __hash__(self):
        return hash((self.id))

    def __repr__(self):
        return self.id

    def __str__(self):
        return self.id

    @classmethod
    def vectorize_all(cls, version: str, pad_to: int = None) -> np.ndarray:
        return vectorize(cls.list_all(version), pad_to = pad_to)

def vectorize(palette: List[Tile], pad_to: int = None) -> np.ndarray:
    """Returns a vector representation of all tiles in a list.

    Args:
        palette (List[Tile]): A list of tiles.
        pad_to (int): Pad all vectors to a specific length.

    Returns:
        np.ndarray: A 2D array of tile vector representations.
    """
    tile_vecs = [t.to_vec() for t in palette]
    max_len = max([len(v) for v in tile_vecs])
    if pad_to is not None:
        max_len = max(max_len, pad_to)
    tile_vecs_pad = np.array(
        [np.pad(v, (0, max_len - len(v)), 'constant') for v in tile_vecs]
    )
    return tile_vecs_pad