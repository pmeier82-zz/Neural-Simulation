##!/usr/bin/env python
## -*- coding: utf-8 -*-
################################################################################
##
##  Copyright 2010 Philipp Meier <pmeier82@googlemail.com>
##
##  Licensed under the EUPL, Version 1.1 or – as soon they will be approved by
##  the European Commission - subsequent versions of the EUPL (the "Licence");
##  You may not use this work except in compliance with the Licence.
##  You may obtain a copy of the Licence at:
##
##  http://ec.europa.eu/idabc/eupl
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the Licence is distributed on an "AS IS" basis,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the Licence for the specific language governing permissions and
##  limitations under the Licence.
##
################################################################################
#
# setup.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-07-05
#

##---IMPORTS

import os
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup


##---HELPERS

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


##---STRINGS

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.6',
    'Topic :: Scientific/Engineering :: Bio-Informatics'
]
DESCRIPTION = 'A simulation framework for extracellular recordings.'
LONG_DESCRIPTION = """%s

%s
""" % (DESCRIPTION, read('README'))

##---SETUP BLOCK

setup(
    # names and description
    name='Neural-Simulation',
    version='0.2.0',
    author='Philipp Meier',
    author_email='pmeier82@googlemail.com',
    maintainer='Philipp Meier',
    maintainer_email='pmeier82@googlemail.com',
    url='http://ni.cs.tu-berlin.de',
    download_url='http://github.com/pmeier82/Neural-Simulation/zipball/master',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    # package distribution
    packages=['nsim',
              'nsim.io',
              'nsim.gui',
              'nsim.math',
              'nsim.scene',
              'nsim.scene.neuron_data',
              'nsim.scene.noise'],
    package_data={'res':['*.*'],
                  'nsim.gui':['*.ui', '*.qrc', '*.png']},
    zip_safe=False,
    include_package_data=True,
    license='EUPL v1.1',
    classifiers=CLASSIFIERS,
    install_requires=[],
)
