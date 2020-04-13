import os
import sys

import numpy as np
from PIL import Image

from creAI.plugins.file_manager.formats.tilemaps.minecraft_tilemaps import (
    Minecraft_ID, Minecraft_Tile, Minecraft_Tilemap)
from creAI.plugins.file_manager.formats.tilemaps.minecraft_tilemaps.geometry import (
    get_model_json, blocktextures_folder_path)


np.set_printoptions(threshold=sys.maxsize)


def generate_training_data(tilemap: Minecraft_Tilemap) -> np.ndarray:
    x_train = []
    palette = set(tilemap.flat)
    for tile in palette:
        model = get_model_json(tile)
        if model is None:
            x_train.append(np.zeros(2*3 + 6*3))
            continue
        boxes = []
        for element in model['elements']:
            from_ = np.array(element['from']) / 16
            to = np.array(element['to']) / 16
            face_colors = {
                'up':   np.array([0., 0., 0.]),
                'down': np.array([0., 0., 0.]),
                'east': np.array([0., 0., 0.]),
                'west': np.array([0., 0., 0.]),
                'north': np.array([0., 0., 0.]),
                'south': np.array([0., 0., 0.])
            }
            for face in element['faces']:
                texture_id = element['faces'][face]['texture'][1:]
                texture_path = os.path.join(
                    blocktextures_folder_path,
                    model['textures'][texture_id].split('/')[1] + '.png'
                )
                img = Image.open(texture_path).convert('RGB')
                face_colors[face] = np.average(img, axis=(0, 1))[:3]/256

            box_vector = np.concatenate(
                [from_, to] + list(face_colors.values()))
            boxes.append(box_vector)

        tile_vector = np.concatenate(boxes)
        x_train.append(tile_vector)

    max_len = max([len(x) for x in x_train])
    x_train = np.array(
        [np.pad(x, (0, max_len - len(x)), 'constant') for x in x_train]
    )
    return x_train