from creAI.Tilemaps.MinecraftTilemaps import Schematic
import creAI.Globals
import creAI.UI


@creAI.UI.display_loading_animation('Loading schematic')
@creAI.UI.display_error_message_on_error
def load_schematic(file_name, raw_data):
	raw_data = bytearray(raw_data.values())
	tilemap = Schematic.load(None, raw_data)

	id_ = creAI.Globals.gen_id()
	creAI.Globals.tilemaps[id_] = {'name' : file_name, 'tilemap' : tilemap}
	creAI.Globals.selected_tilemap_id = id_

	return id_

	

def save_schematic():
	tilemap = creAI.Globals.tilemaps[creAI.Globals.selected_tilemap_id]['tilemap']
	Schematic.save(tilemap, "saving_test.schem")