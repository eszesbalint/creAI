import tensorflow as tf

from creAI.plugins.file_manager.formats.tilemaps.minecraft_tilemaps import Minecraft_Tilemap
from creAI.plugins.style_transfer.data_generator import Random_Data_Generator
import creAI.plugins.style_transfer

def generate(model_name: str) -> Minecraft_Tilemap:
    model = tf.keras.models.load_model(model_name + '.h5')
