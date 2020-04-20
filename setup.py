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
        'deodr',
    ],
    extras_require={
        'training': ['tensorflow-gpu>=1.13.0, <1.14.0', 'dirt @ git+https://github.com/pmh47/dirt.git'],
    }
)
