import unittest

from creAI.mc import Tile
import creAI.mc.version_manager as vm
vm.MC_PATH = '/home/ebalint96/.minecraft'

class TestTile(unittest.TestCase):

    def test_id(self):
        t1 = Tile('minecraft:something[arg1=foo,arg2=bar]')
        self.assertEqual(t1.name, 'something')
        self.assertEqual(t1.data_values[0], 'arg1=foo')
        self.assertEqual(t1.data_values[1], 'arg2=bar')


        with self.assertRaises(AttributeError):
            t2 = Tile('minecraftsomething[arg1=foo,arg2=bar]')
        with self.assertRaises(AttributeError):
            t2 = Tile('minecraft:somethingarg1=foo,arg2=bar]')
        with self.assertRaises(AttributeError):
            t2 = Tile('minecraft:something[arg1=foo,arg2=bar')
        with self.assertRaises(AttributeError):
            t2 = Tile('minecraftt:something[arg1=foo,arg2=bar]')
        with self.assertRaises(AttributeError):
            t2 = Tile('minecraft:something[arg1=foo, arg2=bar]')

    def test_model_loading(self):
        tiles = Tile.list_all('1.15.2')
        l = [t.textures for t in tiles]



if __name__ == '__main__':
    unittest.main()