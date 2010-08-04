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

from setuptools import setup, find_packages

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None


##---STINGS

##required
NAME = 'Neural Simulation'
VERSION = '0.3.a12'
URL = 'http://ni.cs.tu-berlin.de'
DESCRIPTION = 'A simulation framework for extracellular recordings'
## mandatory
AUTHOR = 'Neural Simulation Team'
AUTHOR_EMAIL = 'ff@ni.cs.tu-berlin.de'
MAINTAINER = 'Philipp Meier'
MAINTAINER_EMAIL = 'pmeier82@googlemail.com'
## long strings
LONG_DESCRIPTION = """%s

Extracellular recordings are a key tool to study the activity of
neurons in vivo. Especially in the case of experiments with behaving
animals, however, the tedious procedure of electrode placement can
take a considerable amount of expensive and restricted experimental
time. Furthermore, due to tissue drifts and other sources of
variability in the recording setup, the position of the electrodes
with respect to the neurons under study can change, causing low
recording quality. Here, we developed a system online simulation of
extracellular recordings that allows for feedback from electrode
positioning systems and recording systems.

The simulator is based on realistically reconstructed 3D neurons. The
shape of the extracellular waveform is estimated from their morphology
for every point on a 3D grid around the neurons. If a recording device
is close to a neuron, the corresponding waveform for its spikes is
calculated from that grid by interpolating the waveforms of the
adjacent grid positions. This way we can simulate a realistic
recording environment in which an unconstrained movement of electrodes
and neurons and an interaction with a positioning system and online
spike sorter is possible.
""" % DESCRIPTION

##---SETUP BLOCK

setup(
    # package identification
    name=NAME,
    version=VERSION,
    # contact information
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    url=URL,
    # description strings
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    # package paths
    packages=['nrl_sim'],
    package_dir={
        '':'src'
    },
    # package option
    zip_safe=False,
    include_package_data=True,
    # licens information
    license='EUPL v1.1',
    # trove classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Environment :: X11 Applications :: Qt',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ]
)
