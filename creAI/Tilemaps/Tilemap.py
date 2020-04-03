import numpy as np

class ID(object):
    def __init__(self, value):
        self.value = value
        
    _value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = self.value_type(new_value)

    def __str__(self):
        return str(self.value)

    def __eq__(self, other_id):
        return self.value == other_id.value
    
    def __hash__(self):
        return hash((self.value))

class StringID(ID):
    value_type = str

class NumericID(ID):
    value_type = int

class Tile(object):
    def __init__(self, id_object = None):
        self.id_object = id_object
    _id_object = None

    @property
    def id_object(self):
        return self._id_object

    @id_object.setter
    def id_object(self, new_id_object):
        self._id_object = self.id_object_type(new_id_object)

    def __eq__(self, other_tile):
        return self.id_object == other_tile.id_object

    def __hash__(self):
        return hash((self.id_object))

    def __str__(self):
        return str(self.id_object)

    def __repr__(self):
        return str(self.id_object)


class Tilemap(np.ndarray):
    def __new__(cls, input_array):
        obj = np.asarray(cls.tiles_type(input_array)).view(cls)
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return

