# -*- coding: utf-8 -*-
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
# sim - sim_objects/data/__init__.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-01-21
#

"""interface for datafiles from Einevoll group"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
import os
import os.path as osp
# packages
from tables import openFile, NoSuchNodeError
import scipy as N
from scipy.special import cbrt
# own packages
from lerp import LERP3


##---CLASSES

class NeuronData(object):
    """data container to access the neuron data provided by Einevoll group

    The archives contain a sampling of voltage data recorded in the vincinity of
    a simulated pyramidal cell. The data has an isotrope spatial and temporal
    sampling that is derived from the data and stored with the class instance.

    The data is generated from a NEURON model that simulates the intracellular
    currents and interactions based on the works of ... TODO: add reference!

    The data contained in the archive is placed in an array that has a row of
    data per temporal sample, and a column for each spatial sample. The data is
    sampled temporally for the duration of one action potential temporally (from
    the very beginning of the intracellular hyper-polarization until the resting
    potential is re-established.

    reaching the intracellular resting potential is re
    """

    ## constructor

    def __init__(self, filepath):
        """
        :Parameters:
            filepath : path
                Path to a HDF5 archive.
            extraction_time_vector : sequence
                The sequence of sample in the time domain that should be
                contained as a full waveform.
                Default=xrange(150,250)
        :Exceptions:
            IOError:
                Error finding or reading in the archive.
            NosuchNodeError:
                Error finding a data node in the archive.
            ValueError:
                Error for inconsistent archive contents while calculatiing
                interals.
        """

        ## read in data - may raise IOError or NoSuchNodeError

        arc = openFile(filepath, 'r')

        # read in the all data
        self.data = arc.getNode('/LFP').read().T

        # time frame
        soma_v = arc.getNode('/soma_v').read()
        self.time_frame = xrange(*get_eap_range(soma_v))
        self.data = self.data[..., self.time_frame]

        # voltage traces
        self.time_vec = arc.getNode('/time_vector').read()[..., self.time_frame]
        self.soma_v = arc.getNode('/soma_v').read()[..., self.time_frame]
        try:
            self.hill_v = arc.getNode('/hill_v').read()[..., self.time_frame]
        except NoSuchNodeError:
            self.hill_v = None

        # read in the data
        self.x_pos = arc.getNode('/el_pos_x').read()
        self.y_pos = arc.getNode('/el_pos_y').read()
        self.z_pos = arc.getNode('/el_pos_z').read()

        # read parameters
        self.params = {}
        for item in arc.getNode('/parameters'):
            self.params[item.name] = item.read()

        # close and delete archive
        arc.close()
        del arc

        ## compute internals

        # sphere radius
        if not (
            abs(self.x_pos.min()) ==
            abs(self.x_pos.max()) ==
            abs(self.y_pos.min()) ==
            abs(self.y_pos.max()) ==
            abs(self.z_pos.min()) ==
            abs(self.z_pos.max())
        ):
            raise ValueError('spatial resolution is not cubic!')
        # SAFETY: because in the very unlikely event of a query on the outermost bundary of the sampling
        # grid in which case the interpolation would not work, we have to decrease the sphere radius by
        # a itzy tiny bit
        self.sphere_radius = self.x_pos.max()*.999999
        # spatial info - spatial resolution: x > y > z
        self.grid_step = abs(self.z_pos[1] - self.z_pos[0])
        self.grid_size = cbrt(self.data.shape[0])
        # phase info
        self.phase_max = self.data.shape[1]
        self.phase_spike = self.soma_v.argmax()
        # sample rate
        self.sample_rate = 1.0
        if 'timeres_python' in self.params:
            self.sample_rate = 1000.0 / self.params['timeres_python']
        # filenames for caching
        self.filename = osp.basename(filepath)
        self.dirname = osp.dirname(filepath)

    ## interface methods

    def get_data(self, pos, phase=None):
        """return voltage data for position and phase
        pos is a relative position to the orientation of the neuron, i.e. pos is already in respect to the
        datagrid. We need the surrounding 8 grid positions and their waveforms for interpolation"""

        if phase is None:
            phase = xrange(self.time_vec.size)

        # scale the position in multiple of grid steps
        scaled_pos = pos / self.grid_step

        # calculate the reference position for interpolation. That is the corner of the cube in which the
        # polation takes place that is nearest to the origin
        reference_pos = N.floor(scaled_pos)

        #Grid coordinates of unit cube in which we want to interpolate
        x = N.array([0., 0., 0., 0., 1., 1., 1., 1.])+reference_pos[0]
        y = N.array([0., 1., 1., 0., 0., 1., 1., 0.])+reference_pos[1]
        z = N.array([0., 0., 1., 1., 0., 0., 1., 1.])+reference_pos[2]

        v = N.zeros((8, len(phase)))

        for i in xrange(8):
            v[i, :] = self.data[NeuronData.pos_kernel(N.array([x[i], y[i], z[i]]), self.grid_size), phase]

        alpha = scaled_pos - reference_pos

        return LERP3(
            alpha[0], alpha[1], alpha[2],
            v[0], v[4], v[1], v[5],
            v[3], v[7], v[2], v[6]
        )

    ## position kernel

    @staticmethod
    def pos_kernel(pos, grid_size):
        """kernel to compute array index for grid position

        :Parameters:
            pos : ndarray/list
                3d position
            grid_size : int
                size of the grid
        """

        offset = (grid_size - 1) / 2
        return (
            grid_size**2 * (pos[0] + offset) +
            grid_size * (pos[1] + offset) +
            (pos[2] + offset)
        )

    ## specials methods
    def __str__(self):
        return '%s from %s' % (self.__class__.__name__, self.filename)

    def __eq__(self, other):
        if not isinstance(other, NeuronData):
            return False
        else:
            return self.filename == other.filename
    def __hash__(self):
        return hash(ospp.join(self.dirname, self.fname))


class NeuronDataContainer(dict):
    """container for NeuronData objects"""

    ## constructor

    def __init__(self):

        # super
        super(NeuronDataContainer, self).__init__()
        self.paths = set([])

    ## public methods

    def insert(self, items):
        """insert a single NeuronData

        :Parameters:
            item : list
                A list of stings and or NeuronData objects, that will be added.
                If a str, it should be a valid path to an archive loading to a
                NeuronData or a directory containing such.
        :Returns:
            Count of successfully inserted NeuronData instances.
        """

        if not isinstance(items, list):
            items = [items]
        rval = 0

        for item in items:

            ndata = None

            # check what we have
            if isinstance(item, NeuronData):
                rval += self._insert(item)
                self.paths.update([ndata.dirname])
            elif isinstance(item, (str, unicode)):
                if osp.exists(item):
                    if osp.isfile(item):
                        try:
                            ndata = NeuronData(item)
                            rval += self._insert(ndata)
                            self.paths.update([ndata.dirname])
                        except:
                            continue
                    elif osp.isdir(item):
                        for f in os.listdir(item):
                            try:
                                ndata = NeuronData(osp.join(item, f))
                                rval += self._insert(ndata)
                                self.paths.update([ndata.dirname])
                            except Exception, ex:
                                continue

            else:
                continueq

        return rval

    ## private methods

    def _insert(self, item):
        """add a single NeuronData object to the container

        :Parameters:
            item : NeuronData
                The NeuronData object to add.
        :Return:
            bool : True on success, False on failure
        """

        if isinstance(item, NeuronData):
            if item.filename in self:
                return False
            else:
                self.__setitem__(item.filename, item)
                return True
        else:
            return False

    ## dict interface

    def clear(self):
        super(NeuronDataContainer, self).clear()
        self.paths = set([])


##---FUNCTIONS

def get_eap_range(soma_v):
    """return the indices where the eap has a significant waveform"""

    my_soma = N.concatenate((soma_v[3:].copy(), N.ones(5) * soma_v[-1]))
    soma_func = lambda x: my_soma[x]
    der1 = [N.derivative(soma_func, i) for i in xrange(soma_v.size)]
    der1 = N.absolute(N.asarray(der1[1:]))
    start = stop = (der1 > 1e-1).argmax()
    stop += (der1[stop:] > 1e-2).argmin()
    return start, stop


##---PACKAGE

__all__ = ['NeuronData', 'NeuronDataContainer']


##---MAIN

if __name__ == '__main__':

    from pylab import plot, figure, show
    from mpl_toolkits.mplot3d import Axes3D
    from datetime import datetime, timedelta

    neuron = NeuronData('/home/phil/SVN/Data/Einevoll/LFP-20100517_235609.h5')

    fig_phil = figure()
    ax_phil = Axes3D(fig_phil)
    times_phil = timedelta()

    x_value = neuron.time_vec.copy()

    for i in xrange(200):

        # plot phil interpolation
        t0 = datetime.now()
        wave = neuron.get_data(
            N.array((-10+.1*i, -10+.1*i, -10+.1*i))*neuron.grid_step
        )
        t1 = datetime.now()
        times_phil += t1 - t0
        ax_phil.plot(x_value, wave, i)

    fig_phil.suptitle('Trilinear Interpolation - method="phil" - %s' % times_phil)

    show()
