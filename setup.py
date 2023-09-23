import os
import re
from setuptools import setup, find_packages


def read_requirements(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        install_requires = [line.strip() for line in f.readlines() if line.strip()]
    return install_requires


def get_version():
    with open(os.path.join(os.path.dirname(__file__), 'owl', '__init__.py'), 'r', encoding='utf-8') as f:
        return re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', f.read(), re.M).group(1)


CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

desktop_requires = ['ultralytics']
rpi_requires = []

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='openweedlocator-tools',
    version=get_version(),
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'desktop': desktop_requires,
        'rpi': rpi_requires
    },
    author='Guy Coleman',
    author_email='hoot@openweedlocator.com',
    classifiers=CLASSIFIERS,
    license='MIT',
    maintainer_email="guy.coleman@sydney.edu.au",
    description='A toolkit for green-on-brown and green-on-green weed detection',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/geezacoleman/openweedlocator-tools',
)
