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
# nsim - io/manager.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-02-15
#

"""io manager class, this class channels the output and input streams"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
import logging
from Queue import Queue
# packages
import scipy as sp
# own imports
from package import SimPkg
from tcp_server import SimIOServer


##---MODULE_ADMIN

__all__ = ['SimIOManager']


##---CONSTANTS

MAXQUEUESIZE = 1000


##---LOGGING

logging.basicConfig(level=logging.DEBUG)


##---CLASSES

class SimIOManager(object):
    """the singleton input/output manager thread

    This class handles all data input and output for a BaseSimulation object.
    Data is received from and sent to via Queue.Queue objects using the protocol
    defined in package.py.
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
        self.addr_ini = (kwargs.get('addr', '0.0.0.0'), kwargs.get('port', 31337))
        self.addr = 'not connected'
        self._q_recv = Queue(maxsize=MAXQUEUESIZE)
        self._q_send = Queue(maxsize=MAXQUEUESIZE)
        self._srv = None
        self._is_initialized = False

    def initialize(self):

        self.finalize()
        self._srv = SimIOServer(
            self.addr_ini,
            self._q_recv,
            self._q_send
        )
        self._srv.start()
        self.addr = self._srv.server_address
        self._status = None
        self._is_initialized = True

    def finalize(self):

        if self._srv is not None:
            self._srv.stop()
            self._srv = None
        while not self._q_recv.empty():
            self._q_recv.get_nowait()
        while not self._q_send.empty():
            self._q_send.get_nowait()
        self._is_initialized = False

    ## properties

    def get_status(self):
        return self._status
    def set_status(self, value):
        if not isinstance(value, dict):
            return
        if self._status != value:
            status_pkg = SimIOManager.build_status_pkg(value)
            if status_pkg is not None:
                self._status = status_pkg
                self._srv.status = status_pkg
            else:
                print 'problem with status value'
    status = property(get_status, set_status)

    def get_q_recv(self):
        return self._q_recv
    q_recv = property(get_q_recv)

    def get_q_send(self):
        return self._q_send
    q_send = property(get_q_send)

    def get_is_initialized(self):
        return self._is_initialized
    is_initialized = property(get_is_initialized)

    ## io methods

    def tick(self):
        """querys the receive-queue returns all queued items"""

        rval = []
        while not self._q_recv.empty():
            item = self._q_recv.get()
            rval.append(item)
            self._q_recv.task_done()
        return rval

    def send_package(
        self,
        tid=SimPkg.T_UKN,
        ident=SimPkg.NOIDENT,
        frame=SimPkg.NOFRAME,
        cont=None
    ):
        """build a package fromdata and send to clients

        SimPkg constructor wrapper

        :Parameters:
            pkg : SimPkg
                the SimPkg type id
                Default=T_UKN
            ident : long
                target ident or None if unrestricted
                Default=NOIDENT
            frame : long
                target frame
                Default=NOFRAME
            cont : list
                the conetnt of the package (ndarrays)
                Default=None
        """

        self.send_pkg(SimPkg(tid=tid, ident=ident, frame=frame, cont=cont))

    def send_pkg(self, pkg):
        """senda SimPkg to clients

        :Parameters:
            pkg : SimPkg
                The SimPkg instance to send.
        """

        self.q_send.put(pkg)

    ## static utility

    @staticmethod
    def build_status_pkg(status):
        """build a package from status

        items are mapped by id:
            0   : sample_rate
            1   : frame_size
            10  : neurons
            20  : recorders
        """

        try:
            cont = [
                [status['sample_rate'], 0],
                [status['frame_size'], 1]
            ]
            if len(status['neurons']) > 0:
                cont.extend([[item, 10] for item in status['neurons']])
            if len(status['recorders']) > 0:
                cont.extend([[item, 20] for item in status['recorders']])
            cont = sp.asarray(cont, dtype=sp.float32)
            return SimPkg(tid=SimPkg.T_STS, cont=cont)
        except:
            return None


##---MAIN

if __name__ == '__main__':

    from time import sleep

    print
    print 'setting up manager..'
    io_man = SimIOManager()
    io_man.initialize()

    try:
        while True:
            events = io_man.tick()
            while len(events) > 0:
                print events.pop(0)
            else:
                print '.'
            sleep(5)
            io_man.send_package(cont=sp.ones((4, 4)))
    except KeyboardInterrupt:
        print
        print 'stoping due to KeyboardInterrupt'
        io_man.finalize()
