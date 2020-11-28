import argparse
import configparser
import json
import io
import sys
import platform
from os import PathLike
from os.path import join, dirname, abspath
import eel
import traceback

from creAI.style import Style
from creAI.cli import CommandlineInterface, command, default_command
from creAI.mc import Schematic
from creAI.mc.geometry import tilemap_to_geometry
import creAI.mc.version_manager




if getattr(sys, 'frozen', False):
    #Path to the configuration file
    CFG_PATH = join(sys._MEIPASS, 'cfg.ini')
    #Path to the user interface
    GUI_PATH = join(sys._MEIPASS, 'gui')
else:
    #Path to the configuration file
    CFG_PATH = join(dirname(abspath(__file__)), 'cfg.ini')
    #Path to the user interface
    GUI_PATH = join(dirname(abspath(__file__)), 'gui')

CFG = configparser.ConfigParser()
CFG.read(CFG_PATH)
creAI.mc.version_manager.MC_PATH = CFG['Minecraft']['InstallationPath']
DEBUG_MODE = bool(int(CFG['App']['DebugMode']))


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            if DEBUG_MODE:
                traceback.print_exc()
            else:
                try:
                    eel.exception_alert(str(e))
                except:
                    print(str(e))

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


class App(CommandlineInterface):
    """Generates Minecraft tilemaps via a selection of deep learning models.

    Run creAI without commandline parameters to start the graphical user
    interface, or use a subcommand from below.
    """

    def __init__(self):
        #Init commandline interface
        super(App, self).__init__(prog='creAI')
        #Current tilemap
        self._tlmp = None
        #The last style used, for faster re-runs
        self._last_stl = None

    @command
    @handle_exceptions
    def list(self, styles, versions):
        """List subcommand.

        List available styles or installed Minecraft versions. These could be
        useful while training or generating.

        Args:
            styles (bool, optional): List available styles.
            versions (bool, optional): List installed Minecraft versions.
        """
        if styles:
            print('Styles:')
            for stl in Style.list_all():
                stl = Style(stl, load_models=False)
                print('{}\t{}'.format(stl.name, stl.info['mc_version']))

        if versions:
            print('Minecraft versions:')
            for v in creAI.mc.version_manager.versions():
                print(v)

    @command
    @handle_exceptions
    def config(self, mc_path, debug_mode):
        """Config subcommand.

        Use this command to change settings.

        Args:
            mc_path (str, optional): Set Minecraft installation path.
            debug_mode (int, optional): Wether or not to print the exception
                traceback. 

        """
        if mc_path is not None:
            CFG['Minecraft']['InstallationPath'] = mc_path
            with open(CFG_PATH, 'w') as cfg_file:
                CFG.write(cfg_file)

        if debug_mode is not None:
            CFG['App']['DebugMode'] = str(debug_mode)
            with open(CFG_PATH, 'w') as cfg_file:
                CFG.write(cfg_file)
        print('Config saved.')

    @command
    @handle_exceptions
    def train(self, mc_version, schem, style, icon, vae, generator, epochs, 
                                                                batch_size):
        """Training subcommand.

        Train or retrain different parts of a style. If the given style has
        not been created previously, it will be created. 
        The style is saved automatically at the end of each epoch, so you
        can resume training later.

        Args:
            style (str): The name of the style.
            icon (str, optional): Path to an image file. This will be
                displayed in the graphical user interface.
            vae (bool, optional): Use this flag to train the variational
                autoencoder part of the model.
            generator (bool, optional): Use this flag to train the generator
                part of the model.
            mc_version (str, optional): Specify the Minecraft version to
                train the VAE on. You don't have to give this for subsequent
                training sessions. It will be saved in the style file.
            epochs (int): Number of training epochs (ie how many times do
                you want the model to go through the whole training data).
                More epochs usually mean better accuracy.
            batch_size (int): Trainig samples to use from the training data
                at any given time. Smaller batch sizes use less memory, but
                the training will be slower.
            schem (str, optional): The Minecraft schematic file to use as a
                reference through training.
        """

        stl = Style(style, mc_version=mc_version, icon_pth=icon)
        stl.train(vae=vae, generator=generator, schem_pth=schem,
                  batch_size=batch_size, epochs=epochs)
        

    @command
    @handle_exceptions
    def generate(self, style=None, output=None):
        """Generate subcommand.

        This function is available from the graphical user interface too.

        Args:
            style (str): The style to generate.
            output (str): The generated tilemap will be saved here.
        """
        
        stl = Style(style)
        self._tlmp = stl.generate((16, 16, 16))
        if output is not None:
            with open(output, 'wb') as schem_file:
                self._tlmp.save(schem_file)
        print(self._tlmp)

    @default_command
    @handle_exceptions
    def start_gui(self):
        #Defining some functions to make the communication
        #between the App and the graphical user interface
        #a bit easier

        def get_style_list():
            return Style.list_all()
        
        def get_style_info(stl_name: str):
            stl = Style(stl_name, load_models=False)
            return {
                'name': stl.name,
                'mc_version': stl.info['mc_version'],
                'icon': list(stl.icon.to_byte_array())
            }

        def get_tilemap_geometry():
            if self._tlmp is None:
                return None

            geometry = tilemap_to_geometry(self._tlmp)

            geometry = {
                'vertices': geometry[0, :].flatten().tolist(),
                'normals': geometry[1, :].flatten().tolist(),
                'colors': geometry[2, :].flatten().tolist(),
            }

            return geometry

        def get_tilemap_schematic():
            if self._tlmp is None:
                return None

            buffer = io.BytesIO()

            self._tlmp.save(buffer)

            return bytearray(buffer.getvalue())

        def get_app_info():
            return {
                'description': self.description
            }

        self.get_style_list = get_style_list 
        self.get_style_info = get_style_info 
        self.get_tilemap_geometry = get_tilemap_geometry 
        self.get_tilemap_schematic = get_tilemap_schematic 
        self.get_app_info = get_app_info 

        #Exposing functions to the GUI
        func_to_expose = [
            self.get_style_list,
            self.get_style_info,
            self.get_tilemap_geometry,
            self.get_tilemap_schematic,
            self.get_app_info,
            self.generate
        ]
        for func in func_to_expose:
            eel.expose(func)

        #Starting the GUI
        eel.init(GUI_PATH)
        try:
            eel.start('index.html', block=False)
        except EnvironmentError:
            #If Chrome isn't found, fallback to Microsoft Edge on Win10
            if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
                eel.start('index.html', mode='edge', block=False)
            else:
                raise
        while True:
            eel.sleep(10)

    

