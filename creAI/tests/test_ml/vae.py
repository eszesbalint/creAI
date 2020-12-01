from os.path import join, dirname

from creAI import Style
import creAI.style

from creAI.mc import Tile
from creAI.mc.tile import vectorize

from creAI.cli import CommandlineInterface, command

creAI.style.STYLES_PATH = join(dirname(__file__), 'test_styles')


class VaeTest(CommandlineInterface):
    """Testing VAE.

    This is a simple test program for the VAE implemented in
    creAI/ml/models/vae.py
    """
    def __init__(self):
        super(VaeTest, self).__init__()
        

    @command
    def train(self, style):
        """Training mode.

        This subcommand has no additional parameters.

        Args:
            style (str): Name of the style.
        """
        self.stl = Style(style, mc_version='1.15.2')
        self.stl.train(vae=True, batch_size=64, epochs=300)
    
    @command
    def display(self, style):
        """Display mode.

        This subcommand displays a plot of the latent space.
        Args:
            style (str): Name of the style.
        """
        self.stl = Style(style, mc_version='1.15.2')
        vae = self.stl.models.vae

        vae_data = Tile.vectorize_all(self.stl.info['mc_version'])
        encodings = vae.encoder.predict(vae_data)[0]

        tiles = [
            Tile('minecraft:quartz_stairs[half=bottom]', version='1.15.2'),
            Tile('minecraft:birch_stairs[half=bottom]', version='1.15.2'),
            Tile('minecraft:brick_stairs[half=bottom]', version='1.15.2'),
            Tile('minecraft:bricks', version='1.15.2'),
            Tile('minecraft:nether_bricks', version='1.15.2'),
            Tile('minecraft:white_carpet', version='1.15.2'),
            Tile('minecraft:snow[layers=1]', version='1.15.2')
            ]

        vae_data = vectorize(tiles, pad_to=vae.input_dim)
        encodings_subset = vae.encoder.predict(vae_data)[0]

        import matplotlib.pyplot as plt

        fig=plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(encodings[:,0], encodings[:,1], c=[[.9,.9,.9]], marker='x')
        ax.scatter(encodings_subset[:,0], encodings_subset[:,1], color='r', marker='x')
        for idx, t in enumerate(tiles):
            ax.annotate(t.name, (encodings_subset[idx,0], encodings_subset[idx,1]))
        ax.set_title('Minecraft tile-ok 2D látenstere')
        plt.show()

VaeTest().run()