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
# sim - sim_objects/recorder.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-01-21
#

"""simulation object - recorder class"""
__doctype__ = 'restructuredtext'


##---IMPORTS

# packages
import scipy as N
# own packages
from sim_object import SimObject
from neuron import BadNeuronQuery, Neuron
from noise import NoiseGen, ArNoiseGen
from nsim.math import unit_vector


##---CLASSES

class Recorder(SimObject):
    """multichanneled recorder object with an intrinsic noise process

    If the Recorder has self._points, these correspond to the recorder channels.
    Else there will be only one channel at self.position.
    """

    ## constructor
    def __init__(self, **kwargs):
        """
        :Keywords:
            snr : float
                Signal to Noise Ratio (SNR) for the noise process.
                Default=1.0
            noise : bool
                If False, do not setup noise generator. For setup in subclass
                Default=True
        """

        # super
        super(Recorder, self).__init__(**kwargs)

        # members
        self._origin = self.position.copy()
        if self.points is None:
            self.nchan = 1
        else:
            self.nchan = self.points.shape[0]
        self._noise_gen = None
        self._snr = None
        traj = kwargs.get('orientation', N.asarray([0.0, 0.0, 1.0]))
        if traj is True or traj is False:
            traj = [0.0, 0.0, 1.0]
        self._trajectory = unit_vector(traj)
        self._trajectory_pos = None

        # set from kwargs
        self.snr = kwargs.get('snr', 1.0)
        self.trajectory_pos = 0.0
        noise = kwargs.get('noise', True)
        if noise is True:
            self._noise_gen = NoiseGen(mu=N.zeros(self.nchan))

    ## properties

    def get_origin(self):
        return self._origin
    origin = property(get_origin)

    def get_snr(self):
        return self._snr
    def set_snr(self, value):
        if value <= 0.0:
            raise ValueError('cannot set SNR <= 0.0')
        self._snr = float(value)
    snr = property(get_snr, set_snr)

    def get_trajectory(self):
        return self._trajectory
    def set_trajectory(self, value):
        self._trajectory = value
    trajectory = property(get_trajectory, set_trajectory)

    def get_trajectory_pos(self):
        return self._trajectory_pos
    def set_trajectory_pos(self, value):
        self._trajectory_pos = float(value)
        self.position = self.origin + self._trajectory_pos * self.trajectory
    trajectory_pos = property(get_trajectory_pos, set_trajectory_pos)

    ## methods public

    def simulate(self, nlist=[], frame_size=1):
        """record a multichanneled frame from neurons in range

        :Parameters:
            nlist : list
                List of Neuron instances to record from.
                Default=[]
            frame_size : int
                Size of the frame in samples.
                Default=1
        :Returns:
            list : A list of items for this frame. The first item is the noise
            for this frame. Subsequent items are tuples of waveform and interval
            data for the neurons that have significant (not all zero) waveforms
            in this frame for this recorder.
        """

        # init
        rval = None
        if self._noise_gen is None:
            rval = [N.zeros((frame_size, self.nchan))]
        else:
            rval = [self._noise_gen.query(size=frame_size) / self.snr]

        # for each neuron query waveform and firing data
        for nrn in nlist:
            try:
                rval.extend(nrn.query_for_recorder(self.points[:self.nchan]))
            except BadNeuronQuery:
                continue

        # return
        return tuple(rval)


class Tetrode(Recorder):
    """tetrode object, resembling a tetrode as build by Thomas Recording GmbH"""

    # constructor
    def __init__(self, **kwargs):
        """
        :Keywords:
            noise_params : list
                List with 2 matricies, [ar parameters, channel covariance] with
                consistant shapes.
                Default=None
        """

        # tetrode points
        hz = 0.5 * N.sqrt(3)
        s3o6 = N.sqrt(3) / 6.0
        points = N.array([
            [  0.0, 0.0, 0.0 ], # tip electrode
            [ -0.5, -s3o6, -hz ], # south west rear electrode
            [  0.5, -s3o6, -hz ], # south east rear electrode
            [  0.0, 2 * s3o6, -hz ], # north rear electrode
        ])
        points *= N.array([[40] + 3 * [20]]).T # match to TRec scales
        kwargs.update(points=points)

        # super
        super(Tetrode, self).__init__(noise=False, **kwargs)

        # noise AR model from munk data
        noise_params = kwargs.get('noise_params', None)
        if noise_params is not None:
            try:
                # list of len 2
                assert len(noise_params) == 2
                # ar parameters consistent with points
                assert noise_params[0].shape[0] == self.nchan
                # channel covariance
                assert noise_params[1].shape[0] == noise_params[1].shape[1] == self.nchan
            except:
                noise_params = None
        if noise_params is None:
            noise_params = [
                N.array([
                    [ 0.71442494, 0.20257086, -0.00850916, 0.2368369 ,
                     - 0.24215925, -0.17167059, 0.0125938 , -0.23022224,
                      0.12538984, 0.04433236, -0.00631453, 0.1004515 ],
                    [-0.03496567, 0.87848262, 0.00826437, 0.07128014,
                      0.03575446, -0.33148169, 0.03356261, -0.03429215,
                     - 0.02584761, 0.15418811, -0.00396265, 0.01696292],
                    [-0.00501744, 0.15455094, 0.74612578, 0.15237156,
                      0.02853695, -0.10804699, -0.2478788 , -0.12939667,
                     - 0.03661882, 0.04972772, 0.14696973, 0.04525116],
                    [-0.02562255, 0.08109374, -0.01441578, 0.81397469,
                      0.03561313, -0.04552583, 0.03256103, -0.31543032,
                     - 0.01135552, 0.01822465, -0.01507197, 0.13653283]
                ]),
                N.array([
                    [ 0.02120132, 0.0046539 , 0.00629694, 0.00614801],
                    [ 0.0046539 , 0.02226795, 0.00402148, 0.00663766],
                    [ 0.00629694, 0.00402148, 0.01920582, 0.00401457],
                    [ 0.00614801, 0.00663766, 0.00401457, 0.02340445]
                ])
            ]
        self._noise_gen = ArNoiseGen(noise_params)


##---PACKAGE

__all__ = ['Recorder', 'Tetrode']


##---MAIN

if __name__ == '__main__':

    # inits
    from neuron import NeuronData
    import pylab as P
    frame_size = 500
    ndpath = '/home/phil/SVN/Data/Einevoll/LFP-20100516_225124.h5'
    ftimes = [0]

    # neuron
    print
    print 'build neuron'
    nd = NeuronData(ndpath)
    n = Neuron(neuron_data=nd)

    # tetrode
    print
    print 'Building Tetrode'
    t = Tetrode(snr=3.0)
    print t
    print 'snr:', t.snr

    # noise frame
    print
    print 'noise frame'
    frame = t.simulate(nlist=[], frame_size=frame_size)
    print frame
    f = P.figure()
    P.plot(frame)

    print
    print 'spike frame'
    n.simulate(frame_size=frame_size, firing_times=ftimes)
    frame = t.simulate(nlist=[n], frame_size=frame_size)
    print frame
    f = P.figure()
    P.plot(frame)

    # finalize
    P.show()
