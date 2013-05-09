#!/usr/bin/env python

from distutils.core import setup


setup(
    name='SVG-Optimizer',
    version='0.1',
    description='Python program to clean up SVG files, particularly those created by Inkscape or Illustrator',
    author='Peter Collingridge',
    author_email='peter.collingridge@gmail.com',
    url='https://github.com/petercollingridge/SVG-Optimiser',
    py_modules=['cleanSVG'],
    install_requires=open('requirements.txt').readlines(),
)
