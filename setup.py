from setuptools import setup, find_packages

import os
import re

def read_requirements():
    with open('requirements.txt', 'r') as req:
        content = req.read()
        requirements = content.split('\n')

    return requirements

# ==================== VERSIONING ====================

with open(os.path.join(os.path.dirname(__file__), 'owl', '__init__.py'), 'r') as f:
    version = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', f.read(), re.M).group(1)

setup(
    name='openweedlocator-toolkit',
    version=version,
    packages=find_packages(),
    install_requires=read_requirements(),
    author='Guy Coleman',
    author_email='hoot@openweedlocator.com',
    maintainer_email="guy.coleman@sydney.edu.au",
    description='A toolkit for green-on-brown and green-on-green weed detection',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/geezacoleman/openweedlocator-tools',
)
