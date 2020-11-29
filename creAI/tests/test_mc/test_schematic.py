import unittest
from os.path import join, dirname
import numpy as np

from creAI.mc import Tile, Schematic
from creAI.mc.exceptions import *
import creAI.mc.version_manager as vm
vm.MC_PATH = '/home/ebalint96/.minecraft'

test_schems_path = join(dirname(__file__), 'test_schems')

class TestSchematic(unittest.TestCase):

    def test_load(self):
        with open(join(test_schems_path, 'lime_walls_16x16x16.schem'), 'rb') \
            as schem_file:
            schem = Schematic.load(schem_file, '1.15.2')

        self.assertEqual(len(schem.palette), 2)
        self.assertEqual(schem.shape, (16,16,16))

    def test_save(self):
        #Creating schematic
        schem = Schematic(shape=(5,5,5))

        #Adding tile to schematic
        schem[0,0,0] = Tile('minecraft:red_concrete')

        #Saving schematic
        with open(join(test_schems_path, 'save_test.schem'), 'wb') \
            as schem_file:
            schem.save(schem_file)

        #Loading back schematic
        with open(join(test_schems_path, 'save_test.schem'), 'rb') \
            as schem_file:
            schem = Schematic.load(schem_file, '1.15.2')

        #Checking wether or not it contains the added tile
        self.assertIn(Tile('minecraft:red_concrete'), schem.palette)
            
if __name__ == '__main__':
    unittest.main()