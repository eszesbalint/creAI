import eel

import creAI.ui
from creAI.plugins.file_manager.formats.tilemaps.minecraft_tilemaps import Schematic
from creAI.plugins.file_manager.formats.tilemaps.minecraft_tilemaps.geometry import tilemap_to_geometry


def load_schematic(raw_data):
    raw_data = bytearray(raw_data.values())
    tilemap = Schematic.load(None, raw_data)
    return tilemap


def display_schematic(id_: str, file_: dict):
    if 'geometry' in file_:
        geometry = file_['geometry']
    else:
        geometry = tilemap_to_geometry(file_['content'])
        file_['geometry'] = geometry
    creAI.ui.display_geometry(id_, geometry)


def hide_schematic(id_: str, file_: dict):
    creAI.ui.hide_geometry(id_)


def save_schematic():
    #tilemap = creAI.Globals.tilemaps[creAI.Globals.selected_tilemap_id]['tilemap']
    #Schematic.save(tilemap, "saving_test.schem")
    pass


files = {}
selected = None

formats = {
    'schem': {
        'load': load_schematic,
        'display': display_schematic,
        'hide': hide_schematic,
        'save': save_schematic,
    }
}


@eel.expose('FileManager_read')
@creAI.ui.display_loading_animation('Reading file')
@creAI.ui.display_error_message_on_error
def read(file_name, raw_data):
    extention = file_name.split('.')[-1]
    if extention in formats:
        content = formats[extention]['load'](raw_data)
        id_ = str(id(content))
        add(
            id_,
            {
                'name': file_name,
                'format': extention,
                'content': content,
            }
        )
    else:
        raise ValueError('{} is not a supported format!'.format(extention))


def add(id_: str, file_: dict):
    tag = creAI.ui.File_Tag(
        text=file_['name'],
        script_1=creAI.ui.function_to_script(select, id_),
        script_2=creAI.ui.function_to_script(delete, id_),
    )
    tag.create(parent_id='file_list')
    file_['tag'] = tag
    global files
    files[id_] = file_
    global selected
    selected = id_
    display(selected)


@eel.expose('FileManager_load')
def load():
    dialog = creAI.ui.File_Open_Dialog(
        script=creAI.ui.function_to_script(read))
    dialog.create()


def display(id_):
    file_ = files[id_]
    function_name = 'display'
    if function_name in formats[file_['format']]:
        formats[file_['format']][function_name](id_, file_)
    else:
        raise NotImplementedError(
            'Function \'{}\' for format \'{}\' is not implemented yet!'.format(
                function_name, file_['format']
            )
        )


def hide(id_):
    file_ = files[id_]
    function_name = 'hide'
    if function_name in formats[file_['format']]:
        formats[file_['format']][function_name](id_, file_)
    else:
        raise NotImplementedError(
            'Function \'{}\' for format \'{}\' is not implemented yet!'.format(
                function_name, file_['format']
            )
        )


@eel.expose('FileManager_select')
def select(id_):
    global selected
    hide(selected)
    selected = id_
    display(selected)


@eel.expose('FileManager_delete')
def delete(id_):
    hide(id_)
    global files
    files[id_]['tag'].destroy()
    del files[id_]
