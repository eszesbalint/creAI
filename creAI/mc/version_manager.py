import sys
from zipfile import ZipFile
from os import PathLike
from os import listdir
from os.path import join, isdir, dirname, exists
from typing import List

if getattr(sys, 'frozen', False):
    EXTRACTION_PATH = join(sys._MEIPASS, 'mc', 'versions')
else:
    EXTRACTION_PATH = join(dirname(__file__), 'versions')

if not exists(EXTRACTION_PATH):
    mkdir(EXTRACTION_PATH)

MC_PATH = None


EXTRACTED_VERSIONS = [d for d in listdir(EXTRACTION_PATH) 
                      if isdir(join(EXTRACTION_PATH, d))]

def versions() -> List[str]:
    return [d for d in listdir(join(MC_PATH, 'versions')) 
            if isdir(join(MC_PATH, 'versions', d))]

def get_path(v: str) -> PathLike:
    if v not in versions():
        raise ValueError('Minecraft version {} is not'
                        ' installed on your system!'.format(v))
    pth = join(EXTRACTION_PATH, v)
    if v not in EXTRACTED_VERSIONS:
        print('Extracting Minecraft version {}...'.format(v))
        with ZipFile(join(MC_PATH, 'versions', v, v+'.jar')) as z:
            z.extractall(join(EXTRACTION_PATH, v))
            EXTRACTED_VERSIONS.append(v)
        print('{} extracted.'.format(v))
    return pth

