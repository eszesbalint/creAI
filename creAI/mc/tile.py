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
        return self._id

    @property
    def name(self):
        return self._id_regex.match(self._id).group(1)

    @property
    def data_values(self):
        d_v = self._id_regex.match(self._id).groups(1)[-1]
        if isinstance(d_v, str):
            return d_v[1:-1].split(',')
        else:
            return ['']

    @property
    def version(self):
        return self._mc_vers

    @version.setter
    def version(self, version):
        self._mc_vers = str(version)

    @property
    def model_3d(self):
        if self.version is None:
            raise ModelLoadingWithUndefinedMinecraftVersion(self)

        return self.__load_mdl()


    @property
    def textures(self):
        return self.__load_txtrs()


    def __load_mdl(self):
        pth = version_manager.get_path(self._mc_vers)
        bs_pth = join(pth, 'assets', 'minecraft', 'blockstates')
        mdl_pth = join(pth, 'assets', 'minecraft', 'models', 'block')
        bs = join(bs_pth, self.name+'.json')
        if not exists(bs):
            raise NoMatchFoundInBlockstates(self)
        with open(bs, 'r') as bs_json:
            bs_data = json.load(bs_json)

        def truncate(s):
            if '/' in s:
                return s.split('/')[-1]
            else:
                return s

        def sel_mdl_from(d):
            if isinstance(d, list):
                return truncate(d[0]['model'])
            elif isinstance(d, dict):
                return truncate(d['model'])
            elif isinstance(d, str):
                return truncate(d)

        def trav_tree_rec(*mdl_names):
            txtrs = {}
            elems = []
            for mdl_name in mdl_names:
                with open(join(mdl_pth, mdl_name+'.json'), 'r') as mdl_json:
                    mdl_data = json.load(mdl_json)
                if 'textures' in mdl_data:
                    txtrs.update(mdl_data['textures'])
                if 'elements' in mdl_data:
                    elems += mdl_data['elements']
                elif 'parent' in mdl_data:
                    prnt_mdl_names = [sel_mdl_from(mdl_data['parent'])]
                    prnt_txtrs, prnt_elems = trav_tree_rec(*prnt_mdl_names)
                    txtrs.update(prnt_txtrs)
                    elems += prnt_elems

            return (txtrs, elems)

        if 'multipart' in bs_data:
            mdl_names = [
                sel_mdl_from(bs_data['multipart'][i]['apply'])
                for i in range(len(bs_data['multipart']))
            ]

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
        mdl = self.model_3d
        txtrs = self.textures
        if mdl is None:
            return np.zeros(2*3 + 6*3)

        bx_vecs = []
        for elem in mdl['elements']:
            from_ = np.array(elem['from']) / 16
            to = np.array(elem['to']) / 16
            f_cols = {
                'up':   np.array([0., 0., 0.]),
                'down': np.array([0., 0., 0.]),
                'east': np.array([0., 0., 0.]),
                'west': np.array([0., 0., 0.]),
                'north': np.array([0., 0., 0.]),
                'south': np.array([0., 0., 0.])
            }
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

        tile_vec = np.concatenate(bx_vecs)
        return tile_vec

    @classmethod
    def list_all(cls, version: str):
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
    tile_vecs = [t.to_vec() for t in palette]
    max_len = max([len(v) for v in tile_vecs])
    if pad_to is not None:
        max_len = max(max_len, pad_to)
    tile_vecs_pad = np.array(
        [np.pad(v, (0, max_len - len(v)), 'constant') for v in tile_vecs]
    )
    return tile_vecs_pad