
import creAI.UI
import creAI.Globals
from creAI.Plugins.FileManager import add_file_tag


def generate():
	pass

plugin = creAI.UI.Plugin(
		icon_class = 'picture icon',
		name = 'StyleTransfer',
		title = 'Style transfer',
		description = 'Procedural building generator using real-time artistic style transfer.',
		content = [
			creAI.UI.Button(text = 'Train'),
			creAI.UI.Button(text = 'Generate')
		]
	)
plugin.create()
creAI.UI.UI_ELEMENTS[plugin.id] = plugin

