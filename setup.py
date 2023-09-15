from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt', 'r') as req:
        content = req.read()
        requirements = content.split('\n')

    return requirements

setup(
    name='openweedlocator-toolkit',
    version='0.0.1',
    packages=find_packages(),
    install_requires=read_requirements(),
    author='Guy Coleman',
    author_email='hoot@openweedlocator.com',
    description='A toolkit for green-on-brown and green-on-green weed detection',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/geezacoleman/openweedlocator-tools',
)
