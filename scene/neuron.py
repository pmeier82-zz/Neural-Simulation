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
from scipy.stats import poisson
# own packages
from sim_object import SimObject
from math3d import quaternion_matrix, vector_norm
from data import NeuronData


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

        self._interv_overshoot = []
        self._interv_waveform = []
        self._firing_times = []

        # set from kwargs
        self.active = True
        self.amplitude = kwargs.get('amplitude', 1.0)
        self.rate_of_fire = kwargs.get('rate_of_fire', 10.0)

    ## properties

    @property
    def active(self):
        return self._active
    @active.setter
    def active(self, value):
        self._active = bool(value)

    @property
    def amplitude(self):
        return self._amplitude
    @amplitude.setter
    def amplitude(self, value):
        self._amplitude = float(value)

    @property
    def rate_of_fire(self):
        return self._rate_of_fire
    @rate_of_fire.setter
    def rate_of_fire(self, value):
        self._rate_of_fire = float(value)
        if self._rate_of_fire <= 0.0:
            self._rate_of_fire = 1.0

    @property
    def sphere_radius(self):
        return self._neuron_data.sphere_radius

    ## event slots

    def simulate(self, **kwargs):
        """this method simulates the neurons firing behavior

        :Keywords:
            frame_size : int
                Size of the frame to simulate
            firing_times : list
                list of int representing sample where the neuron fires in the
                frame. obviously fireing_times[i] < frame_size!
        """

        # get kwargs and init
        self._firing_times = kwargs.get('firing_times', [])
        self._frame_size = kwargs.get('frame_size', 1)
        self._interv_waveform = []

        # check if we are active
        if self.active is False:
            return

        # overshooting waveform intervals from last frame
        if len(self._interv_overshoot) > 0:
            self._interv_waveform = self._interv_overshoot
            self._interv_overshoot = []

        # waveform intervals for this frame
        for t in self._firing_times:
            start = [t, 0]
            end = [t + self._neuron_data.phase_max, self._neuron_data.phase_max]

            # check if waveform overshoots
            if end[0] >= self._frame_size:
                residual = end[0] - self._frame_size
                end = [self._frame_size, self._neuron_data.phase_max - residual]
                self._interv_overshoot.append([0, end[1]])
                self._interv_overshoot.append([residual, self._neuron_data.phase_max])

            # add interval
            self._interv_waveform.append(start)
            self._interv_waveform.append(end)

    ## methods public

    def query_for_position(self, pos):
        """return the voltage trace for this neuron for the current frame

        :Keywords:
            pos : arraylike
                absolute 3d-position of the listener
        :Returns:
            The waveform of this neuron of length 'frame_size'.
        :Raises:
            ValueError : if self._frame_size is None or the position is outside
            of the listening spehere of the neuron.
        """

        # check for valid position
        rel_pos = pos - self.position
        if vector_norm(rel_pos) > self.sphere_radius:
            raise ValueError('queried position outside of sphere_radius')

        # inits
        rval = N.zeros(self._frame_size)

        # if we have orientation, rotate rel_pos accoringly
        if self.orientation is not False:
            rel_pos = N.dot(
                quaternion_matrix(self.orientation)[:3,:3],
                rel_pos
            )

        # copy waveform stips
        if len(self._interv_waveform) > 0:
            temp = self._neuron_data.get_data(rel_pos)
            for i in xrange(0, len(self._interv_waveform), 2):
                start = self._interv_waveform[i]
                end = self._interv_waveform[i+1]
                rval[start[0]:end[0]] = temp[start[1]:end[1]]

        # adjust for amplitude and return
        if self.amplitude != 1.0:
            rval *= self.amplitude
        return rval


##---PACKAGE

__all__ = ['Neuron']

##---MAIN

if __name__ == '__main__':
    pass
