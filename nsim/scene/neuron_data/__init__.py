#﻿# -*- coding: utf-8 -*-
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
# nsim - scene/neuron_data/__init__.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-09-13
#

"""interface for neuron data objects"""
__docformat__ = 'restructuredtext'


##---IMPORTS

from neuron_data import NeuronData, NeuronDataContainer
from ndata_sampled import SampledND, get_eap_range

##---PACKAGE

__all__ = [
    # lerp
    'lerp1',
    'lerp2',
    'lerp3',
    # neuron data interface
    'NeuronData',
    'NeuronDataContainer',
    # sampled neuron data
    'SampledND',
    'get_eap_range'
]


##---MAIN

if __name__ == '__main__':
    pass
