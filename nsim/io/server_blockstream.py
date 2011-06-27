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
# nsim - io/server_blockstream.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-02-15
#

"""tcp point to point connection classes"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
import logging
from select import select
from threading import Event, Lock, Thread
from Queue import Queue
from SocketServer import BaseRequestHandler, TCPServer, ThreadingMixIn
# own imports
from package import SimPkg, recv_pkg, send_pkg


##---MODULE_ADMIN

__all__ = ['SimIOProtocol', 'SimIOServer']


##---CONSTANTS

MAXQUEUESIZE = 1000


##---LOGGING

logging.basicConfig(level=logging.DEBUG)


##---CLASSES

class SimIOProtocol(BaseRequestHandler):
    """the protocoll implementation

    inherited member variables:
    self.request : socket to work with
    self.client_address : (addr,port) of the client
    self.server : server reference
    """

    ## BaseRequestHandler interface

    def setup(self):
        """setup the connection"""

        self.sq_lock = self.server.send_queues_lock
        self.q_recv = self.server.q_recv
        with self.sq_lock:
            self.server.send_queues[self.client_address] = Queue(maxsize=MAXQUEUESIZE)
        self.q_send = self.server.send_queues[self.client_address]
        if self.server.status is not None:
            self.q_send.put(self.server.status)
        self.poll = self.server.client_poll

        logging.info('new connection from %s', str(self.client_address))

    def handle(self):
        """the run method"""

        while True:
            # select
            r, w, e = select([self.request], [], [self.request], self.poll)
            # error
            if len(e) > 0:
                break
            # receive
            if len(r) > 0:
                pkg = recv_pkg(self.request)
                if pkg is None:
                    break
                if pkg.tid in [SimPkg.T_CON, SimPkg.T_END]:
                    pkg.cont = self.client_address
                self.q_recv.put(pkg)
                if pkg.tid == SimPkg.T_END:
                    break
            # send
            with self.sq_lock:
                while not self.q_send.empty():
                    item = self.q_send.get()
                    send_pkg(self.request, item)
                    self.q_send.task_done()

    def finish(self):
        """finalize the connection"""

        logging.debug('closing for %s', str(self.client_address))
        with self.sq_lock:
            if self.client_address in self.server.send_queues:
                q = self.server.send_queues.pop(self.client_address)
                del q


class SimIOServer(ThreadingMixIn, TCPServer, Thread):
    """the server thread spawning one thread per connection"""

    ## class memebers

    allow_reuse_address = True
    request_queue_size = 5
    daemon_threads = True

    ## constructor

    def __init__(
        self,
        server_address,
        q_recv,
        q_send,
        client_poll=0.001
    ):

        # thread super
        Thread.__init__(self, name='SimIOServer')
        self.daemon = True

        # members
        self.q_recv = q_recv    # singleton receive queue
        self.q_send = q_send    # incomming send queue
        self.send_queues = {}
        self.send_queues_lock = Lock()
        self.client_poll = client_poll
        self._status = None
        self._serving = False
        self._is_shutdown = Event()
        self._is_shutdown.set()

        # TCPerver super
        TCPServer.__init__(self, server_address, SimIOProtocol, False)

    ## properties

    def get_status(self):
        return self._status
    def set_status(self, value):
        if not isinstance(value, SimPkg):
            return
        if value != self._status:
            self._status = value
            self.q_send.put(self._status)
    status = property(get_status, set_status)

    ## threading handlers with queue propagation

    def verify_request(self, request, client_address):
        """Verify the request.

        Return True if client_address is not served yet.
        [OVERWRITE]
        """

        if client_address in self.send_queues:
            return False
        else:
            return True

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

    def run(self):
        """Handle one request at a time until shutdown.

        Polls for shutdown every poll_interval seconds. Ignores
        self.timeout. If you need to do periodic tasks, do them in
        another thread.
        """

        self.server_bind()
        self.server_activate()
        self._serving = True
        self._is_shutdown.clear()
        while self._serving:
            r, w, e = select([self], [], [], 0.5)
            if r:
                self._handle_request_noblock()
            self.propagate_send_queue()
        self.server_close()
        self._is_shutdown.set()

    def stop(self):
        """stop the thread"""

        self._serving = False
        self._is_shutdown.wait()


##---MAIN

if __name__ == '__main__':

    pass
