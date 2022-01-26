from setuptools import setup, find_packages
from os import path


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name = 'p2pshare',
    author='Dhrumil Mistry',
    version = '1.0.0',
    license='MIT License',
    description = 'Peer to Peer file transfer over the network',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data = True,
    install_requires = [
        'wheel',
        'tqdm',
    ],
)