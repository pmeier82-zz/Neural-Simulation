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
# sim - data_io.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-02-15
#

"""data io classes for the simulation"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
import os
from os import path as osp
# packages
import scipy as N
import tables
# own imports
from package import SimPkg
from data_thread import DataThread


##---CLASSES

class SimClient(DataThread):
    """client wrapper"""

    def __init__(self, addr, ident):
        """
        :Parameters:
            addr : tuple
                Host address and port tuple
            ident : long
                ident of the recorder this client is attached to.
        """

        # super
        super(SimClient, self).__init__(addr=addr)

        # members
        self.ident = ident

class SimIOManager(object):
    """the singleton input/output manager

    This class handles all data input and output for a SimBase object. Data is
    received from and sent to instances of SimIOBase. The manager is a
    dict of SimIOBase instances.
    """

    ## constructor

    def __init__(self, **kwargs):
        """
        :Parameters:
            kwargs : keywords
        :Keywords:
            addr : str
                Host address the server binds to.
                Default=all
            port : int
                Host port the server binds to.
                Default=31337
        """

        # members
        self._status = None

        # io members
        self.addr = kwargs.get('addr', '')
        self.port = kwargs.get('port', None)
        self._srv = None
        self._clt = []

    def initialize(self):

        if self._srv is not None:
            self.finalize()
        self._srv = DataThread(addr=('', self.port), is_server=True)
        self._srv.start()
        self.status = None

    def finalize(self):

        if not self._srv.is_shutdown:
            self._srv.stop()
            self._srv.join(5.0)
        self._srv = None

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

    def tick(self):

        # inits
        rval = []

        # server socket query
        while not self._srv.q_recv.empty():
            pkg = self._srv.q_recv.get_nowait()
            # TODO: handle client request
        for clt in self._clt:
            while not clt.q_recv.empty():
                rval.append(clt.q_recv.get_nowait())
        return rval

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

        if len(self._clt) > 0:

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


##---MAIN

if __name__ == '__main__':

    pass
