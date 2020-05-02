import eel

import creAI.globals
from creAI.ui.helper_functions import toggle_plugin_visibility, function_to_script, remove_ui_element


class UI_Element(object):
    """ Base class for UI elements."""
    def __init__(self, **kwargs):
        """ Initalizing UI element.

        Args:
            **kwargs: keyword arguments describing the element's properties,
                      each subclass implements its own set of required and
                      optional properties.
        """
        self.check_required_keyword_arguments(**kwargs)
        self.property = kwargs
        self.id = creAI.globals.gen_id()

    _required = []
    _additional = []
    _optional = []

    def create(self, **kwargs):
        self.check_additional_keyword_arguments(**kwargs)
        self.property.update(kwargs)
        self.construct_DOM_elements()

    def check_required_keyword_arguments(self, **kwargs):
        """ Checking wether or not the given keyword arguments are valid.

        The arguments should either be in _required or _optional, but all
        keywords in _required should appear once and once only.

        Args:
            **kwargs: keyword arguments to check
        """
        for key in self._required:
            if key not in kwargs:
                raise AttributeError(
                    'Keyword argument \'{}\' is required for {}!'.format(
                        key,
                        type(self).__name__
                    )
                )
        for key in kwargs:
            if key not in self._required and key not in self._optional:
                raise AttributeError(
                    'Invalid keyword argument \'{}\' for {}!'.format(
                        key,
                        type(self).__name__
                    )
                )

    def check_additional_keyword_arguments(self, **kwargs):
        """ Checking wether or not the given keyword arguments are valid.

        The arguments should be in _additional.

        Args:
            **kwargs: keyword arguments to check
        """
        for key in self._additional:
            if key not in kwargs:
                raise AttributeError(
                    ('Additional keyword argument '
                     '\'{}\' is required for {}!').format(
                        key,
                        type(self).__name__
                    )
                )

    def destroy(self):
        """ Removing the DOM element associated with this UI element"""
        eel.remove_DOM_element(self.id)

    def __eq__(self, other):
        return self.id == other.id


class Dialog_Window(UI_Element):
    """ Creates a dialog window.
    
    Kwargs:
        Required:
            title (str): title of the window, this appears on the top of the 
                window
            content (List[UI_Element]): a list of UI elements to add to the
                window's body
    """
    _required = ['title', 'content']

    def construct_DOM_elements(self):
        title_str = self.property['title']
        window = self.id
        eel.add_DOM_element(
            'body',
            'div',
            {'class': 'dialog_window', 'id': window}
        )
        grid = creAI.globals.gen_id()
        eel.add_DOM_element(
            window,
            'div',
            {'class': 'dialog_window_grid', 'id': grid}
        )
        title = creAI.globals.gen_id()
        eel.add_DOM_element(grid, 'h1', {'id': title})
        eel.append_text(title, title_str)
        #close_button = creAI.globals.gen_id()
        # close_button_script = '{}.{}(\'{}\')'.format(
        #    'eel',
        #    'remove_ui_element',
        #    self.id
        # )
        # eel.add_DOM_element(
        #    grid,
        #    'div',
        #    {
        #        'class': 'menu_element',
        #        'id': close_button,
        #        'onclick': close_button_script
        #    }
        # )
        #eel.add_DOM_element(close_button, 'div', {'class': 'close icon'})
        Menu_Element(
            text='Close',
            icon_class='close icon',
            script=function_to_script(
                remove_ui_element,
                self.id
            )
        ).create(parent_id=grid)
        body_grid = creAI.globals.gen_id()
        eel.add_DOM_element(
            window,
            'div',
            {'class': 'dialog_window_body_grid', 'id': body_grid}
        )
        for element in self.property['content']:
            element.create(parent_id=body_grid)

    def destroy(self):
        for element in self.property['content']:
            element.destroy()
        eel.remove_DOM_element(self.id)


class Progress_Bar(UI_Element):
    """ Creates a placeholder progressbar. It is more like a loading animation.
    
    Kwargs:
        Additional:
            parent_id (str): ID of the parent DOM element 

    """
    _additional = ['parent_id']

    def construct_DOM_elements(self):
        parent_id = self.property['parent_id']
        eel.add_DOM_element(
            parent_id,
            'div',
            {'class': 'progress_bar', 'id': self.id}
        )


class Paragraph(UI_Element):
    """ Creates a simple paragraph.
    
    Kwargs:
        Required:
            text (str): the body of text to display
        Additional:
            parent_id (str): ID of the parent DOM element 

    """
    _required = ['text']
    _additional = ['parent_id']

    def construct_DOM_elements(self):
        parent_id = self.property['parent_id']
        text = self.property['text']
        eel.add_DOM_element(parent_id, 'p', {'id': self.id})
        eel.append_text(self.id, text)


class Title(UI_Element):
    """ Creates a simple title.
    
    Kwargs:
        Required:
            text (str): the body of text to display
        Additional:
            parent_id (str): ID of the parent DOM element 

    """
    _required = ['text']
    _additional = ['parent_id']

    def construct_DOM_elements(self):
        parent_id = self.property['parent_id']
        text = self.property['text']
        eel.add_DOM_element(parent_id, 'h1', {'id': self.id})
        eel.append_text(self.id, text)


class Button(UI_Element):
    """ Creates a customizable button.
    
    Kwargs:
        Optional:
            script (str): JavaScript script to run when button is clicked
            text (str): button label
            icon_class (str): CSS class of the icon to display
        Additional:
            parent_id (str): ID of the parent DOM element 

    """
    _optional = ['script', 'text', 'icon_class']
    _additional = ['parent_id']

    def construct_DOM_elements(self):
        onclick_script = ''
        if 'script' in self.property:
            onclick_script = self.property['script']
        parent_id = self.property['parent_id']
        eel.add_DOM_element(
            parent_id,
            'button',
            {
                'id': self.id,
                'onClick': onclick_script
            }
        )
        if 'icon_class' in self.property:
            eel.add_DOM_element(
                self.id,
                'div',
                {'class': self.property['icon_class']}
            )
        if 'text' in self.property:
            eel.append_text(self.id, self.property['text'])


class Menu_Element(UI_Element):
    """ Creates a menu button.
    
    Kwargs:
        Optional:
            script (str): JavaScript script to run when button is clicked
            text (str): button label
            icon_class (str): CSS class of the icon to display
            tag (str): HTML tag type
        Additional:
            parent_id (str): ID of the parent DOM element 

    """
    _optional = ['script', 'text', 'icon_class', 'tag']
    _additional = ['parent_id']

    def construct_DOM_elements(self):
        onclick_script = ''
        if 'script' in self.property:
            onclick_script = self.property['script']
        parent_id = self.property['parent_id']
        if 'tag' in self.property:
            tag = self.property['tag']
        else:
            tag = 'div'
        eel.add_DOM_element(
            parent_id,
            tag,
            {
                'class': 'menu_element_wrapper',
                'id': self.id,
            }
        )
        menu_element = creAI.globals.gen_id()
        eel.add_DOM_element(
            self.id,
            'div',
            {
                'class': 'menu_element',
                'id': menu_element,
                'onclick': onclick_script
            }
        )
        if 'icon_class' in self.property:
            icon_wrapper = creAI.globals.gen_id()
            eel.add_DOM_element(
                menu_element,
                'div',
                {'class': 'icon wrapper', 'id': icon_wrapper}
            )
            eel.add_DOM_element(
                icon_wrapper,
                'div',
                {'class': self.property['icon_class']}
            )
        if 'text' in self.property:
            title = creAI.globals.gen_id()
            eel.add_DOM_element(menu_element, 'p', {'id': title})
            eel.append_text(title, self.property['text'])


class Plugin(UI_Element):
    """ Creates the UI of a plugin, including the menu button and proprerties tab.
    
    Kwargs:
        Required:
            icon_class (str): CSS class of the icon to display
            name (str): name of the plugin
            title (str): the name to display in the menu
            description (str): plugin description
            content (List[UI_Element]): list of UI elements to expose the
                plugin's functions

    """
    _required = ['icon_class', 'name', 'title', 'description', 'content']

    def construct_DOM_elements(self):
        menu_element_id = creAI.globals.gen_id()
        menu_element = Menu_Element(
            text=self.property['title'],
            icon_class=self.property['icon_class'],
            script=function_to_script(
                toggle_plugin_visibility,
                menu_element_id
            )
        )
        menu_element.id = menu_element_id
        menu_element.create(parent_id='plugin_menu')

        properties_tab = creAI.globals.gen_id()
        eel.add_DOM_element(
            menu_element.id,
            'div',
            {'class': 'properties hidden', 'id': properties_tab}
        )

        title = creAI.globals.gen_id()
        #eel.add_DOM_element(properties_tab, 'h1', {'id': title})
        eel.append_text(title, self.property['title'])
        description = creAI.globals.gen_id()
        eel.add_DOM_element(
            properties_tab,
            'p',
            {
                'class': 'italic',
                'id': description
            }
        )
        eel.append_text(description, self.property['description'])
        for element in self.property['content']:
            element.create(parent_id=properties_tab)

    def destroy(self):
        for element in self.property['content']:
            element.destroy()
        eel.remove_DOM_element(self.id)


class File_Tag(UI_Element):
    """ Creates a file tag.
    
    Kwargs:
        Required:
            text (str): the body of text to display
        Optional:
            script_1 (str): JavaScript script to run when the tag is clicked
            script_2 (str): JavaScript script to run when the close button is 
                clicked
        Additional:
            parent_id (str): ID of the parent DOM element 

    """
    _required = ['text']
    _optional = ['script_1', 'script_2', 'text']
    _additional = ['parent_id']

    def construct_DOM_elements(self):
        onclick_script_1 = ''
        if 'script_1' in self.property:
            onclick_script_1 = self.property['script_1']
        onclick_script_2 = ''
        if 'script_2' in self.property:
            onclick_script_2 = self.property['script_2']
        parent_id = self.property['parent_id']

        eel.add_DOM_element(
            parent_id,
            'div',
            {
                'class': 'file_tag',
                'id': self.id,
            }
        )

        icon_wrapper = creAI.globals.gen_id()
        eel.add_DOM_element(
            self.id,
            'div',
            {'class': 'icon wrapper', 'id': icon_wrapper}
        )
        eel.add_DOM_element(
            icon_wrapper,
            'div',
            {
                'class': 'close icon',
                'onclick': onclick_script_2,
            }
        )
        title = creAI.globals.gen_id()
        eel.add_DOM_element(
            self.id,
            'p',
            {
                'id': title,
                'onclick': onclick_script_1,
            }
        )
        eel.append_text(title, self.property['text'])


class File_Open_Dialog(UI_Element):
    """ Creates a file opening dialog.
    
    Kwargs:
        Required:
            script (str): JavaScript script to run when the file has been 
                selected
        Optional:
            file_extention (str): show files only with this file extention

    """
    _required = ['script']
    _optional = ['file_extention']

    def construct_DOM_elements(self):
        eel.file_open_dialog(self.property['script'], '')

    def destroy(self):
        pass


class File_Save_Dialog(UI_Element):
    """ Creates a file saving dialog.
    
    Kwargs:
        Required:
            file_name (str): file name with extention
            bytes_ ()

    """
    _required = ['file_name', 'bytes_']

    def construct_DOM_elements(self):
        list_of_bytes = list(self.property['bytes_'])
        eel.file_save_dialog(self.property['file_name'], list_of_bytes)

    def destroy(self):
        pass


class Form(UI_Element):
    """ Creates a form element.
    
    Kwargs:
        Required:
            content (List[UI_Element]): list of UI elements
            script (str): JavaScript script to run when the form has been
                submitted
        Optional:
            file_extention (str): show files only with this file extention
        Additional:
            parent_id (str): ID of the parent DOM element 
    """
    _required = ['content', 'script']
    _additional = ['parent_id']

    def construct_DOM_elements(self):
        onsubmit_script = ''
        if 'script' in self.property:
            onsubmit_script = 'return read_form(\'{}\', \'{}\')'.format(
                self.id,
                self.property['script'],
            )
        eel.add_DOM_element(
            self.property['parent_id'],
            'form',
            {
                'id': self.id,
                'onsubmit': onsubmit_script,
            }
        )
        for element in self.property['content']:
            element.create(parent_id=self.id)

    def destroy(self):
        for element in self.property['content']:
            element.destroy()
        eel.remove_DOM_element(self.id)


class Input(UI_Element):
    """ Creates a general input element.
    
    Kwargs:
        Required:
            type_ (str): input type 
            name (str): name of the value it holds
        Optional:
            value (str): default input value
            label (str): label of the input element
            min_ (int): min value for numeric input types
            max_ (int): max value for numeric input types
        Additional:
            parent_id (str): ID of the parent DOM element 
    """
    _required = ['type_', 'name']
    _optional = ['value', 'label', 'min_', 'max_']
    _additional = ['parent_id']

    def construct_DOM_elements(self):
        value = ''
        if 'value' in self.property:
            value = self.property['value']
        min_ = ''
        if 'min_' in self.property:
            min_ = self.property['min_']
        max_ = ''
        if 'max_' in self.property:
            max_ = self.property['max_']
        if 'label' in self.property:
            label = creAI.globals.gen_id()
            eel.add_DOM_element(
                self.property['parent_id'],
                'label',
                {
                    'for': self.id,
                    'id': label,
                }
            )
            eel.append_text(label, self.property['label'])
        eel.add_DOM_element(
            self.property['parent_id'],
            'input',
            {
                'id': self.id,
                'type': self.property['type_'],
                'name': self.property['name'],
                'value': value,
                'min': min_,
                'max': max_,
            }
        )

        
class Radio_Input(UI_Element):
    """ Creates a radio button element.
    
    Kwargs:
        Required:
            name (str): name of the value it holds
        Optional:
            value (str): input value
            label (str): label of the input element
        Additional:
            parent_id (str): ID of the parent DOM element 
    """
    _required = ['name']
    _optional = ['value', 'label']
    _additional = ['parent_id']

    def construct_DOM_elements(self):
        value = ''
        if 'value' in self.property:
            value = self.property['value']
        if 'label' in self.property:
            eel.add_DOM_element(
                self.property['parent_id'],
                'input',
                {
                    'id': self.id,
                    'type': 'radio',
                    'name': self.property['name'],
                    'value': value,
                }
            )
            label = creAI.globals.gen_id()
            eel.add_DOM_element(
                self.property['parent_id'],
                'label',
                {
                    'for': self.id,
                    'id': label,
                    'class': 'radio_label',
                }
            )
            eel.append_text(label, self.property['label'])
            
       

class Number_Input(UI_Element):
    """ Creates a numeric input element with incement and decrement buttons.
    
    Kwargs:
        Required:
            name (str): name of the value it holds
        Optional:
            value (str): default input value
            label (str): label of the input element
            min_ (int): min value for numeric input types
            max_ (int): max value for numeric input types
        Additional:
            parent_id (str): ID of the parent DOM element 
    """
    _required = ['name']
    _optional = ['value', 'label', 'min_', 'max_']
    _additional = ['parent_id']

    def construct_DOM_elements(self):
        value = ''
        if 'value' in self.property:
            value = self.property['value']
        min_ = ''
        if 'min_' in self.property:
            min_ = self.property['min_']
        max_ = ''
        if 'max_' in self.property:
            max_ = self.property['max_']
        if 'label' in self.property:
            label = creAI.globals.gen_id()
            eel.add_DOM_element(
                self.property['parent_id'],
                'label',
                {
                    'for': self.id,
                    'id': label,
                }
            )
            eel.append_text(label, self.property['label'])
        wrapper = creAI.globals.gen_id()
        eel.add_DOM_element(
            self.property['parent_id'],
            'div',
            {
                'class': 'number_input_wrapper',
                'id': wrapper,
            }
        )
        eel.add_DOM_element(
            wrapper,
            'button',
            {
                'type': 'button',
                'class': 'decrement',
                'onclick': 'document.getElementById(\'{}\').stepDown()'.format(
                    self.id
                ),
            }
        )
        eel.add_DOM_element(
            wrapper,
            'input',
            {
                'id': self.id,
                'type': 'number',
                'name': self.property['name'],
                'value': value,
                'min': min_,
                'max': max_,
            }
        )
        eel.add_DOM_element(
            wrapper,
            'button',
            {
                'type': 'button',
                'class': 'increment',
                'onclick': 'document.getElementById(\'{}\').stepUp()'.format(
                    self.id
                ),
            }
        )


class Code_Block(UI_Element):
    """ Creates an element to display code.
    
    Kwargs:
        Required:
            code (str): the code to display
        Additional:
            parent_id (str): ID of the parent DOM element 
    """
    _required = ['code']
    _additional = ['parent_id']

    def construct_DOM_elements(self):
        parent_id = self.property['parent_id']
        code = self.property['code']
        eel.add_DOM_element(
            parent_id,
            'div',
            {
                'id': self.id,
                'class': 'code_block',
            }
        )
        Paragraph(text=code).create(parent_id=self.id)


class Button_List(UI_Element):
    """ Creates a strip to display button elements.
    
    Kwargs:
        Required:
            content (List[Button_Element]): list of button elements
        Additional:
            parent_id (str): ID of the parent DOM element 
    """
    _required = ['content']
    _additional = ['parent_id']

    def construct_DOM_elements(self):
        for element in self.property['content']:
            if not isinstance(element, Button):
                raise ValueError('Button_List can only contain Buttons!')
        parent_id = self.property['parent_id']
        eel.add_DOM_element(
            parent_id,
            'div',
            {
                'id': self.id,
                'class': 'button_list',
            }
        )
        for element in self.property['content']:
            element.create(parent_id=self.id)

    def destroy(self):
        for element in self.property['content']:
            element.destroy()
        eel.remove_DOM_element(self.id)
