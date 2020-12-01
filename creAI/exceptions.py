class ApplicationError(Exception):
    """Base class for application related exceptions"""
    pass

class MissingCommandDocstring(ApplicationError):
    def __init__(self, fun):
        self.fun_name = fun.__name__

    def __str__(self):
        return ('Can not create command from {},'
                ' no docstring was found!').format(self.fun_name)


class MissingAppDocstring(ApplicationError):
    def __init__(self, obj):
        self.cls_name = obj.__class__.__name__

    def __str__(self):
        return ('Can not create commandline interface for class {},'
                ' no docstring was found!').format(self.cls_name)


class InvalidStyleName(ApplicationError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return ('Style names should only contain alphanumeric characters'
                ' and underscores, {} is not a valid name!').format(self.name)


class IconFileMissing(ApplicationError):
    def __init__(self, pth):
        self.pth = pth

    def __str__(self):
        return ('Could not load image file from {} as this path doesn\'t'
                ' seem to exist!').format(self.pth)


class VAEModelMissing(ApplicationError):
    def __init__(self, stl_name):
        self.stl_name = stl_name

    def __str__(self):
        return ('You must train the VAE part of the model first in'
                ' style {}').format(self.stl_name)

class SchematicFileMissing(ApplicationError):
    def __init__(self, pth):
        self.pth = pth

    def __str__(self):
        return ('Schematic file is invalid or missing!'
                ' No file was found on path: \'{}\'').format(self.pth)


class UndefinedStyleMinecraftVersion(ApplicationError):
    def __init__(self, stl_name):
        self.stl_name = stl_name

    def __str__(self):
        return ('No Minecraft version was defined'
                ' for style {}!').format(self.stl_name)