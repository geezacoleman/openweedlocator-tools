import os
import re
from setuptools import setup, find_packages


def read_requirements(filename):
    with open(filename, 'r+') as req_file:
        return req_file.read().splitlines()


def get_version():
    with open(os.path.join(os.path.dirname(__file__), 'owl', '__init__.py'), 'r') as f:
        return re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', f.read(), re.M).group(1)


setup(
    name='openweedlocator-toolkit',
    version=get_version(),
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'desktop': read_requirements('requirements_desktop.txt'),
        'rpi': read_requirements('requirements_rpi.txt')
    },
    author='Guy Coleman',
    author_email='hoot@openweedlocator.com',
    maintainer_email="guy.coleman@sydney.edu.au",
    description='A toolkit for green-on-brown and green-on-green weed detection',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/geezacoleman/openweedlocator-tools',
)
