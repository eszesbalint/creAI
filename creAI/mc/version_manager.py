"""Minecraft version manager.

This module implements simple functions to find and extract specific
Minecraft versions.

Attributes:
    MC_PATH (os.PathLike): Minecraft installation path.
    EXTRACTION_PATH (os.PathLike): The path to extract Minecraft versions.

"""


import sys
from zipfile import ZipFile
from os import PathLike, listdir, mkdir
from os.path import join, isdir, dirname, exists
from typing import List


from creAI.mc.exceptions import *

#The extraction path depends on wether or not the main creAI package has been
#packaged to a single executable.
if getattr(sys, 'frozen', False):
    EXTRACTION_PATH = join(sys._MEIPASS, 'mc', 'versions')
else:
    EXTRACTION_PATH = join(dirname(__file__), 'versions')

#If the extraction folder hasn't been created then create it.
if not exists(EXTRACTION_PATH):
    mkdir(EXTRACTION_PATH)

MC_PATH = None




def versions() -> List[str]:
    """List installed Minecraft versions.

    This function iterates through the ``versions/`` directory in the
    Minecraft installation path and returns a list of Minecraft versions 
    identified by their directory's name. This function doesn't check wether 
    or not the directory contains a valid installation.

    Returns:
        List(str): A list of Minecraft versions identified by their
            name.
    """
    return [d for d in listdir(join(MC_PATH, 'versions')) 
            if isdir(join(MC_PATH, 'versions', d))]


def get_path(v: str) -> PathLike:
    """Get the path to the extracted Minecraft version.

    This function extracts the ``.jar`` file inside a Minecraft version
    directory to a path defined at module level, then returns the path.

    Args:
        v (str): Name of the Minecraft version.

    Returns:
        os.PathLike: Path to the extracted .jar file's content.

    Raises:
        MinecraftVersionNotInstalled: If the specified version is not present 
            in the versions/ directory.
        MissingMinecraftJarFile: If the directory doesn't contain the 
            corresponding .jar file.
    """
    extracted_versions = [d for d in listdir(EXTRACTION_PATH) 
                      if isdir(join(EXTRACTION_PATH, d))]
    if v not in versions():
        raise MinecraftVersionNotInstalled(v)
    pth = join(EXTRACTION_PATH, v)
    if v not in extracted_versions:
        print('Extracting Minecraft version {}...'.format(v))
        jar_pth = join(MC_PATH, 'versions', v, v+'.jar')
        if not exists(jar_pth):
            raise MissingMinecraftJarFile(v)
        with ZipFile(join(MC_PATH, 'versions', v, v+'.jar')) as z:
            z.extractall(join(EXTRACTION_PATH, v))
        print('{} extracted.'.format(v))
    return pth

