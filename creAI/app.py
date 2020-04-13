def run():
    import os

    import creAI.globals
    creAI.globals.cli_mode = False

    import eel
    #import creAI.ui

    ui_path = os.path.join( os.path.dirname(os.path.abspath(__file__)), 'web')
    eel.init(ui_path)
    eel.start('index.html', block=False)

    import creAI.plugins

    while True:
    	eel.sleep(10)