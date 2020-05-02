import eel

import creAI.ui
from creAI.plugins.file_manager.formats.tilemaps.minecraft_tilemaps import Schematic, Minecraft_Tilemap
from creAI.plugins.file_manager.formats.tilemaps.minecraft_tilemaps.geometry import tilemap_to_geometry

@creAI.ui.display_error_message_on_error
def load_schematic(raw_data):
    raw_data = bytearray(raw_data.values())
    tilemap = Schematic.load(None, raw_data)
    return tilemap

@creAI.ui.display_error_message_on_error
def display_schematic(id_: str, file_: dict):
    if 'geometry' in file_:
        geometry = file_['geometry']
    else:
        geometry = tilemap_to_geometry(file_['content'])
        file_['geometry'] = geometry
    creAI.ui.display_geometry(id_, geometry)

@creAI.ui.display_error_message_on_error
def hide_schematic(id_: str, file_: dict):
    creAI.ui.hide_geometry(id_)

@creAI.ui.display_error_message_on_error
def save_schematic(tilemap: Minecraft_Tilemap) -> bytearray:
    return bytearray(Schematic.save(tilemap))



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
            name=file_name,
            format=extention,
            content=content,
        )
    else:
        raise ValueError('{} is not a supported format!'.format(extention))

@creAI.ui.display_error_message_on_error
def add(id_: str, **kwargs):
    file_ = kwargs
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

@eel.expose('FileManager_save')
@creAI.ui.display_error_message_on_error
def save():
    file_ = files[selected]
    buffer = formats[file_['format']]['save'](file_['content'])
    dialog = creAI.ui.File_Save_Dialog(file_name = file_['name'], bytes_ = buffer)
    dialog.create()

@creAI.ui.display_loading_animation('Displaying file')
@creAI.ui.display_error_message_on_error
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

@creAI.ui.display_error_message_on_error
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
@creAI.ui.display_error_message_on_error
def select(id_):
    global selected
    if id_ != selected:
        hide(selected)
        selected = id_
        display(selected)


@eel.expose('FileManager_delete')
@creAI.ui.display_error_message_on_error
def delete(id_):
    hide(id_)
    global files
    files[id_]['tag'].destroy()
    del files[id_]
