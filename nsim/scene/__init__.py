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
# sim - scene/__init__
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-03-23
#

"""scene package

This package contains objects that interact in the SCENE
"""
__docformat__ = 'restructuredtext'


##---IMPORTS

from neuron_data import NeuronData, NeuronDataContainer
from sim_object import SimObject
from neuron import Neuron
from recorder import Recorder, Tetrode


##---PACKAGE

__all__ = [
    'BadNeuronQuery',
    # from data
    'NeuronData',
    'NeuronDataContainer',
    # from sim_object
    'SimObject',
    # from neuron
    'Neuron',
    # from recorder
    'Recorder',
    'Tetrode'
]


##---MAIN

if __name__ == '__main__':
    pass
