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
from select import select
from struct import unpack
from threading import Event, Lock, Thread
from time import sleep
from Queue import Queue
from SocketServer import BaseRequestHandler, TCPServer, ThreadingMixIn
# packages
import scipy as N
# own imports
from package import SimPkg


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

        self.q_recv = self.server.q_recv
        self.q_send = self.server.send_queues[self.client_address]
        self.poll = self.server.client_poll
        self.buf = ''

    def handle(self):
        """the run method"""

        while True:
            # select
            r, w, e = select([self.request], [self.request], [self.request], self.poll)
            # receive
            if len(r) > 0:
                pkg = self.recv_pkg()
                if pgk is not None:
                    self.q_recv.put(pkg)
            # send
            if len(w) > 0:
                while not self.q_send.empty():
                    item = self.q_send.get()
                    self.request.sendall(item())
                    self.q_send.task_done()
            # error
            if len(e) > 0:
                break

    def finish(self):
        """finalize the connection"""
        pass

    ## interface

    def recv_pkg(self):
        """receive one package"""

        try:
            # get length
            pkg_data_len = SimPkg.len_from_bin(self.request.recv(2))
            # get data
            data = self.request.recv(pkg_data_len)
            return SimPkg.from_data(data)
        except:
            return None

class SimIOServer(TCPServer):
    """the server thread spawning one thread per connection"""

    ## constructor

    def __init__(
        self,
        server_address,
        q_recv,
        q_send,
        daemon_threads=True,
        client_poll=0.001
    ):

        # super
        TCPServer.__init__(self, server_address, SimIOProtocol)

        # members
        self.q_recv = q_recv    # singleton receive queue
        self.q_send = q_send    # incomming send queuq
        self.send_queues = {}
        self.send_queues_lock = Lock()
        self.client_poll = client_poll

    ## threading handlers with queue propagation

    def close_request(self, request):
        """Called to clean up an individual request."""

        client_address = request.getpeername()
        with self.send_queues_lock:
            if client_address in self.send_queues:
                self.send_queues.pop(client_address)

    def verify_request(self, request, client_address):
        """Verify the request.

        Return True if client_address is not served yet.
        """

        if client_address in self.send_queues:
            return False
        else:
            return True

    def process_request(self, request, client_address):
        """implement queue handling"""

        with self.send_queues_lock:
            self.send_queues[client_address] = Queue()

        TCPServer.process_request(self, request, client_address)

    def propagate_send_queue(self):
        """multiplex items in the send queue to the clients"""

        while not self.q_send.empty():
            item = self.q_send.get()
            with self.send_queues_lock:
                for q in self.send_queues.values():
                    q.put()
            self.q_send.task_done()

    def serve_forever(self, poll_interval=0.5):
        """Handle one request at a time until shutdown.

        Polls for shutdown every poll_interval seconds. Ignores
        self.timeout. If you need to do periodic tasks, do them in
        another thread.
        """

        self._BaseServer__serving = True
        self._BaseServer__is_shut_down.clear()
        while self._BaseServer__serving:
            r, w, e = select([self], [], [], poll_interval)
            if r:
                self._handle_request_noblock()
            self.propagate_send_queue()
        self._BaseServer__is_shut_down.set()


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
        self.port_ini = kwargs.get('port', 31337)
        self._q_recv = Queue()
        self._q_send = Queue()
        self._srv = None
        self._events = []

    def initialize(self):

        self.finalize()
        self._srv = SimIOServer(
            (self.addr_ini, self.port_ini),
            self._q_recv,
            self._q_send
        )
        t = Thread(target=self._srv.serve_forever, name='SimIOServer')
        t.daemon = True
        t.start()
        self._status = None

    def finalize(self):

        if self._srv is not None:
            self._srv.shutdown()
        self._srv = None
        while not self._q_recv.empty():
            self._q_recv.get_nowait()
        while not self._q_send.empty():
            self._q_send.get_nowait()

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
    def q_send(self):
        return self._q_send

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
            cont = N.asarray(cont, dtype=long)
            return SimPkg(tid=SimPkg.T_STS, cont=cont)
            # TODO long type ok?
        except:
            return None

    ## io methods

    def tick(self):
        """querys the send-queue and handles incoming packages"""

        while not self._q_recv.empty():
            pkg = self._q_recv.get()
            self._events.append(pkg)
            self._q_recv.task_done()

    def send_package(
        self,
        tid=SimPkg.T_UKN,
        ident=SimPkg.NOIDENT,
        frame=SimPkg.NOFRAME,
        cont=None
    ):
        """build a package fromdata and send to clients

        :Parameters:
            pkg : SimPkg
                the SimPkg to send
            ident : long
                target ident or None if unrestricted
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

    def send_status(self):
        """send the status package"""

        pkg = self.get_status_pkg()
        if pkg is not None:
            self.send_pkg(pkg)


##---MAIN

if __name__ == '__main__':

    from select import select

    print
    print 'setting up manager..'
    io_man = SimIOManager()
    io_man.initialize()

    try:
        while True:
            io_man.tick()
            print io_man.events
            sleep(.5)

    except KeyboardInterrupt:
        print
        print 'stoping due to KeyboardInterrupt'
        io_man.finalize()
