from setuptools import setup, find_packages

from codecs import open
from os import path

PACKAGE_NAME = 'ucapi'
HERE = path.abspath(path.dirname(__file__))
VERSION = '0.0.1'

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description="Python wrapper for the Unfolded Circle Integration API",
    url="https://unfoldedcircle.com",
    author="Unfolded Circle ApS",
    author_email="hello@unfoldedcircle.com",
    license="MIT",
    packages=['ucapi'],
    include_package_data=True,
    install_requires=find_packages()
    )
