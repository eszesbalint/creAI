import creAI.globals
from creAI.plugins.file_manager.file_functions import delete, load, read, select

if not creAI.globals.cli_mode:
    import creAI.ui
    plugin = creAI.ui.Plugin(
        icon_class='import icon',
        name='FileManager',
        title='File Manager',
        description='Loading and saving files.',
        content=[
            creAI.ui.Button(
                text='Load',
                script=creAI.ui.function_to_script(load)
            ),
            creAI.ui.Button(text='Save')
        ]
    )
    plugin.create()

    btn_1 = creAI.ui.Menu_Element(
        text='Load',
        icon_class='import icon',
        script=creAI.ui.function_to_script(load)
    )
    btn_2 = creAI.ui.Menu_Element(
        text='Save',
        icon_class='export icon',
        script=creAI.ui.function_to_script(load)
    )
    btn_1.create(parent_id='main_menu')
    btn_2.create(parent_id='main_menu')
