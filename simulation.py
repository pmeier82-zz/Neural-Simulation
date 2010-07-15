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
# sim - simulation.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-01-21
#

"""simulation framework for extracellular recordings

This module provides a discrete time event simulation framework for objects
placed in a 3-dimensional space (refered to as the scene). Objects have a
distinct position in the scene for each point in time. Time is descretized to
samples with a fixed sample rate. This way the realtime/observed simulation
speed is decoupled from the internal time scale and can be changed on the fly.

Objets are classified as either Recorders or Neurons and are modeled as
subclasses of SimObject. A SimObject is a set of scene coordinates, along with a
set of applicable behaviors. E.g. Neurons can have a firing statistic.

The simulation is conducted in frames. A Frame is a batch of samples that is
simulated as one step of the simulation. Any input to the simulation while a
frame is processed is queued and applied at the end of the frame (applies to
movement etc.).

The framework is tailored towards simulation of extracellular recordings with
several (1 to 10) Recorders and clusters of Neurons (3 clusters, 10 each).

Recorded data can be either saved to files (HDF5) or broadcasted to the net via
TCP/IP with a simple protocoll.

Definition of terms:
:SCENE:
    The SCENE is the spatial context of the simulation (usually a 3D space with
    euclidean coordinates). Time is advanced with respect to a fixed sampling
    rate and the SCENE has a destinct configuration per sample. There is only
    one SCENE.
:OBJECT:
    An OBJECT is a subclass of SimObject. OBJECTs model all agents and sources
    in the SCENE, they are administrated as items of the BaseSimulation instance
    .
:SAMPLE:
    A SAMPLE is the smallest discrete time step known to the simulation. It is
    thus the unit of measurement for the temporal sampling. A SAMPLE i related
    to real time via the SAMPLE_RATE, denoting the SAMPLEs in a second (Hz).
:FRAME:
    A FRAME is a fixed time period of n samples. The simulation is advanced in
    frames. It is computationally attractive to simulate FRAMEs as oposed to
    single SAMPLEs, as most numerical algorithms perform better on batch data
    than on single SAMPLEs. Also timer implementations of normal systems may not
    provide the resolution neccessary to simulate common sampling rates (like
    16kHz or 32kHz) in real time.
"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
from ConfigParser import ConfigParser
import os.path as osp
# packages
import scipy as N
# own packages
from cluster_dynamics import ClusterDynamics
from data_io import SimIOManager, SimPkg
from scene import (
    NeuronDataContainer,
    NeuronData,
    Neuron,
    Recorder,
    SimObject,
    Tetrode
)


##---VERSION

try:
    __version__ = 'rev. %s - %s %s' % tuple(
        '$Id: simulation.py 4857 2010-06-09 14:59:29Z phil $'.split(' ')[2:5]
    )
except:
    __version__ = 'unknown'


##---CONSTANTS

MOVEMENT_TOL = 1e-5


##---CLASSES

class SimExternalDelegate(object):
    """delegate class, subclass for specific GUI kit or other interface

    An instance of SimExternalDelegate should pass messages/events on to a
    suitable external interface, like a GUI kit (frex QT or GTK). As we must not
    make assumptions about the frontend, we have the frontend operate on a
    suitably customized subclass of his delegate.
    """

    ## constructor

    def __init__(self, **kwargs):
        """
        :Parameters:
            kwargs : dict
                Keywords for subclasses
        """

        pass

    ## event delegate methods

    def log(self, log_str):
        """log a sting"""
        pass

    def frame(self, frame):
        """update frame"""
        pass

    def frame_size(self, frame_size):
        """update frame size"""
        pass

    def sample(self, sample):
        """update sample"""
        pass

    def sample_rate(self, sample_rate):
        """update sample rate"""
        pass

    def info_internal(self, info):
        """update internal infos"""
        pass

    def info_ndata(self, info):
        """update neuron data infos"""
        pass

    def info_neuron(self, info):
        """update neuron infos"""
        pass

    def info_recorder(self, info):
        """update recorder infos"""
        pass

    def info_complete(self, info):
        """update complete infos"""
        pass


class BaseSimulation(dict):
    """simulation class controlling the scene"""

    ## constructor

    def __init__(self, **kwargs):
        """
        :Parameters:
            kwargs : dict
                Keyword arguments, see Keywords.
        :Keywords:
            debug : bool
                Debug output toggle.
                Default=False
            externals : list
                A list of SimExternalDelegate instances. Internal state changes
                will be propagated to the delegates.
                Default=False
            sample_rate : float
                Sample rate.
            frame : int
                Frame to start at.
            frame_size : int
                Frame size.
            cfg : str
                Path to a config file, readable by a ConfigParser instance.
        """

        # private property members
        self._cfg = None
        self._externals = []
        self._frame = None
        self._frame_size = None
        self._sample_rate = None
        self._status = None

        # public members
        self.cls_dyn = ClusterDynamics()
        self.io_man = SimIOManager()
        self.neuron_data = NeuronDataContainer()
        self.debug = kwargs.get('debug', False)

        # externals
        for ext in kwargs.get('externals', []):
            if not isinstance(ext, SimExternalDelegate):
                continue
            self._externals.append(ext)

    def initialize(self, **kwargs):
        """initialize the simulation

        :Keywords:
            debug : bool
                Debug flag, enables verbose output.
                Default=False
            frame : long
                Frame id to start at.
                Default=0
            frame_size : int
                The frame size.
                Default=16
            sample_rate : float
                Sample rate to operate.
                Default=16000.0
        """

        self.clear()

        # reset pubic members
        self.cls_dyn.clear()
        self.io_man.initialize()
        self.neuron_data.clear()

        # reset private members
        self.sample_rate = kwargs.get('sample_rate', 16000.0)
        self.frame = kwargs.get('frame', 0)
        self.frame_size = kwargs.get('frame_size', 1024)
        self.status

    def finalize(self):
        """finalize the simulation"""

        self.clear()

        # reset pubic members
        self.cls_dyn.clear()
        self.io_man.finalize()
        self.neuron_data.clear()

    ## properties

    @property
    def frame(self):
        return self._frame
    @frame.setter
    def frame(self, value):
        self._frame = long(value)
        for ext in self._externals:
            ext.frame(self.frame)

    @property
    def frame_size(self):
        return self._frame_size
    @frame_size.setter
    def frame_size(self, value):
        self._frame_size = int(value)
        for ext in self._externals:
            ext.frame_size(self.frame_size)
        self.status

    @property
    def sample_rate(self):
        return self._sample_rate
    @sample_rate.setter
    def sample_rate(self, value):
        self._sample_rate = float(value)
        self.cls_dyn.sample_rate = self.sample_rate
        for ext in self._externals:
            ext.sample_rate(self.sample_rate)
        self.status

    @property
    def status(self):
        self._status = {
            'frame_size'    : self.frame_size,
            'sample_rate'   : self.sample_rate,
            'neurons'       : self.neuron_keys,
            'recorders'     : self.recorder_keys,
        }
        if self.io_man.status != self._status:
            self.io_man.status = self._status
        return self._status

    @property
    def neuron_keys(self):
        return [
            id(nrn) for nrn in filter(
                lambda x: isinstance(x, Neuron),self.values()
            )
        ]

    @property
    def recorder_keys(self):
        return [
            id(rec) for rec in filter(
                lambda x: isinstance(x, Recorder),self.values()
            )
        ]

    ## simulation controll methods

    def simulate(self):
        """advance the simulation by one frame"""

        # process events
        self._simulate_events()

        # process units
        self._simulate_neurons()

        # record for recorders
        self._simulate_recorders()

        # inc frame counter
        self.frame += 1

    def _simulate_events(self):
        """process events for the current frame"""

        # process
        while len(self.io_man.events) > 0:

            pkg = self.io_man.events.pop(0)

            log_str = 'Event:'

            if pkg.ident in self:

                # recorder event
                if isinstance(self[pkg.ident], Recorder):

                    log_str +='R[%s]:' % pkg.ident

                    # position event
                    if pkg.tid == SimPkg.T_POS:

                        pos_data = pkg.cont[0]

                        # position request
                        if pos_data.size == 1:
                            log_str += 'MOVE[%s] - request' % (
                                self[pkg.ident].name
                            )

                        # reposition request
                        elif pos_data.size == 2:
                            pos, vel = pos_data
                            log_str += 'MOVE: %s, %s' % (pos, vel)
                            self[pkg.ident].trajectory_pos = pos
                            # TODO: implemementation of the velocity component

                        # weird position event
                        else:
                            print 'weird event, was T_POS with:', pos_data
                            continue

                        # send position aknowledgement
                        self.io_man.send_position(
                            self._frame,
                            pkg.ident,
                            self[pkg.ident].trajectory_pos
                        )

                # neuron event
                elif isinstance(self[pkg.ident], Neuron):
                    log_str += 'N:ANY\n%s' % pkg

                # log
                self.log(log_str)

            # other event
            else:

                log_str += 'O[%s]:' % pkg.ident
                if pkg.tid == SimPkg.T_CON:
                    log_str += 'CONNECT from %s' % str(pkg.cont)
                elif pkg.tid == SimPkg.T_END:
                    log_str += 'DISCONNECT from %s' % str(pkg.cont)
                else:
                    log_str += 'unknown'
                self.log(log_str)

    def _simulate_neurons(self):
        """generate spiketrains for the current frame"""

        # generate spike trains fo the scene
        self.cls_dyn.generate(self.frame_size)

        # propagate spike trains to neurons
        for nrn_k in self.neuron_keys:
            nrn = self[nrn_k]
            firing_times = self.cls_dyn.get_spike_train(nrn_k)
            nrn.simulate(frame_size=self.frame_size, firing_times=firing_times)

    def _simulate_recorders(self):
        """recorder operation for the current frame"""

        # list of all neurons
        nlist = [self[nrn_k] for nrn_k in self.neuron_keys]

        # record per recorder
        for rec_k in self.recorder_keys:
            rec = self[rec_k]
            wf_neuron, wf_noise = self[rec_k].simulate(
                nlist=nlist,
                frame_size=self.frame_size
            )

            self.io_man.send_wf_neuron(self.frame, id(rec), wf_neuron)
            self.io_man.send_wf_noise(self.frame, id(rec), wf_noise)

    ## methods logging

    def log(self, log_str):
        """log a string"""

        for ext in self._externals:
            ext.log('[#%09d] %s' % (self.frame, log_str))

    def log_d(self, log_str):
        """log a string"""

        if self.debug is True:
            for ext in self._externals:
                ext.log('[DEBUG] %s' % log_str)

    ## methods object management

    def register_neuron(self, **kwargs):
        """register a neuron to the simulation

        :Keywords:
            neuron_data : NeuronData or path or None
                Reference to a NeuronData object or a path to the HDF5 archive
                where the data can be load from.
                CAUTION! str != QString etc.. use str(neuron_data)!
            position : arraylike
                Position in the scene (x,y,z).
                Default=[0,0,0]
            orientation : arraylike
                Orientation of the object. If ndarray it is interpreted as
                direction of orientation relative to the scene's positive
                z-axis. If its a list or tuple, it is interpreted as a triple of
                euler angles relative to the scene's positive z-axis. If it is
                True a random rotation is created.
                Default=False
            rate_of_fire : float
                Rate of fire in Hz.
                Default=50.0
            amplitude : float
                Amplitude of the waveform.
                Default=1.0
            cluster : int
                The cluster idx
        :Raises:
            some error .. mostly ValueErrors for invalid parameters.
        :Returns:
            The string representation of the registered Neuron.
        """

        # check neuron data
        try:
            neuron_data = kwargs.pop('neuron_data')
        except:
            raise ValueError('No "neuron_data" given!')
        if neuron_data in self.neuron_data:
            ndata = self.neuron_data[neuron_data]
        else:
            if not self.neuron_data.insert(neuron_data):
                raise ValueError('Unknown neuron_data: %s' % str(neuron_data))
            else:
                ndata = self.neuron_data[neuron_data]
        kwargs.update(neuron_data=ndata)

        # build neuron
        neuron = Neuron(**kwargs)
        self[id(neuron)] = neuron

        # register in cluster dynamics
        cls_idx = kwargs.get('cluster', None)
        if cls_idx is not None:
            cls_idx = int(cls_idx)
        self.cls_dyn.add_neuron(neuron, cls_idx=cls_idx)

        # log and return
        self.log('>> %s created!' % neuron)
        self.status
        return str(neuron)

    def register_recorder(self, **kwargs):
        """register a recorder for simulation

        :Keywords:
            position : array like
                Position in scene (x,y,z).
                Default=[0,0,0]
            orientation : arraylike or bool
                Orientation of the object. If ndarray it is interpreted as
                direction of orientation relative to the scene's positive
                z-axis. If its a list or tuple, it is interpreted as a triple of
                euler angles relative to the scene's positive z-axis. If it is
                True a random rotation is created.
                Default=False
            scale : float
                Scale factor for the Tetrahedron height. The default uses values
                from the Thomas Recording GmbH website, with a tetrode of about
                40µm height and 20µm for the basis triangle. Note that negative
                values invert the tetrode direction with respect to
                self.position.
                Default=1.0
            snr : float
                Signal to Noise Ratio (SNR) for the noise process.
                Default=1.0
                TODO: fix this value to be congruent with the neuron amplitudes.
            noise_params : list
                The noise generator parameters.
                Default=None
        :Raises:
            some error ..mostly ValueError for invalid parameters.
        :Returns:
            The string representation of the registered Recorder.
        """

        # build tetrode
        tetrode = Tetrode(**kwargs)
        self[id(tetrode)] = tetrode

        # connect and return
        self.log('>> %s created!' % tetrode)
        self.status
        return str(tetrode)

    def remove_object(self, key):
        """remove the SimObject with objectName 'key'

        :Parameters:
            key : SimObject or int/long
                A SimObject or the id of a SimObject attached (as int/long/str).
        :Returns:
            True on successful removal, False else.
        """

        # convert the key
        if isinstance(key, SimObject):
            lookup = id(key)
        elif isinstance(key, (str, unicode, int, long)):
            try:
                lookup = long(key)
            except:
                try:
                    lookup = long(key, 16)
                except:
                    return False
        else:
            return False

        # remove item
        try:
            item = self.pop(lookup)
            self.log('>> %s destroyed!' % item)
            self.status
            return True
        except:
            return False

    def scene_config_load(self, fname):
        """load a scene configuration file

        :Parameters:
            fname : str
                Path to the scene configuration file.
        """

        # checks and inits
        cfg = ConfigParser()
        cfg_check = cfg.read(fname)
        if fname not in cfg_check:
            raise IOError('could not load scene from %s' % fname)

        # check for config
        ndata_paths = cfg.get('CONFIG', 'neuron_data_dir')
        ndata_paths = ndata_paths.strip().split('\n')

        # read per section
        for sec in cfg.sections():

            # check section
            sec_str = sec.split(' ')
            cls = sec_str[0]
            if cls not in ['Neuron', 'Tetrode']:
                continue
            kwargs = {}
            if len(sec_str) > 1:
                kwargs['name'] = ' '.join(sec_str[1:])

            # elaborate class and keyword arguments
            for k, v in cfg.items(sec):

                # read items
                if k is None or v is None or k == '' or v == '':
                    continue
                elif k in ['position', 'orientation', 'trajectory']:
                    if v == 'False':
                        kwargs[k] = False
                    elif v == 'True':
                        kwargs[k] = True
                    else:
                        kwargs[k] = map(float, v.split(' '))
                elif k in ['neuron_data']:
                    kwargs[k] = v
                    if v not in self.neuron_data:
                        for path in ndata_paths:
                            self.neuron_data.insert(osp.join(path, v))
                else:
                    kwargs[k] = v

            # delegate action
            if cls == 'Neuron':
                self.register_neuron(**kwargs)
            elif cls == 'Tetrode':
                self.register_recorder(**kwargs)

    def scene_config_save(self, fname):
        """save the current scene configuration to a file

        :Parameters:
            fname : str
                Path to save tha cfg to.
        """

        # checks and inits
        cfg = ConfigParser()

        # write CONFIG section
        cfg.add_section('CONFIG')
        cfg.set('CONFIG', 'frame_size', self.frame_size)
        cfg.set('CONFIG', 'sample_rate', self.sample_rate)
        ndata_paths = '\t\n'.join(self.neuron_data.paths)
        cfg.set('CONFIG', 'neuron_data_dir', ndata_paths)

        # helper functions
        npy2cfg = lambda x: ' '.join(map(str, x.tolist()))

        # add per SimObject
        for obj in self.values():

            if isinstance(obj, Neuron):

                name = 'Neuron %s' % obj.name
                cfg.add_section(name)
                cfg.set(name, 'cluster', str(self.cls_dyn.get_cls_for_nrn(obj)))
                cfg.set(name, 'position', npy2cfg(obj.position))
                if obj.orientation is True or obj.orientation is False:
                    cfg.set(name, 'orientation', obj.orientation)
                else:
                    cfg.set(name, 'orientation', npy2cfg(obj.orientation))
                cfg.set(name, 'rate_of_fire', str(obj.rate_of_fire))
                cfg.set(name, 'amplitude', str(obj.amplitude))
                cfg.set(name, 'neuron_data', str(obj._neuron_data.filename))

            elif isinstance(obj, Recorder):

                name = 'Tetrode %s' % obj.name
                cfg.add_section(name)
                cfg.set(name, 'position', npy2cfg(obj.position))
                cfg.set(name, 'orientation', npy2cfg(obj._trajectory))
                cfg.set(name, 'snr', str(obj.snr))

        # save
        with open(fname, 'w') as save_file:
            cfg.write(save_file)

    ## methods config loading

    def load_config(self, cfg_path=None):
        """loads initialization values from file

        :Parameters:
            cfg_file : str
                Path to the config file. shoul be readale by a ConfigParser
                instance.
        """

        cfg = ConfigParser()



    ## special methods

    def __len__(self):
        return len(filter(lambda x: isinstance(x, Neuron), self.values()))

    def __str__(self):
        return 'BaseSimulation :: %d items' % len(self)


if __name__ == '__main__':

    print
    print 'creating BaseSimulation'
    sim = BaseSimulation()
