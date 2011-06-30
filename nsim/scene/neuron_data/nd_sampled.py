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
# nsim - scene/neuron_data/ndata_sampled.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-09-13
#

"""NeuronData implementation based on pre-sampled data on a voxel grid"""
__docformat__ = 'restructuredtext'


##---IMPORTS

import os.path as osp
from tables import openFile
import scipy as N
from scipy.special import cbrt
from neuron_data_base import NeuronData
from nsim.math import lerp3


##---ALL

__all__ = [
    'SampledND',
    'get_eap_range',
]


##---CLASSES

class SampledND(NeuronData):
    """data container to access neuron data provided by Einevoll group

    The archives contain a sampling of voltage data simulated on a voxel grid
    around a pyramidal cell. The data has an isotrope spatial and temporal
    sampling that is derived from the data and stored with the class instance.

    The data is generated from a NEURON model that simulates the intracellular
    currents and interactions based on the works of ... TODO: add reference!

    The data contained in the archive is placed in an array that has a row of
    data per temporal sample, and a column for each spatial sample. The data is
    sampled temporally for the duration of one action potential temporally (from
    the very beginning of the intracellular hyper-polarization until the resting
    potential is re-established.
    """

    ## constructor

    def __init__(self, path_to_arc, rootUEP='/', **kwargs):
        """
        :Parameters:
            path_to_arc : path
                Path to the HDF5 archive.
            rootUEP : str
                root in the archive used as the user entry path (UEP).
        :Keywords:
            see NeuronData
            clamp_soma_v : bool
                if True, try to find the significant part of the intracellular
                waveform.
        :Exceptions:
            IOError:
                Error finding or reading in the archive.
            NosuchNodeError:
                Error finding a data node in the archive.
            see NeuronData
        """

        # super
        super(SampledND, self).__init__(**kwargs)

        # read in data - may raise IOError or NoSuchNodeError
        arc = openFile(path_to_arc, mode='r', rootUEP=rootUEP)
        soma_v = arc.getNode('/soma_v').read()
        ap_phase = xrange(0, soma_v.size)
        if bool(kwargs.get('clamp_soma_v', True)) is True:
            ap_phase = xrange(*get_eap_range(soma_v))
        self.intra_v = arc.getNode('/soma_v').read()[..., ap_phase]
        LFP = arc.getNode('/LFP').read()
        if LFP.shape[0] < LFP.shape[1]:
            LFP = LFP.T
        self.extra_v = LFP[..., ap_phase]
        # read temporary data
        x_pos = arc.getNode('/el_pos_x').read()
        y_pos = arc.getNode('/el_pos_y').read()
        z_pos = arc.getNode('/el_pos_z').read()
        params = {}
        for item in arc.getNode('/parameters'):
            params[item.name] = item.read()
        # close and delete archive
        arc.close()
        del arc
        # horizon calculation
        if not (
            abs(x_pos.min()) ==
            abs(x_pos.max()) ==
            abs(y_pos.min()) ==
            abs(y_pos.max()) ==
            abs(z_pos.min()) ==
            abs(z_pos.max())
        ):
            raise ValueError('spatial shape is not cubic!')
        self.horizon = x_pos.max()

        # sample rate
        if 'timeres_python' in params:
            self.sample_rate = 1000.0 / params['timeres_python']

        # spatial info - spatial resolution: x > y > z
        self.grid_step = abs(z_pos[1] - z_pos[0])
        self.grid_size = cbrt(self.extra_v.shape[0])
        # filename stuff
        self.description = 'Einevoll::%s' % osp.basename(path_to_arc)

    ## interface methods - implementation

    def _get_data(self, pos, phase):
        """return voltage data for a position in the grid and phase
        
        Will query the surrounding 8 voxel positions for interpolation"""

        # find the reference position (closer to origin from real position)
        grid_pos = pos / self.grid_step
        ref_pos = N.floor(grid_pos)

        # voxel grid coordinates for interpolation values
        interp_cube = N.array([
            # x-y plane at z=0
            [ 0., 0., 0.],
            [ 1., 0., 0.],
            [ 0., 1., 0.],
            [ 1., 1., 0.],
            # x-y plane at z=1
            [ 0., 0., 1.],
            [ 1., 0., 1.],
            [ 0., 1., 1.],
            [ 1., 1., 1.],
        ]) + ref_pos

        # interpolation values
        v = N.zeros((8, len(phase)))
        for i in xrange(8):
            v[i, :] = self.extra_v[
                SampledND.pos_kernel(interp_cube[i], self.grid_size),
                phase
            ]
        # interpolation parameters
        alpha = grid_pos - ref_pos

        # return interpolated voltage trace
        return lerp3(
            alpha[0], alpha[1], alpha[2],
            v[0], v[1], v[2], v[3],
            v[4], v[5], v[6], v[7]
        )

    ## static methods

    @classmethod
    def from_file(cls, path):
        """factory to create an SampledND from an archive
        
        :Parameters:
            path : str
                Path to the archive to load from
        :Return:
            SampledND : if successfully loaded from the file
            None : on any error
        """

        try:
            return cls(path)
        except:
            return None


    @staticmethod
    def pos_kernel(pos, grid_size):
        """kernel to compute array index for grid position

        :Parameters:
            pos : ndarray/list
                3d position, relative to the voxel grid origin
            grid_size : int
                size of the voxel grid (cube side length in oxels)
        """

        offset = (grid_size - 1) / 2
        return (
            grid_size ** 2 * (pos[0] + offset) +
            grid_size * (pos[1] + offset) +
            (pos[2] + offset)
        )


##---FUNCTIONS

def get_eap_range(iap_v):
    """return the index range where the eap has a significant waveform
    
    based on the derivative of the iap, an index range is determined that will
    cover the course of the significant (that is non-zero) waveform for the eap.
    
    very heuristic.. might not work all the time
    """

    # this gets rid of apossible bump from 0 to x on the first samples and
    # extends the waveform for the derivative calculation
    my_iap = N.concatenate((iap_v[3:].copy(), N.ones(5) * iap_v[-1]))
    iap_func = lambda x: my_iap[x]
    der_1st = [N.derivative(iap_func, i) for i in xrange(iap_v.size)]
    der_1st = N.absolute(N.asarray(der_1st[1:]))
    start = stop = (der_1st > 1e-1).argmax()
    stop += (der_1st[stop:] > 1e-2).argmin()
    return start, stop


##---MAIN

if __name__ == '__main__':
    pass
