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

"""io manager class using the blockstream protocoll"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
import logging
from Queue import Queue
# packages
import scipy as sp
# own packages
from nsim.events import *
from blockstream import *


##---MODULE_ADMIN

__all__ = [
    'IOManager',
]


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
            verbose : bool
                verboseness flag
        """

        # members
        self._recorder_map = {}
        self._w_bxpd = None
        self._q_w_bxpd = Queue()
        self._w_sort = None
        self._q_w_sort = Queue()
#        self._w_posi = None
#        self._q_w_posi = Queue()
#        self._r_posi = None
#        self._q_r_posi = Queue()
        self._is_initialised = False
        self._verbose = bool(kwargs.get('verbose', False))

    def initialize(self):

        self.finalise()
        self._w_bxpd = BS3Writer('BXPD', self._q_w_bxpd, verbose=self._verbose,
                                 ident='NS BXPD')
        self._w_bxpd.start()
#        self._w_posi = BS3Writer('POSI', self._q_w_posi, verbose=self._verbose,
#                                 ident='NS POSI')
#        self._w_posi.start()
        self._w_sort = BS3Writer('SORT', self._q_w_sort, verbose=self._verbose,
                                 ident='NS SORT')
        self._w_sort.start()
#        self._r_posi = BS3Reader(POSIProtocolHandler, self._q_r_posi,
#                                 verbose=self._verbose, ident='NS POSI')
#        self._r_posi.start()
        self._is_initialised = True

    def finalise(self):

        if self._w_bxpd is not None:
            self._w_bxpd.stop()
            self._w_bxpd = None
#        if self._w_posi is not None:
#            self._w_posi.stop()
#            self._w_posi = None
        if self._w_sort is not None:
            self._w_sort.stop()
            self._w_sort = None
#        if self._r_posi is not None:
#            self._r_posi.stop()
#            self._r_posi = None
        self._is_initialised = False

    ## properties

    def get_is_initialised(self):
        return self._is_initialised
    is_initialised = property(get_is_initialised)

    ## io methods

    def tick(self):
        """querys the POSI queue and returns all queued items"""

        rval = []
#        while not self._q_r_posi.empty():
#            item = self._q_recv.get()
#            rval.append(item)
#            self._q_recv.task_done()
        return rval

    def update_preambles(self, bxpd, sort):
        """set preambles for the writers
        
        :Parameters:
            bxpd : bxpd setup object
            sort : sort setup object
        """

        # BXPD
        self._q_w_bxpd.put(
            BS3BxpdSetupBlock(
                # header
                BS3BxpdBlockHeader(0),
                # sample rates
                [float(bxpd['sample_rate'] / 1000.0)],
                # analog channels
                bxpd['anchans'],
                # digital channels
                [],
                # event channels
                [],
                # groups
                bxpd['groups']
            )
        )

        # SORT
        self._q_w_sort.put(
            BS3SortSetupBlock(
                BS3SortBlockHeader(0),
                sort['groups']
            )
        )

    def send_frame(self, bxpd, sort):
        """send data for one frame

        :Parameters:
            bxpd : bxpd data object
            sort : data object
        """

        # BXPD
        self._q_w_bxpd.put(
            BS3BxpdDataBlock(
                BS3BxpdBlockHeader(1),
                bxpd['time_stamp'],
                bxpd['srate_offsets'],
                bxpd['anchans'],
                [],
                [])
        )

        # SORT
        self._q_w_sort.put(
            BS3SortDataBlock(
                BS3SortBlockHeader(1),
                sort['events']
            )
        )


##---MAIN

def main(nblocks=1000):

    from time import sleep

    print
    print 'setting up manager..'
    io_man = IOManager(verbose=True)
    io_man.initialize()

    bxpd = object()

    try:
        while True:
            events = io_man.tick()
            while len(events) > 0:
                print events.pop(0)
            else:
                print '.'
            sleep(5)
    except KeyboardInterrupt:
        print
        print 'stopping due to KeyboardInterrupt'
        io_man.finalise()


if __name__ == '__main__':

    main()
