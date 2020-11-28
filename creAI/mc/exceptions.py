class MinecraftError(Exception):
    """Base class for Minecraft related exceptions"""
    pass

class MinecraftVersionNotInstalled(MinecraftError):
    def __init__(self, version):
        self.version = version

    def __str__(self):
        return ('Minecraft version {} is not ' 
               'installed in your system!').format(self.version)

class MissingMinecraftJarFile(MinecraftError):
    def __init__(self, version):
        self.version = version

    def __str__(self):
        return ('No .jar file found for Minecraft version {}! '
               'Modded versions are not supported.').format(self.version) 

class TilemapInvalidInitArguments(MinecraftError):
    def __init__(self, shape, data, palette):
        self.args =  (shape, data, palette)

    def __str__(self):
        return ('Couldn\'t initialize tilemap with shape {}, data (shape {})' 
               ' and palette (length {})'
               '').format(self.args[0],self.args[0].shape,len(self.args[0]))


class TilemapDataTypeError(MinecraftError):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return ('Tilemap data should be a np.ndarray, but got {}!' 
               '').format(type(self.data).__name__)


class TilemapDataShapeError(MinecraftError):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return ('Tilemap data should be of rank 3, but got array with shape {}!'
               '').format(self.data.shape)


class TilemapPaletteIsNotList(MinecraftError):
    def __init__(self, palette):
        self.p = palette

    def __str__(self):
        return ('Tilemap palette should be a list, but got {}!' 
               '').format(type(self.p).__name__)

class TilemapPaletteIsNotAListOfTiles(MinecraftError):
    def __init__(self, palette_element):
        self.p = palette_element

    def __str__(self):
        return ('Tilemap palette should be a list of tiles, but got value with type {}!' 
               '').format(type(self.p).__name__)

class TilemapAssertionTypeError(MinecraftError):
    def __init__(self, value):
        self.v = value

    def __str__(self):
        return ('Couldn\'t assert value of type {} to tilemap!'
               '').format(type(self.v).__name__)

class InvalidMinecraftNamespaceID(MinecraftError):
    def __init__(self, id_):
        self.id = id_

    def __str__(self):
        return ('\"{}\" is not a valid Minecraft namespace id! ' 
               'The following format is supported:'
               '\tminecraft:namespace_id[data_value1=value,...,data_valuen=value]'
               '').format(self.id)

class ModelLoadingWithUndefinedMinecraftVersion(MinecraftError):
    def __init__(self, tile):
        self.t = tile

    def __str__(self):
        return ('Manipulation of tiles with undefined Minecraft is supported,' 
               ' but model loading requires to assign an installed Minecraft' 
               ' version to load the 3D model from.' 
               ' Please provide a Minecraft version for tile {}').format(self.t)


class NoMatchFoundInBlockstates(MinecraftError):
    def __init__(self, tile):
        self.t = tile

    def __str__(self):
        return ('Couldn\'t find tile {0} in Minecraft version {1}! '
               'Please keep an eye on the patch notes for Minecraft version {1}, ' 
               'especially on renamings and changes in available blockstates '
               'for tile {2}.').format(self.t, self.t.version, self.t.name)

class MissingNBTTag(MinecraftError):
    def __init__(self, tag_name):
        self.tag = tag_name

    def __str__(self):
        return 'Tag \"{}\" is missing from schematic!'.format(self.tag)

class InvalidNBTTagType(MinecraftError):
    def __init__(self, tag_name, tag_class):
        self.tag_class = tag_class
        self.tag_name = tag_name

    def __str__(self):
        return ('Tag \"{}\" found in schematic, ' 
               'but its type should be {}!').format(self.tag_name, self.tag_class.__name__)
