import creAI.Plugins.PanelGenerator.generator
import creAI.UI
import creAI.Globals
from creAI.Plugins.FileManager import add_file_tag

@creAI.UI.display_loading_animation('Generating tilemap')
def generate():
	tilemap = creAI.Plugins.PanelGenerator.generator.generate()
	id_ = creAI.Globals.gen_id()
	creAI.Globals.tilemaps[id_] = {'name' : 'Generated', 'tilemap' : tilemap}
	creAI.Globals.selected_tilemap_id = id_

	creAI.UI.display_selected_tilemap()
	add_file_tag(id_)

plugin = creAI.UI.Plugin(
		icon_class = 'link icon',
		name = 'PanelGenerator',
		title = 'Panel generator',
		description = 'Procedural building generator with shape grammars.',
		content = [
			creAI.UI.Button(function = generate, text = 'Generate')
		]
	)
plugin.create()
creAI.UI.UI_ELEMENTS[plugin.id] = plugin


