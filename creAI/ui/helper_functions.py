import eel
import numpy as np

import creAI.globals


@eel.expose
def toggle_plugin_visibility(id_: str):
    if creAI.globals.selected_plugin_id is None:
        creAI.globals.selected_plugin_id = id_
        eel.add_class_to_DOM_element(id_, 'active')
    elif creAI.globals.selected_plugin_id == id_:
        creAI.globals.selected_plugin_id = None
        eel.remove_class_from_DOM_element(id_, 'active')
    elif creAI.globals.selected_plugin_id != id_:
        eel.remove_class_from_DOM_element(creAI.globals.selected_plugin_id, 'active')
        creAI.globals.selected_plugin_id = id_
        eel.add_class_to_DOM_element(id_, 'active')






def display_geometry(id_: str, geometry: np.ndarray):
    eel.add_tilemap(
        id_,
        list(geometry[0, :].flatten()),
        list(geometry[1, :].flatten()),
        list(geometry[2, :].flatten())
    )
    eel.show_tilemap(id_)

def hide_geometry(id_: str):
    eel.hide_tilemap(id_)

def set_innerHTML(id_: str, content: str):
    eel.set_innerHTML(id_, content)

def function_to_script(function, *args, **kwargs):
    if callable(function):
        for key, value in eel._exposed_functions.items():
            if value is function:
                exposed_name = key
                return '{}.{}({})'.format(
                    'eel', 
                    exposed_name, 
                    str(args)[1:-1]
                    )
        raise ValueError(
            'Function \'{}\' is not an exposed eel function!'.format(
                function.__name__
                )
            )
    else:
        raise TypeError(
            'Argument \'{}\' is not a function!'.format(function.__name__)
            )

@eel.expose
def remove_ui_element(id_: str):
    eel.remove_DOM_element(id_)