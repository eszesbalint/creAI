import os

default_save_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'models'
)
import glob

def get_model_list():
    return [
        os.path.basename(f) 
        for f in glob.glob(os.path.join(default_save_path, '*.h5'))
    ]

def get_full_path(filename):
    return os.path.join(default_save_path, filename)