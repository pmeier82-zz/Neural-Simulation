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
# own packages
#from server_blkstr import BlkIOServer
from server_simpkg import SimIOServer
from simpkg import T_UKN, T_CON, T_END, T_STS, T_POS, T_REC, NOFRAME, NOIDENT


##---MODULE_ADMIN

__all__ = [
    # class
    'IOManager',
]


##---CONSTANTS

MAXQUEUESIZE = 1000


##---LOGGING

logging.basicConfig(level=logging.DEBUG)


##---CLASSES

class IOManager(object):
    """the singleton input/output manager thread

    This class handles all data input and output for a BaseSimulation object.
    Data is received from and sent to via Queue.Queue objects using one or more
    protocol defined in the server_*.py modules.
    """

    ## constructor

    def __init__(self, **kwargs):
        """
        :Keywords:
            srv_cls : IOServer class
                Default=SimIOServer
            srv_kwargs : dict
                keywords to pass to the server instance
        """

        # members
        self._status = None
        self._srv_cls = kwargs.get('srv_cls', SimIOServer)
        self._srv_kwargs = kwargs.get('srv_kwargs', {})
        self._q_recv = Queue(maxsize=MAXQUEUESIZE)
        self._q_send = Queue(maxsize=MAXQUEUESIZE)
        self._srv = None
        self._is_initialized = False

    def initialize(self):

        self.finalise()
        self._srv = self._srv_cls(
            self._q_recv,
            self._q_send,
            **self._srv_kwargs
        )
        self._srv.start()
        self._status = None
        self._is_initialized = True

    def finalise(self):

        if self._srv is not None:
            self._srv.stop()
            self._srv = None
        while not self._q_recv.empty():
            item = self._q_recv.get_nowait()
            del item
        while not self._q_send.empty():
            item = self._q_send.get_nowait()
            del item
        self._is_initialized = False

    ## properties

    def get_status(self):
        return self._status
    def set_status(self, value):
        if not isinstance(value, dict):
            return
        if self._status != value:
            self._status = value
            self.send_item(T_STS, NOIDENT, NOFRAME, self._status)
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

    def send_item(self,
        tid=T_UKN,
        ident=NOIDENT,
        frame=NOFRAME,
        cont=None
    ):
        """build a package from data and send to clients

        SimPkg constructor wrapper

        :Parameters:
            tid : int
                the type id
                Default=T_UKN
            ident : long
                target ident or None if unrestricted
                Default=NOIDENT
            frame : long
                target frame
                Default=NOFRAME
            cont : list
                the content of the package (ndarrays)
                Default=None
        """

        self.q_send.put((tid, ident, frame, cont))


##---MAIN

if __name__ == '__main__':

    from time import sleep

    print
    print 'setting up manager..'
    io_man = IOManager()
    io_man.initialize()

    try:
        while True:
            events = io_man.tick()
            while len(events) > 0:
                print events.pop(0)
            else:
                print '.'
            sleep(5)
            io_man.send_item(cont=sp.ones((4, 4)))
    except KeyboardInterrupt:
        print
        print 'stopping due to KeyboardInterrupt'
        io_man.finalise()
