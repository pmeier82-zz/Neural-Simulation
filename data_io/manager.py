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
from Queue import Queue
import tables
# own imports
from package import SimPkg
from data_thread import DataThread


##---CLASSES

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
        self.addr_ini = kwargs.get('addr', '')
        self.addr = None
        self.port_ini = kwargs.get('port', 31337)
        self.port = None
        self._q_recv = Queue()
        self._srv = None
        self._clt = {}
        self._events = []

    def initialize(self):

        self.finalize()
        while not self._q_recv.empty():
            self._q_recv.get_nowait()
        self._srv = DataThread(
            addr_peer=(),
            q_recv=self._q_recv,
            addr_host=(self.addr_ini, self.port_ini)
        )
        self._srv.start()
        self.addr, self.port = self._srv.addr_host
        self._status = None

    def finalize(self):

        if self._srv is not None:
           if not self._srv.is_shutdown:
               self._srv.stop()
               self._srv.join(5.0)
        self._srv = None
        while len(self._clt) > 0:
            clt = self._clt.popitem()
            clt.stop()
            clt.join

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

    @property
    def q_recv(self):
        return self._q_recv

    @property
    def events(self):
        return self._events

    ## methods utility

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
            cont = [
                [self.status['sample_rate'], 0],
                [self.status['frame_size'], 1]
            ]
            if len(self.status['neurons']) > 0:
                cont.extend([[item, 10] for item in self.status['neurons']])
            if len(status['recorders']) > 0:
                cont.extend([[item, 20] for item in self.status['recorders']])
            return SimPkg(tid=SimPkg.T_STS, cont=cont.astype(long))
            # TODO long type ok?
        except:
            return None

    ## io methods

    def tick(self):
        """querys the send-queue and handles incoming packages"""

        # input packages
        while not self._q_recv.empty():

            # get package
            pkg, addr = self._q_recv.get_nowait()
            # propagate package
            self._events.append(pkg)

            # do we need to take actions ?
            if pkg.tid == SimPkg.T_CON:
                # new connection
                clt = ClientThread(addr_peer=addr, q_recv=self._q_recv)
                clt.start()
                clt.q_send(self.get_status_pkg())
                self._clt.append(clt)

            elif pkg.tid == SimPkg.T_END:
                # connection close
                clt = self._clt.pop(addr, None)
                if clt is not None:
                    if clt.is_alive():
                        clt.stop()
                        clt.join()

    def send_package(self, package, ident=None):
        """send package to interested clients

        :Parameters:
            pkg : SimPkg
                the SimPkg to send
            ident : long
                target ident or None if unrestricted
                Default=None
        """

        for clt in self._clt:

            if pkg.ident is None or pkg.ident == clt.ident:
                clt.q_send.put_nowait(pkg)

    def send_status(self):
        """send the status package"""

        self.send_package(self.get_status_pkg())


##---MAIN

if __name__ == '__main__':

    pass
