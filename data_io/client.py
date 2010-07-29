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
# sim - data_io/client.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-07-19
#

"""client stub for the simulator protocoll"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from threading import Event, Thread
from time import sleep
from Queue import Queue
# own packages
from package import SimPkg, recv_pkg, send_pkg


##---MODULE_ADMIN

__all__ = ['SimIOClientNotifier', 'SimIOConnection']


##---CLASSES

class SimIOClientNotifier(object):
    """delegate class, subclass for specific GUI kit or other interface

    An instance of SimExternalDelegate should pass messages/events on to a
    suitable external interface, like a GUI kit (frex QT or GTK). As we must not
    make assumptions about the frontend, we provide this delegate class for the
    frontend to receive events.
    """

    def __init__(self, **kwargs):
        """
        :Parameters:
            kwargs : dict
                Keywords for subclasses
        """

        pass

    def notify(self):
        """to be implemented in a subclass"""

        pass


class SimIOConnection(Thread):
    """connection thread for the sim client stub"""

    def __init__(self, addr, q_recv=None, q_send=None, delegate=None, poll=0.001):
        """
        :Parameters:
            addr : tuple
                Socket connection address and port tuple.
            q_recv : Queue
                The queue for received items.
                Default=None
            q_send : Queue
                The queue for items to send.
                Defualt=None
            delegate : SimIOClientNotifier
                Object implementing the self.notify(SimPkg) method.
                Default=None
            poll : float
                select intervall
                Default=0.001
        """

        # super
        super(SimIOConnection, self).__init__(name='SimIOConnection')
        self.daemon = True

        # inits
        self.addr_ini = addr
        self.poll = float(poll)
        self.q_recv = q_recv or Queue()
        self.q_send = q_send or Queue()
        self.delegate = delegate
        self.status = None
        self._online = False
        self._is_shutdown = Event()
        self._is_shutdown.set()

    def run(self):
        """thread context"""

        # setup the socket
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect(self.addr_ini)
        self._online = True
        self._is_shutdown.clear()
        self.q_send.put(SimPkg(tid=SimPkg.T_CON))

        # doomsday loop
        while self._online:
            # select
            r, w, e = select([sock], [], [sock], self.poll)
            # error
            if len(e) > 0:
                break
            # receive
            if len(r) > 0:
                pkg = recv_pkg(sock)
                print pkg
                if pkg is None:
                    break
                if pkg.tid == SimPkg.T_STS:
                    self.status = pkg.cont[0].cont.copy()
                self.q_recv.put(pkg)
                if self.delegate is not None:
                    self.delegate.notify()
            # send
            while not self.q_send.empty():
                item = self.q_send.get()
                send_pkg(sock, item)
                self.q_send.task_done()

        self._is_shutdown.set()

    def stop(self):
        """stop the thread"""

        self.q_send.put(SimPkg(tid=SimPkg.T_END))
        self._online = False
        self._is_shutdown.wait()


##---MAIN

if __name__ == '__main__':

    from Queue import Empty
    from time import sleep

    print 'initialize'
    q_r, q_s = Queue(), Queue()
    client = SimIOConnection(('localhost', 31337), q_r, q_s)
    client.start()

    moved = False

    print 'started client, going to listen:'
    try:
        while True:
            try:
                while not q_r.empty():
                    pkg = q_r.get()
#                    print pkg
            except Empty:
                continue
            sleep(.5)
            if not client.is_alive():
                print 'client not alive :('
                break
            if client.status is not None and not moved:
                ident = client.status[client.status[:,1]==20,0]
                pos_pkg = SimPkg(tid=SimPkg.T_STS, ident=ident, cont=N.asarray([150, 9999]))
                q_s.put(pos_pkg)
                moved = True
    except KeyboardInterrupt:
        client.stop()
    print 'Done.'
