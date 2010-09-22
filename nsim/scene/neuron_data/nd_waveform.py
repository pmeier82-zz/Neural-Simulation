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
# nsim - scene/neuron_data/nd_waveform.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-09-13
#

"""interface for datafiles based on singe-channel waveforms"""
__docformat__ = 'restructuredtext'


##---IMPORTS

from tables import openFile
import scipy as N
from neuron_data import NeuronData
from nsim.math import vector_norm


##---CLASSES

class WaveformND(NeuronData):
    """data container to access the neuron data build from a waveform
    
    This NeuronData implementation is generated from a single-channel waveform
    that is scaled with a distance kernel.
    """

    ## constructor

    def __init__(self,
                 waveform=N.ones(32),
                 sample_rate=16000.0,
                 horizon=100.0,
                 **kwargs):
        """
        :Parameters:
            waveform : ndarray
                The single-channel waeform as a one-dimensional ndarray.
                Default=ones(32) 
            sample_rate : float
                Sample rate of the waveform in Hz.
                Default=16000.0
        :Keywords:
            see NeuronData
        :Exceptions:
            see NeuronData
        """

        # super
        super(WaveformND, self).__init__(**kwargs)

        # interface members
        self.intra_v = waveform.copy()
        self.extra_v = waveform.copy()
        self.horizon = horizon
        self.sample_rate = sample_rate

    ## interface methods - implementations

    def _get_data(self, pos, phase):
        """return voltage data for position and phase
        
        Will scale the waveform with a distant dependent kernel.
        """

        return WaveformND.kernel(pos) * self.extra_v[phase]


    ## class methods

    @classmethod
    def from_file(cls, path_to_arc, rootUEP='/'):
        """factory to create an SampledND from an archive
        
        :Parameters:
            path_to_arc : str
                Path to the archive to load from
            rootUEP : str
                user entry path
        :Return:
            WaveformND : if successfully loaded from the file
            None : on any error
        """

        try:
            # are we good to go ?
            arc = openFile(path_to_arc, mode='r', rootUEP='/')
            TYPE = arc.getNode('/__TYPE__').read()
            assert TYPE == 'NeuronData'
            CLASS = arc.getNode('/__CLASS__').read()
            assert CLASS == cls.__name__
            # load stuff
            param_waveform = arc.getNode('/waveform').read()
            param_horizon = arc.getNode('/horizon').read()
            param_sample_rate = arc.getNode('/sample_rate').read()
            param_description = None
            try:
                param_description = arc.getNode('/description').read()
            except:
                param_description = 'Waveform_undefined'
            return cls(
               waveform=param_waveform,
               horizon=param_horizon,
               sample_rate=param_sample_rate,
               description=param_description
            )
        except:
            return None
        finally:
            try:
                arc.close()
                del arc
            except:
                pass

    ## static methods

    @staticmethod
    def kernel(pos):
        """computes scaling kernel based on the relative position vector
                
        :Parameters:
            pos : ndarray
                A three-dimensional relative position.
        :Returns:
            scale : scalar scaling factor on [0.0, 1.0]
        """

        return 1.0


class ScalingWaveformND(WaveformND):
    """data container for the neural simulation (see WaveformND)
       
    This subclass of WaveformND implements a realistic scaling kernel as:
    phi(dist) = 1.0 / 4 * pi * dist**2 
    """

    @staticmethod
    def kernel(pos):
        """computes scaling kernel based on the relative position vector
                
        :Parameters:
            pos : ndarray
                A three-dimensional relative position.
        :Returns:
            scale : scalar scaling factor on [0.0, 1.0]
        """

        return 1.0 / (4.0 * N.pi * vector_norm(pos) ** 2)



##---PACKAGE

__all__ = ['ScalingWaveformND', 'WaveformND']


##---MAIN

if __name__ == '__main__':
    pass
