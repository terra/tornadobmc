# -*- coding: utf-8 -*-

import os
from distutils.core import setup

setup(
    name='tornadobmc',
    version='0.0.3',
    description=('Asynchronous MemCache client using Binary protocol for Tornado (Python)'),
    author='Roi Avidan',
    author_email='roi.avidan@corp.terra.com.br',
    url='http://github.com/Terra/tornadobmc',
    packages=['tornadobmc'],
    license=open(os.path.join(os.path.dirname(__file__), 'LICENSE')).read(),
    install_requires=['tornado>=3.2'],
    platforms=['any']
)

