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
# sim - sim_objects/neuron.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-01-21
#

"""simulation object - neuron"""
__doctype__ = 'restructuredtext'


##---IMPORTS

# packages
import scipy as N
# own packages
from sim_object import SimObject
from math3d import quaternion_matrix, vector_norm
from data import NeuronData


##---EXCEPTIONS

class BadNeuronQuery(Exception):
    pass


##---CLASSES

class Neuron(SimObject):
    """neuron class for the simulator"""

    ## constructor
    def __init__(self, **kwargs):
        """
        :Keywords:
            neuron_data : NeuronData or path
                Reference to a NeuronData object. This is required, not setting
                the neuron_data will result in an exception.
                Default=None
            rate_of_fire : float
                Rate of fire in Hz.
                Default=10.0
            amplitude : float
                Amplitude of the waveform
                Default=1.0
        """

        # check neuron_data
        if 'neuron_data' not in kwargs:
            raise ValueError('no neuron_data passed!')
        ndata = kwargs.get('neuron_data')
        if not isinstance(ndata, NeuronData):
            raise ValueError('neuron_data is a %s' % ndata.__class__.__name__)

        # super
        super(Neuron, self).__init__(**kwargs)

        # members
        self._active = None
        self._amplitude = None
        self._rate_of_fire = None
        self._frame_size = None
        self._neuron_data = ndata

        self._interval_overshoot = []
        self._interval_waveform = []
        self._firing_times = []

        # set from kwargs
        self.active = True
        self.amplitude = kwargs.get('amplitude', 1.0)
        self.rate_of_fire = kwargs.get('rate_of_fire', 10.0)

    ## properties

    def get_active(self):
        return self._active
    def set_active(self, value):
        self._active = bool(value)
    active = property(get_active, set_active)

    def get_amplitude(self):
        return self._amplitude
    def set_amplitude(self, value):
        self._amplitude = float(value)
    amplitude = property(get_amplitude, set_amplitude)

    def get_rate_of_fire(self):
        return self._rate_of_fire
    def set_rate_of_fire(self, value):
        self._rate_of_fire = float(value)
        if self._rate_of_fire <= 0.0:
            self._rate_of_fire = 1.0
    rate_of_fire = property(get_rate_of_fire, set_rate_of_fire)

    def get_sphere_radius(self):
        return self._neuron_data.sphere_radius
    sphere_radius = property(get_sphere_radius)

    ## event slots

    def simulate(self, **kwargs):
        """this method simulates the neurons firing behavior

        :Keywords:
            frame_size : int
                Size of the frame to simulate
            firing_times : list
                list of int representing sample where the neuron fires in the
                frame. obviously firing_times[i] < frame_size!
        """

        # get kwargs and init/reset
        self._firing_times = kwargs.get('firing_times', [])
        self._frame_size = kwargs.get('frame_size', 1)
        self._interval_waveform = []

        # check if we are active
        if not self.active:
            return

        # overshooting waveform intervals from last frame
        if len(self._interval_overshoot) > 0:
            self._interval_waveform = self._interval_overshoot
            self._interval_overshoot = []

        # waveform intervals for this frame
        for t in self._firing_times:
            start = [t, 0]
            end = [t + self._neuron_data.phase_max, self._neuron_data.phase_max]

            # check if waveform overshoots
            if end[0] >= self._frame_size:
                residual = end[0] - self._frame_size
                end = [self._frame_size, self._neuron_data.phase_max - residual]
                self._interval_overshoot.append([0, end[1], residual, self._neuron_data.phase_max])

            # add interval
            self._interval_waveform.append([start[0], end[0], start[1], end[1]])

            # DEBUG: start
            for interv in self._interval_waveform:
                if interv[1] - interv[0] != interv[3] - interv[2]:
                    raise ValueError('intervals do not match: %s' % interv)
            for interv in self._interval_overshoot:
                if interv[1] - interv[0] != interv[3] - interv[2]:
                    raise ValueError('intervals do not match: %s' % interv)
            # DEBUG: end

    ## methods public

    def query_for_recorder(self, positions):
        """return the multichanneled waveform and firing times for this neuron
        for the current frame. The multichanneled waveform is build from the
        positions passed, yielding a [positions, frame_size] matrix with one
        channel per column.

        :Parameters:
            positions : ndarray
                Points of the recorder
        :Returns:
            tuple : (waveform, interval_waveforms)
        :Raises:
            BadNeuronQuery : if self._frame_size is None or the position is outside
            of the listening sphere of the neuron.
        """

        # check for any valid positions
        rel_pos = positions - self._position
        rel_pos_valid = [
            vector_norm(rel_pos[i]) < self._neuron_data.sphere_radius
            for  i in xrange(rel_pos.shape[0])
        ]
        if not N.any(rel_pos_valid):
            raise BadNeuronQuery('queried position(s) outside of sphere_radius')

        # inits
        wf = N.zeros((self._neuron_data.time_vec.size, rel_pos.shape[0]))

        # if we have orientation, rotate rel_pos accordingly
        if self._orientation:
            rel_pos = N.dot(
                quaternion_matrix(self._orientation)[:3, :3],
                rel_pos.T
            ).T

        # copy waveforms per position (resp. channel)
        for i in xrange(rel_pos.shape[0]):
            if rel_pos_valid[i]:
                wf[:, i] = self._neuron_data.get_data(rel_pos[i])
        # adjust for amplitude
        if self._amplitude != 1.0:
            wf *= self._amplitude

        # return
        return id(self), wf, self._interval_waveform


##---PACKAGE

__all__ = ['BadNeuronQuery', 'Neuron']


##---MAIN

if __name__ == '__main__':
    pass
