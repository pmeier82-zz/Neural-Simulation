# -*- coding: utf-8 -*-
#
# sim - data_io.py
#
# Philipp Meier - <pmeier82 at gmail dot com>
# 2010-02-15
#
# $Id: manager.py 4839 2010-06-01 16:55:46Z phil $
#

"""data io classes for the simulation"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
import os
from os import path as osp
from Queue import Queue
# packages
import scipy as N
import tables
# own imports
from package import SimPkg
from server import SimServer


##---CLASSES

class SimIOManager(object):
    """the singleton input/output manager

    This class handles all input and output for a SimBase object. Input and
    output is received from and sent to instances of SimIOBase. The manager is a
    dict of SimIOBase instances.
    """

    ## constructor

    def __init__(self, **kwargs):

        # status
        self._status = kwargs.get('status', None)

        # queues and buffer
        self._q_read = None
        self._q_writ = None
        self._pkg_buf = []

        # server
        self.port = kwargs.get('port', None)
        self._srv = None

    def initialize(self):

        # setup server
        self.setup_svr()

        # reset members
        self.pkg_buf = []
        self.rcv_buf = []
        self.status = None

        # start server its thread/process
        self._srv.start()
        self._srv.handshake = self.get_status_pkg()

    def finalize(self):

        self.cleanup_svr()

    def setup_svr(self):

        if self._srv is not None:
            self.cleanup_svr()

        self._q_read = Queue()
        self._q_writ = Queue()
        self._srv = SimServer(
            port=self.port,
            q_read=self._q_read,
            q_writ=self._q_writ
        )

    def cleanup_svr(self):

        if not self._srv.is_shutdown:
            self._srv.stop()
            self._srv.join(5.0)
        self._srv = None
        self._q_read = None
        self._q_writ = None

    ## properties

    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        if not isinstance(value, dict):
            return
        if self._status != value:
            self._status = value
            self.send_status()

    ## methods interface

    def get_status_pkg(self):
        """build a package from self.status

        items are mapped by id:
            0   : sample_rate
            1   : frame_size
            10  : neurons
            20  : recorders
        """

        try:
            status = self.status
            cont = N.array([
                [status['sample_rate'], 0],
                [status['frame_size'], 1]
            ])
            if len(self.status['neurons']) > 0:
                cont = N.vstack((
                    cont,
                    [[item, 10] for item in status['neurons']]
                ))
            if len(status['recorders']) > 0:
                cont = N.vstack((
                    cont,
                    [[item, 20] for item in status['recorders']]
                ))
            return SimPkg(tid=SimPkg.T_STS, cont=cont.astype(long))
        except:
            return None

    ## io methods

    def send_wf_neuron(self, frame, ident, cont):
        """pipe neuron waveform for recorder to server

        :Parameters:
            frame : long
                frame id
            ident : long
                recorder id
            cont : ndarray
                the waveform data
        """

        if self._q_writ is not None:
            self._q_writ.put(
                SimPkg(
                    tid=SimPkg.T_WFU,
                    ident=ident,
                    frame=frame,
                    cont=cont
                )
            )

    def send_wf_noise(self, frame, ident, cont):
        """receive noise data for recorder

        :Parameters:
            frame : long
                frame id
            ident : int/long
                recorder id
            cont : ndarray
                the noise data
        """

        if self._q_writ is not None:
            pkg = SimPkg(
                tid=SimPkg.T_WFN,
                ident=ident,
                frame=frame,
                cont=cont
            )
            self._q_writ.put(pkg)

    def send_groundtruth(self, frame, ident, cont):
        """receive noise data for recorder

        :Parameters:
            frame : long
                frame id
            ident : int/long
                neuron id
            cont : ndarray
                the waveform data
        """

        if self._q_writ is not None:
            self._q_writ.put(
                SimPkg(
                    tid=SimPkg.T_GTR,
                    ident=ident,
                    frame=frame,
                    cont=cont
                )
            )

    def send_position(self, frame, ident, cont):
        """receive noise data for recorder

        :Parameters:
            frame : long
                frame id
            ident : int/long
                simobject id
            cont : ndarray
                position data
        """

        if self._q_writ is not None:
            self._q_writ.put(
                SimPkg(
                    tid=SimPkg.T_POS,
                    ident=ident,
                    frame=frame,
                    cont=cont
                )
            )

    def send_status(self):
        """send the status package"""

        pkg = self.get_status_pkg()
        if pkg is not None:
            if self._q_writ is not None:
                self._q_writ.put(pkg)
            if self._srv is not None:
                self._srv.handshake = pkg

    def query_input(self):
        """returns any input events since last query"""

        rval = []
        if self._q_read is not None:
            while not self._q_read.empty():
                rval.append(self._q_read.get_nowait())
        return rval


##---MAIN

if __name__ == '__main__':

    pass
