def run():
    import os

    import creAI.globals
    creAI.globals.cli_mode = False

    import eel
    # import creAI.ui

    ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
    eel.init(ui_path)
    eel.start('index.html', block=False)

    plugins_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'plugins')
    plugins = [
        name for name in os.listdir(plugins_path)
        if os.path.isdir(os.path.join(plugins_path, name)) and name != '__pycache__'
    ]

    for plugin in plugins:
        __import__('creAI.plugins.' + plugin, locals(), globals())

    del plugins

    while True:
        eel.sleep(10)
