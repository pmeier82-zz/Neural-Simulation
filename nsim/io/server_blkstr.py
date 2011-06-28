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
# nsim - io/server_blkstr.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-02-15
#

"""io server using the blockstream protocol"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
import logging
from threading import Event, Lock, Thread
from Queue import Queue
# own imports
from simpkg import T_UKN, T_CON, T_END, T_STS, T_POS, T_REC, NOFRAME, NOIDENT
from blockstream import *

##---MODULE_ADMIN

__all__ = [
    'BlkIOProtocol',
    'BlkIOServer',
]


##---CONSTANTS

MAXQUEUESIZE = 1000


##---LOGGING

logging.basicConfig(level=logging.DEBUG)


##---CLASSES

class BlkIOServer(Thread):
    """the server thread spawning one thread per connection"""

    ## constructor

    def __init__(
        self,
        q_recv,
        q_send,
        client_poll=0.001
    ):

        # thread super
        Thread.__init__(self, name='BlkIOServer')
        self.daemon = True

        # members
        self.q_recv = q_recv    # queue for items received
        self.q_send = q_send    # queue for items to be send
        self.send_queues = {}
        self.send_queues_lock = Lock()
        self.client_poll = client_poll
        self._stastatusone
        self._serving = False
        self._is_shutdown = Event()
        self._is_shutdown.set()
        self._bxpd_q = Queue()
        self._bxpd_writer = None
        self._sort_q = Queue()
        self._sort_writer = None
        self._posi_q = Queue()
        self._posi_reader = None

    def propagate_send_queue(self):
        """multiplex items in the send queue to the clients"""

        while not self.q_send.empty():
            item = self.q_send.get()
            with self.send_queues_lock:
                for q in self.send_queues.values():
                    try:
                        q.put(item)
                    except:
                        logging.error('queue was not accessable')
            self.q_send.task_done()

    def start_blockstream(self):
        """start blockstream reader and writer"""

        # protocol_handler_cls, out_q, verbose=False, ident='?', timeout=1000
        self._posi_reader = BS3Reader(POSIProtocolHandler, self._posi_q,
                                      verbose=False, ident='NS POSI',
                                      timeout=1000)
        self._posi_reader.start()

        # protocol_handler_cls, in_q, verbose=False, ident='?', timeout = 1000
        self._bxpd_writer = BS3Writer('BXPD', self._bxpd_q, verbose=False,
                                      ident='NS BXPD', timeout=1000)
        self._bxpd_writer.start()
        self._sort_writer = BS3Writer('SORT', self._sort_q, verbose=False,
                                      ident='NS SORT', timeout=1000)
        self._sort_writer.start()

    def stop_blockstream(self):
        """stop blockstream reader and writer"""

        self._posi_reader.stop()
        self._bxpd_writer.stop()
        self._sort_writer.stop()

    def run(self):
        """Handle blockstream I/O for the Neural-Simulation.

        Polls for shutdown every poll_interval seconds. Ignores
        self.timeout. If you need to do periodic tasks, do them in
        another thread.
        """

        # setup library
        self.start_blockstream()

        # setup internals
        self._serving = True
        self._is_shutdown.clear()
        while self._serving:

            # items to be send
            while not self.q_send.empty():
                item = self.q_send.get()
                # (tid, ident, frame, cont)
                tid, ident, frame, cont = item
                if tid == T_REC:
                    # build bxpd
                    pass
                else:
                    pass

        # shutdown code
        self.stop_blockstream()
        self._is_shutdown.set()

    def stop(self):
        """stop the thread"""

        self._serving = False
        self._is_shutdown.wait()


##---MAIN

if __name__ == '__main__':
    pass
