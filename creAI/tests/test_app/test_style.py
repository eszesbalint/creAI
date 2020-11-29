import unittest
from os.path import join, dirname
import numpy as np

from creAI import Style
import creAI.style
from creAI.exceptions import *

creAI.style.STYLES_PATH = join(dirname(__file__), 'test_styles')

class TestStyle(unittest.TestCase):

    def test_init(self):
        stl = Style('test_style', mc_version='1.15.2', 
                    icon_pth=join(dirname(__file__), 'icon_test.jpeg'))

        with self.assertRaises(IconFileMissing):
            stl = Style('test_style', mc_version='1.15.2', 
                    icon_pth='this_img_does_not_exists.jpeg')

        with self.assertRaises(InvalidStyleName):
            stl = Style('test style with a space', mc_version='1.15.2', 
                    icon_pth=join(dirname(__file__), 'icon_test.jpeg'))
        
    def test_load_save(self):
        # Creating stlye
        stl1 = Style('test_style', mc_version='1.15.2', 
                    icon_pth=join(dirname(__file__), 'icon_test.jpeg'))
        # Saving style
        stl1.save()

        # Loading
        stl2 = Style('test_style')

        self.assertEqual(stl1.name, stl2.name)
        self.assertEqual(stl1.info['mc_version'], stl2.info['mc_version'])


    def test_train(self):
        pass

    def test_generate(self):
        pass
            
if __name__ == '__main__':
    unittest.main()