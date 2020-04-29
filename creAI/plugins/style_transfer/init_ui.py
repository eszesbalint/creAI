import os
import eel
import creAI.ui

import creAI.plugins.file_manager.file_functions as FileManager
from creAI.plugins.style_transfer.model_manager import get_model_list




@eel.expose('StyleTransfer_train')
@creAI.ui.display_loading_animation('Training')
@creAI.ui.display_error_message_on_error
def train(kwargs: dict):
    from creAI.plugins.style_transfer.train import train

    batch_size = int(kwargs['vae_batch_size'])
    epochs = int(kwargs['vae_epochs'])
    latent_dim = int(kwargs['vae_latent_dim'])
    model_name = kwargs['save_as']

    tilemap = FileManager.files[FileManager.selected]['content']

    model = train(tilemap, model_name)

@eel.expose('StyleTransfer_generate')
@creAI.ui.display_loading_animation('Generating')
@creAI.ui.display_error_message_on_error
def generate(kwargs: dict):
    from creAI.plugins.style_transfer.generate import generate
    model_name = int(kwargs['model_name'])
    tilemap = generate(model_name)





plugin = creAI.ui.Plugin(
    icon_class='picture icon',
    name='StyleTransfer',
    title='Style transfer',
    description='Procedural building generator using real-time artistic style transfer.',
    content=[
        creAI.ui.Title(text='Training'),
        creAI.ui.Form(
            script = creAI.ui.function_to_script(train),
            content = [
                creAI.ui.Input(type_='text', name='save_as',
                               label='Save model as', value='model.h5'),
                creAI.ui.Number_Input(name='vae_epochs',
                               label='VAE Epochs', min_='1', value='100'),
                creAI.ui.Number_Input(name='vae_batch_size',
                               label='VAE Batch size', min_='1', value='32', max_='256'),
                creAI.ui.Number_Input(name='vae_latent_dim',
                               label='VAE latent dim', min_='1', value='8'),
                creAI.ui.Button(type_ = 'submit', text='Train'),
            ]
        ),
        creAI.ui.Title(text='Generation'),
        creAI.ui.Form(
            script = creAI.ui.function_to_script(generate),
            content=[
                creAI.ui.Paragraph(text='Select trained model'),
            ]
            + [
                creAI.ui.Radio_Input(name='model_name', value=s, label=s)
                for s in get_model_list()
            ]
            + [
                creAI.ui.Number_Input(name='test', label='Width'),
                creAI.ui.Number_Input(name='test', label='Height'),
                creAI.ui.Number_Input(name='test', label='Length'),
                creAI.ui.Button(type_='submit', text='Generate'),
            ]
        ),
    ]
)
plugin.create()

