from creAI.Plugins.FileManager.file_manager import *

import creAI.UI
import creAI.Globals
import eel

plugin_name = 'FileManager'
plugin_title = 'File manager'

def add_file_tag(id_):
	file_tag = id_
	eel.add_DOM_element('file_list', 'div', {'class' : 'file_tag', 'id' : file_tag})

	file_name = creAI.Globals.gen_id()
	menu_button_script = '{}.{}(\'{}\')'.format('eel', '{}_{}'.format(plugin_name, 'select'), id_)
	eel.add_DOM_element(id_, 'a', {'class' : 'menu_element', 'id' : file_name, 'onclick' : menu_button_script})
	eel.append_text(file_name, creAI.Globals.tilemaps[id_]['name'])

	close_button = creAI.Globals.gen_id()
	close_button_script = '{}.{}(\'{}\')'.format('eel', '{}_{}'.format(plugin_name, 'close'), id_)
	eel.add_DOM_element(file_tag, 'div', {'class' : 'menu_element', 'id' : close_button, 'onclick' : close_button_script})
	eel.add_DOM_element(close_button, 'div', {'class' : 'close icon'})

function_name = '{}_{}'.format(plugin_name, 'load')
@eel.expose(function_name)
def func_1(file_name, raw_data):
	id_ = load_schematic(file_name, raw_data)
	creAI.UI.display_selected_tilemap()
	add_file_tag(id_)

	

menu_button = creAI.Globals.gen_id()
menu_button_script = 'file_open_dialog(\'{}\', {})'.format('.schem', '{}.{}'.format('eel', function_name))
eel.add_DOM_element('main_menu', 'div', {'class' : 'menu_element', 'id' : menu_button, 'onclick' : menu_button_script})
eel.add_DOM_element(menu_button, 'div', {'class' : 'import icon'})

function_name = '{}_{}'.format(plugin_name, 'save')
@eel.expose(function_name)
def func_2():
	save_schematic(raw_data)

menu_button = creAI.Globals.gen_id()
menu_button_script = '{}()'.format(function_name)
eel.add_DOM_element('main_menu', 'div', {'class' : 'menu_element', 'id' : menu_button, 'onclick' : menu_button_script})
eel.add_DOM_element(menu_button, 'div', {'class' : 'export icon'})


function_name = '{}_{}'.format(plugin_name, 'close')
@eel.expose(function_name)
def func_3(id_):
	del creAI.Globals.tilemaps[id_]
	eel.remove_DOM_element(id_)
	eel.remove_tilemap(id_)

function_name = '{}_{}'.format(plugin_name, 'select')
@eel.expose(function_name)
def func_4(id_):
	eel.hide_tilemap(creAI.Globals.selected_tilemap_id)
	creAI.Globals.selected_tilemap_id = id_
	creAI.UI.display_selected_tilemap()