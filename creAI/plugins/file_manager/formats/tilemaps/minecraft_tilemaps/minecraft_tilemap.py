import json
import math
import os

import numpy as np

from creAI.plugins.file_manager.formats.tilemaps.minecraft_tilemaps import nbt
from creAI.plugins.file_manager.formats.tilemaps import ID, Tile, Tilemap


class Minecraft_ID(ID):
    def value_type(self, value: tuple) -> tuple:
        if len(value) != 2:
            raise TypeError("Minecraft_ID expects a tuple of length 2!")
        elif not isinstance(value[0], str) or not isinstance(value[1], str):
            raise TypeError("Minecraft_ID expects a tuple of 2 strings!")
        return value

    def __str__(self):
        return "{}{}".format(
            self.value[0],
            "[{}]".format(self.value[1]) if self.value[1] != "" else ""
        )


class Minecraft_Tile(Tile):
    def id_object_type(self, id_object: Minecraft_ID) -> Minecraft_ID:
        return id_object


class Minecraft_Tilemap(Tilemap):
    @classmethod
    def tiles_type(cls, tiles):
        for item in tiles.flat:
            cls.tile_type(item)
        return tiles

    @classmethod
    def tile_type(cls, tile):
        if not isinstance(tile, Minecraft_Tile):
            raise TypeError("Array elements are not type Minecraft_Tile!")
        return tile


class Schematic(object):
    @classmethod
    def load(cls, file_name: str = None, raw_data=None) -> Minecraft_Tilemap:
        import time
        root_tag = nbt.load(file_name, raw_data)
        h = root_tag["Height"].payload
        l = root_tag["Length"].payload
        w = root_tag["Width"].payload
        block_data = root_tag["BlockData"].payload
        #block_data = root_tag["BlockData"]
        tiles = np.empty((w, h, l), dtype=object)
        numeric_ids = np.empty((w, h, l), dtype=int)
        data_offset = 0
        palette = {}
        for element in root_tag["Palette"].payload:
            splitted = element.name.split('[')
            name = splitted[0]
            variant = ''
            if len(splitted) > 1:
                variant = element.name.split('[')[1][:-1]
            palette[element.payload] = Minecraft_Tile(
                Minecraft_ID(
                    (name, variant)
                )
            )
        start = time.time()
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
        end = time.time()
        print(end - start)
        tiles = np.vectorize(palette.__getitem__)(numeric_ids)
        return Minecraft_Tilemap(tiles)

    @classmethod
    def load_as_nbt(cls, file_name: str = None, raw_data=None) -> nbt.TAG:
        return nbt.load(file_name, raw_data)

    @classmethod
    def save(cls, tile_map: Minecraft_Tilemap, path: str):
        # Swapping axes
        swapped_tile_map = np.swapaxes(tile_map, 0, 1)
        swapped_tile_map = np.swapaxes(swapped_tile_map, 1, 2)
        # Creating root tag
        root_tag = nbt.TAG_Compound(name='Schematic')
        # Building Palette tag
        tile_set = set(tile_map.flat)
        palette_tag = nbt.TAG_Compound(name='Palette')
        palette_payload = []
        numeric_id = 0
        for tile in tile_set:
            int_tag = nbt.TAG_Int(
                name=str(tile), payload=numeric_id)
            palette_payload.append(int_tag)
            numeric_id += 1
        palette_tag.payload = palette_payload
        # Creating PaletteMax tag
        palette_max_tag = nbt.TAG_Int(
            name='PaletteMax', payload=numeric_id)
        # Creating Width tag
        width_tag = nbt.TAG_Short(
            name='Width', payload=tile_map.shape[0])
        # Creating Height tag
        height_tag = nbt.TAG_Short(
            name='Height', payload=tile_map.shape[1])
        # Creating Length tag
        length_tag = nbt.TAG_Short(
            name='Length', payload=tile_map.shape[2])
        # Creating Version tag
        version_tag = nbt.TAG_Int(name='Version', payload=2)
        # Creating DataVersion tag
        data_version_tag = nbt.TAG_Int(
            name='DataVersion', payload=1976)
        # Creating BlockData tag
        block_data_tag = nbt.TAG_Byte_Array(name='BlockData')
        bytes_ = []
        for tile in swapped_tile_map.flat:
            numeric_id = palette_tag[str(tile)].payload
            if (numeric_id == 0):
                bytes_.append(0)
                continue
            id_length = math.ceil(numeric_id.bit_length()/7.)
            for i in range(id_length):
                next_byte = ((numeric_id >> i*7)
                             - ((numeric_id >> (i+1)*7) << (i+1)*7))
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
        nbt.save(root_tag, path)
