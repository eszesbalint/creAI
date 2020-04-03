import eel
import creAI.Globals
import numpy as np
import creAI.Tilemaps.MinecraftTilemaps.Geometry as geometry

UI_ELEMENTS = {}

@eel.expose
def remove_ui_element(id_):
    global UI_ELEMENTS
    UI_ELEMENTS[id_].destroy()
    del UI_ELEMENTS[id_]
@eel.expose
def toggle_plugin_visibility(id_):
    if creAI.Globals.selected_plugin_id is None:
        creAI.Globals.selected_plugin_id = id_
        eel.show_DOM_element(id_)
    elif creAI.Globals.selected_plugin_id == id_:
        creAI.Globals.selected_plugin_id = None
        eel.hide_DOM_element(id_)
    elif creAI.Globals.selected_plugin_id != id_:
        eel.hide_DOM_element(creAI.Globals.selected_plugin_id)
        creAI.Globals.selected_plugin_id = id_
        eel.show_DOM_element(id_)

def display_loading_animation(label):
    def decorator(function):
        def wrapper(*args, **kwargs):
            global UI_ELEMENTS
            d_w = Dialog_Window(
                    title = label,
                    content = [
                        Paragraph(text = 'Executing: {}'.format(function.__name__)),
                        Progress_Bar()
                    ]
                )
            d_w.create()
            UI_ELEMENTS[d_w.id] = d_w
            result = function(*args, **kwargs)
            remove_ui_element(d_w.id)
            return result
        wrapper.__name__ = function.__name__
        return wrapper
    return decorator


def display_error_message_on_error(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            global UI_ELEMENTS
            d_w = Dialog_Window(
                    title = 'Error!',
                    content = [
                        Paragraph(text = 'Executing: {}'.format(function.__name__)),
                        Paragraph(text = str(e))
                    ]
                )
            d_w.create()
            UI_ELEMENTS[d_w.id] = d_w
    wrapper.__name__ = function.__name__
    return wrapper

@display_loading_animation('Loading 3D data')
#@display_error_message_on_error
def display_selected_tilemap():
    selected = creAI.Globals.tilemaps[creAI.Globals.selected_tilemap_id]
    if 'geometry' in selected:
        eel.show_tilemap(creAI.Globals.selected_tilemap_id)
        return



    selected['geometry'] = geometry.tilemap_to_geometry(selected['tilemap'])

    eel.add_tilemap(creAI.Globals.selected_tilemap_id, list(selected['geometry'][0,:].flatten()), list(selected['geometry'][1,:].flatten()), list(selected['geometry'][2,:].flatten()))
    eel.show_tilemap(creAI.Globals.selected_tilemap_id)




class UI_Element(object):
    def __init__(self, **kwargs):
        self.check_required_keyword_arguments(**kwargs)
        self.property = kwargs
        self.id = creAI.Globals.gen_id()

    _required = []
    _additional = []
    _optional = []
        
    def create(self, **kwargs):
        self.check_additional_keyword_arguments(**kwargs)
        self.property.update(kwargs)
        self.construct_DOM_elements()

    def check_required_keyword_arguments(self, **kwargs):
        for key in self._required:
            if key not in kwargs:
                raise AttributeError('Keyword argument \'{}\' is required for {}!'.format(key, type(self).__name__))
        for key in kwargs:
            if key not in self._required and key not in self._optional:
                raise AttributeError('Invalid keyword argument \'{}\' for {}!'.format(key, type(self).__name__))

    def check_additional_keyword_arguments(self, **kwargs):
        for key in self._additional:
            if key not in kwargs:
                raise AttributeError('Additional keyword argument \'{}\' is required for {}!'.format(key, type(self).__name__))

    def destroy(self):
        eel.remove_DOM_element(self.id)

    def __eq__(self, other):
        return self.id == other.id

class Dialog_Window(UI_Element):
    _required = ['title','content']
    def construct_DOM_elements(self):
        title_str = self.property['title']

        window = self.id
        eel.add_DOM_element('body', 'div', {'class' : 'dialog_window', 'id' : window})

        grid = creAI.Globals.gen_id()
        eel.add_DOM_element(window, 'div', {'class' : 'dialog_window_grid', 'id' : grid})

        title = creAI.Globals.gen_id()
        eel.add_DOM_element(grid, 'h1', {'id' : title})
        eel.append_text(title, title_str)

        close_button = creAI.Globals.gen_id()

        close_button_script = '{}.{}(\'{}\')'.format('eel', 'remove_ui_element', self.id)
        eel.add_DOM_element(grid, 'div', {'class' : 'menu_element', 'id' : close_button, 'onclick' : close_button_script})
        eel.add_DOM_element(close_button, 'div', {'class' : 'close icon'})

        body_grid = creAI.Globals.gen_id()
        eel.add_DOM_element(window, 'div', {'class' : 'dialog_window_body_grid', 'id' : body_grid})

        for element in self.property['content']:
            element.create(parent_id = body_grid)

    def destroy(self):
        for element in self.property['content']:
            element.destroy()
        eel.remove_DOM_element(self.id)

class Progress_Bar(UI_Element):
    _additional = ['parent_id']
    def construct_DOM_elements(self):
        parent_id = self.property['parent_id']
        eel.add_DOM_element(parent_id, 'div', {'class' : 'progress_bar', 'id' : self.id})

class Paragraph(UI_Element):
    _required = ['text']
    _additional = ['parent_id']
    def construct_DOM_elements(self):
        parent_id = self.property['parent_id']
        text = self.property['text']
        eel.add_DOM_element(parent_id, 'p', {'id' : self.id})
        eel.append_text(self.id, text)

class Button(UI_Element):
    _optional = ['function', 'text', 'icon_class']
    _additional = ['parent_id']
    def construct_DOM_elements(self):
        onclick_script = ''
        if 'function' in self.property:
            function_name = '{}_{}'.format(self.property['function'].__name__, self.id)
            global function
            function = (eel.expose(function_name))(self.property['function'])
            onclick_script = '{}.{}()'.format('eel',function_name)

        parent_id = self.property['parent_id']
        eel.add_DOM_element(parent_id, 'div', {'class' : 'menu_element', 'id' : self.id, 'onclick' : onclick_script})
        if 'text' in self.property:
            eel.append_text(self.id, self.property['text'])
        elif 'icon_class' in self.property:
            eel.add_DOM_element(self.id, 'div', {'class' : self.property['icon_class']})

class Plugin(UI_Element):
    _required = ['icon_class', 'name', 'title', 'description', 'content']
    def construct_DOM_elements(self):
        properties_tab = creAI.Globals.gen_id()
        eel.add_DOM_element('properties_wrapper', 'div', {'class' : 'properties hidden', 'id' : properties_tab})

        menu_button = creAI.Globals.gen_id()
        menu_button_script = '{}.{}(\'{}\')'.format('eel', 'toggle_plugin_visibility', properties_tab)
        eel.add_DOM_element('plugin_menu', 'div', {'class' : 'menu_element', 'id' : menu_button, 'onclick' : menu_button_script})
        eel.add_DOM_element(menu_button, 'div', {'class' : self.property['icon_class']})

        title = creAI.Globals.gen_id()
        eel.add_DOM_element(properties_tab, 'h1', {'id' : title})
        eel.append_text(title, self.property['title'])
        
        description = creAI.Globals.gen_id()
        eel.add_DOM_element(properties_tab, 'p', {'id' : description})
        eel.append_text(description, self.property['description'])

        for element in self.property['content']:
            element.create(parent_id = properties_tab)

    def destroy(self):
        for element in self.property['content']:
            element.destroy()
        eel.remove_DOM_element(self.id)

class File_Tag(UI_Element):
    _required = ['text', 'select_function', 'close_function']
    def construct_DOM_elements(self):
        file_tag = self.id
        eel.add_DOM_element('file_list', 'div', {'class' : 'file_tag', 'id' : file_tag})

        name_tag = Button(text = self.property['text'], function = self.property['select_functin'])
        name_tag.create(parent_id = file_tag)
        close_button = Button(icon_class = 'close icon', function = self.property['close_functin'])
        close_button.create(parent_id = file_tag)

        self.property['content'] = [name_tag, close_button]        

    def destroy(self):
        for element in self.property['content']:
            element.destroy()
        eel.remove_DOM_element(self.id)
        