import eel

import creAI.globals
import creAI.plugins.panel_generator.generator
import creAI.ui
import creAI.plugins.file_manager.file_manager as FM



@eel.expose('PanelGenerator_generate')
@creAI.ui.display_loading_animation('Training')
@creAI.ui.display_error_message_on_error
def generate(kwargs):
    w, h, l = int(kwargs['width']), int(kwargs['height']), int(kwargs['length'])
    tilemap = creAI.plugins.panel_generator.generator.generate(w, h, l)
    id_ = str(id(tilemap))
    FM.add(
        id_,
        {
            'name': 'Generated',
            'format': 'schem',
            'content': tilemap
        }
        )


plugin = creAI.ui.Plugin(
    icon_class='link icon',
    name='PanelGenerator',
    title='Panel generator',
    description='Procedural building generator with shape grammars.',
    content=[
        creAI.ui.Title(text='Parameters'),
        creAI.ui.Form(
            script = creAI.ui.function_to_script(generate),
            content = [
                creAI.ui.Number_Input(name='width',
                               label='width', min_='1', value='30', max_='256'),
                creAI.ui.Number_Input(name='height',
                               label='height', min_='1', value='30', max_='256'),
                creAI.ui.Number_Input(name='length',
                               label='length', min_='1', value='30', max_='256'),
                creAI.ui.Button(type_ = 'submit', text='Generate'),
            ]
        ),
    ]
)
plugin.create()

