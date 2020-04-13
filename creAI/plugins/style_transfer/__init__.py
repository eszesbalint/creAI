import os
import eel

import creAI.ui
import creAI.globals
import creAI.plugins.file_manager.file_manager as FileManager



@eel.expose('StyleTransfer_train')
@creAI.ui.display_loading_animation('Training')
@creAI.ui.display_error_message_on_error
def train(kwargs: dict):
    import creAI.plugins.style_transfer.tile_encoder as TileEncoder
    batch_size = int(kwargs['vae_batch_size'])
    epochs = int(kwargs['vae_epochs'])
    latent_dim = int(kwargs['vae_latent_dim'])
    data = TileEncoder.generate_training_data(
        FileManager.files[FileManager.selected]['content']
        )
    TileEncoder.train(data, batch_size, epochs, latent_dim)

default_save_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'models'
)

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
                creAI.ui.Input(type_='text', name='save_path',
                               label='Save model to', value=str(default_save_path)),
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
            script='',
            content=[
                creAI.ui.Input(type_='text', name='test', label='Load model from', value=str(
                    default_save_path)),
                creAI.ui.Number_Input(name='test', label='Width'),
                creAI.ui.Number_Input(name='test', label='Height'),
                creAI.ui.Number_Input(name='test', label='Length'),
                creAI.ui.Button(type_='submit', text='Generate'),
            ]
        ),
    ]
)
plugin.create()

