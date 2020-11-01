import numpy as np
import warnings
from typing import List

from creAI.mc.tile import Tile, vectorize

from creAI.mc.exceptions import *

def to_slice(key, ndim=3):
    new_key = [slice(None) for _ in range(ndim)]
    if not isinstance(key, tuple):
        key = (key)
    for idx, val in enumerate(()+key):
        new_key[idx] = val
    return tuple(new_key)


class Tilemap(object):
    def __init__(self, shape: tuple = None, version: str = None, 
                 data: np.ndarray = None, palette: List[Tile] = None):
        
        if data is not None and palette is not None:
            self.data = data
            self.palette = palette
            self.__remap()
        elif data is None and palette is None and shape is not None:
            self.data = np.zeros(shape, dtype=int)
            self.palette = [Tile('minecraft:air')]
        else:
            raise TilemapInvalidInitArguments(shape, data, palette)

        self.version = version


    @property
    def palette(self):
        return self._p

    @palette.setter
    def palette(self, val):
        if not isinstance(val, list):
            raise TilemapPaletteIsNotList(val)
        else:
            for t in val:
                if not isinstance(t, Tile):
                    raise TilemapPaletteIsNotAListOfTiles(val)
        self._p = val

    def palette_to_vecs(self, pad_to: int = None) -> np.ndarray:
        return vectorize(self._p, pad_to=pad_to)


    @property
    def data(self):
        return self._bd

    @data.setter
    def data(self, val):
        if isinstance(val, np.ndarray):
            if len(val.shape) == 3:
                self._bd = val
            else:
                raise TilemapDataShapeError(val)
        else:
            raise TilemapDataTypeError(val)

    @property
    def shape(self):
        return self._bd.shape

    @property
    def version(self):
        return self._mc_vers

    @version.setter
    def version(self, version):
        self._mc_vers = str(version)
        for t in self._p:
            t.version = self._mc_vers

    def __remap(self):
        bd = self._bd
        p = self._p
        u_ids = list(set(bd.flat))  # Unique indices in BlockData
        p = [p[idx] for idx in u_ids]  # New Palette
        # Mapping between the original indices and the new indices
        map_ = dict(zip(u_ids, range(len(u_ids))))
        bd = np.vectorize(lambda t: map_[t], otypes=[int])(bd)  # Remapping
        self._bd = bd
        self._p = p

    def __getitem__(self, key):
        key = to_slice(key)
        # The slicing operation returns a new Tilemap
        tlmp = Tilemap(self._bd[key].shape, self._mc_vers)
        tlmp._bd = self._bd[key]
        tlmp._p = self._p
        tlmp.__remap()
        return tlmp

    def __setitem__(self, key, val):
        key = to_slice(key)

        if isinstance(val, Tile):
            val.version = self._mc_vers
            if val not in self._p:
                self._p.append(val)
            self._bd[key] = self._p.index(val)
            self.__remap()

        elif isinstance(val, Tilemap):
            val.version = self._mc_vers
            a = self
            b = val
            merged_p = a._p + [t for t in b._p if t not in a._p]
            map_ = [merged_p.index(t) for t in b._p]
            a._bd[key] = np.vectorize(
                lambda t: map_[t],
                otypes=[int])(b._bd)  # Mapping b's indices to the merged palette
            a._p = merged_p
            a.__remap()

        else:
            raise TilemapAssertionTypeError(val)

    



    def __str__(self):
        o_str = ''
        o_str += 'Palette:\n'
        for idx, val in enumerate(self._p):
            o_str += '\t{}: {}\n'.format(idx, val)
        o_str += 'BlockData:\n'
        o_str += str(self._bd)
        return o_str
