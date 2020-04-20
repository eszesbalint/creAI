from setuptools import setup, find_packages

setup(
    name='creAI',
    version='0.1',
    author='Eszes Bálint',
    author_email='eszes.balint96@gmail.com',
    url='https://github.com/ebalint96/creAI',
    packages=find_packages(),
    install_requires=[
        'Eel',
        'Pillow',
        'numpy',
            'tensorflow',
    ],
    extras_require={
        'training': ['keras-tuner', 'dirt @ git+https://github.com/pmh47/dirt.git'],
    }
)
