import math
import numpy as np

import creAI.mc.nbt as nbt
from creAI.mc.tilemap import Tilemap
from creAI.mc.tile import Tile

from creAI.mc.exceptions import *

class Schematic(Tilemap):
    @classmethod
    def _check_format(cls, root: nbt.TAG_Compound) -> nbt.TAG_Compound:
        required_tags = {
            "Width": nbt.TAG_Short,
            "Height": nbt.TAG_Short,
            "Length": nbt.TAG_Short,
            "BlockData": nbt.TAG_Byte_Array,
            "Palette": nbt.TAG_Compound,
            "PaletteMax": nbt.TAG_Int,
            "DataVersion": nbt.TAG_Int,
            "Version": nbt.TAG_Int
        }

        for name, tag_class in required_tags.items():
            found = False
            for tag in root.payload:
                if tag.name == name:
                    if isinstance(tag, tag_class):
                        found = True
                    else:
                        raise InvalidNBTTagType(name, tag_class)

            if not found:
                raise MissingNBTTag(name)

        if root["DataVersion"].payload < 1976:
            raise ValueError("Schematic DataVersion should be at least 1976!")

        if root["Version"].payload < 2:
            raise ValueError("Schematic Version should be at least 2!") 

        return root

        

    @classmethod
    def load(cls, file, version):
        root_tag = cls._check_format(nbt.load(file=file))

        h = root_tag["Height"].payload
        l = root_tag["Length"].payload
        w = root_tag["Width"].payload
        block_data = root_tag["BlockData"].payload
        palette = root_tag["Palette"].payload

        numeric_ids = np.empty((w, h, l), dtype=int)
        data_offset = 0


        for block in range(h*l*w):
            numeric_id = 0
            id_length = 0
            while True:
                next_byte = block_data[data_offset]
                next_byte -= next_byte & 128
                numeric_id = numeric_id | (next_byte << id_length*7)
                id_length += 1
                if id_length > 5:
                    raise Exception(
                        "id_length too big! (Possibly corrupted data)"
                    )
                if ((block_data[data_offset] & 128) != 128):
                    data_offset += 1
                    break
                data_offset += 1
            y = block // (w * l)
            z = (block % (w * l)) // w
            x = (block % (w * l)) % w
            if numeric_id > root_tag["PaletteMax"].payload:
                raise ValueError(
                    "Palette ID {} at {} is bigger than PaletteMax {}".format(
                        numeric_id,
                        (x, y, z),
                        root_tag["PaletteMax"].payload
                    )
                )
            numeric_ids[x, y, z] = numeric_id

        
        data = numeric_ids
        p = [None] * len(palette)
        for tag in palette:
            p[tag.payload] = Tile(tag.name)
        palette = p
        self = cls(data=data, palette=palette, version=version)
        return self

    def save(self, file):
        # Swapping axes
        swapped_tile_map = np.swapaxes(self._bd, 0, 1)
        swapped_tile_map = np.swapaxes(swapped_tile_map, 1, 2)
        # Creating root tag
        root_tag = nbt.TAG_Compound(name='Schematic')
        # Building Palette tag
        palette_tag = nbt.TAG_Compound(name='Palette')
        palette_payload = []

        for tile, idx in zip(self._p, range(len(self._p))):
            int_tag = nbt.TAG_Int(
                name=tile.id, payload=idx)
            palette_payload.append(int_tag)

        palette_tag.payload = palette_payload
        # Creating PaletteMax tag
        palette_max_tag = nbt.TAG_Int(
            name='PaletteMax', payload=len(self._p)-1)
        # Creating Width tag
        width_tag = nbt.TAG_Short(
            name='Width', payload=self.shape[0])
        # Creating Height tag
        height_tag = nbt.TAG_Short(
            name='Height', payload=self.shape[1])
        # Creating Length tag
        length_tag = nbt.TAG_Short(
            name='Length', payload=self.shape[2])
        # Creating Version tag
        version_tag = nbt.TAG_Int(name='Version', payload=2)
        # Creating DataVersion tag
        data_version_tag = nbt.TAG_Int(
            name='DataVersion', payload=1976)
        # Creating BlockData tag
        block_data_tag = nbt.TAG_Byte_Array(name='BlockData')
        bytes_ = []
        for idx in swapped_tile_map.flat:
            if (idx == 0):
                bytes_.append(0)
                continue
            id_length = math.ceil(int(idx).bit_length()/7.)
            for i in range(id_length):
                next_byte = ((idx >> i*7)
                             - ((idx >> (i+1)*7) << (i+1)*7))
                if (i != id_length-1):
                    next_byte = next_byte | 128
                bytes_.append(next_byte)
        bytes_ = np.asarray(bytes_, dtype='uint8')
        block_data_tag.payload = bytes_
        root_tag.payload = [
            palette_tag,
            palette_max_tag,
            width_tag,
            height_tag,
            length_tag,
            block_data_tag,
            version_tag,
            data_version_tag,
        ]
        nbt.save(root_tag, file)






