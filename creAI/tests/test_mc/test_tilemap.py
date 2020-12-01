import unittest
import numpy as np


from creAI import App
from creAI.mc import Tile, Tilemap
from creAI.mc.exceptions import *



class TestTilemap(unittest.TestCase):

    def test_init(self):
        #Init empty
        t = Tilemap(shape=(5,5,5))

        #Init from data and palette
        d = np.array([[[0,0],[0,1]],[[1,0],[1,1]]])
        p = [Tile('minecraft:air'), Tile('minecraft:stone')]
        t = Tilemap(data=d, palette=p)

        #Init wrong number of arguments
        with self.assertRaises(TilemapInvalidInitArguments):
            d = np.array([[[0,0],[0,1]],[[1,0],[1,1]]])
            p = [Tile('minecraft:air'), Tile('minecraft:stone')]
            t = Tilemap(shape=(1,1,1), data=d, palette=p)

        #Init data wrong shape
        with self.assertRaises(TilemapDataShapeError):
            d = np.array([[1,0],[1,1]]) #2D
            p = [Tile('minecraft:air'), Tile('minecraft:stone')]
            t = Tilemap(data=d, palette=p)

        #Init data wrong type
        with self.assertRaises(TilemapDataTypeError):
            d = "foo"
            p = [Tile('minecraft:air'), Tile('minecraft:stone')]
            t = Tilemap(data=d, palette=p)

        #Init palette wrong type
        with self.assertRaises(TilemapPaletteIsNotAListOfTiles):
            d = np.array([[[0,0],[0,1]],[[1,0],[1,1]]])
            p = ["foo", "bar"]
            t = Tilemap(data=d, palette=p)


    def test_surjectivity(self):
        t = Tilemap(shape=(5,5,5))
        self.assertEqual(t[0,0,0].name, 'air')
        t[0,0,0] = Tile('minecraft:stone')
        self.assertEqual(t.palette[1].name, 'stone')
        t[0,0,0] = Tile('minecraft:air')
        self.assertEqual(len(t.palette), 1)

if __name__ == '__main__':
    unittest.main()