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

from distutils.core import setup


##---STINGS

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.6',
    'Topic :: Scientific/Engineering :: Bio-Informatics'
]
DESCRIPTION = 'A simulation framework for extracellular recordings'
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
    name='Neural Simulation',
    version='0.1.54',
    author='Philipp Meier',
    author_email='pmeier82@googlemail.com',
    maintainer='Philipp Meier',
    maintainer_email='pmeier82@googlemail.com',
    url='http://ni.cs.tu-berlin.de',
    download_url='http://github.com/pmeier82/Neural-Simulation/zipball/master',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=['nsim', 'nsim.data_io', 'nsim.gui', 'nsim.scene', 'nsim.scene.data', 'nsim.scene.noise'],
    package_data={'res':['*.*'],
                  'nsim.gui':['*.ui', '*.qrc', '*.png']},
    zip_safe=False,
    include_package_data=True,
    license='EUPL v1.1',
    classifiers=CLASSIFIERS
)
