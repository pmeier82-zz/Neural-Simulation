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
# -*- coding: utf-8 -*-
#
# sim - data_io/server.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-04-21
#

"""socket select server for continuous connection"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
from Queue import Queue
from select import select
from socket import (
    socket, gethostname, gethostbyname, AF_INET, SOCK_STREAM, SOCK_DGRAM,
    SOL_SOCKET, SO_REUSEADDR
)
from struct import calcsize, pack, unpack
from threading import Event, Thread
# packages
import scipy as N
# own packages
from package import SimPkg


##---CONSTANTS

HOST = gethostbyname(gethostname())
PORT = 31337 # why not
POLL = 0.01
MAX_PKG_LEN = 32768


##---CLASSES

class SimServer(Thread):
    """UDP server socket managing clients"""

    ## class members

    addr_fam  = AF_INET
    sock_type = SOCK_DGRAM

    ## constructor

    def __init__(self, q_read, q_writ, port=PORT, poll=POLL):
        """
        :Parameters:
            q_read : Queue
                Threadsave Queue for reading (world->sim)
            q_writ : Queue
                Threadsave Queue for writing (sim->world)
            port : int
                addressPort of the server.
            poll : float
                Polling timeout in seconds.
        """

        # checks
        if not isinstance(q_read, Queue):
            raise ValueError('q_read is not of type(%s)!' % Queue.__class__.__name__)
        if not isinstance(q_writ, Queue):
            raise ValueError('q_writ is not of type(%s)!' % Queue.__class__.__name__)

        # super (for paralell base class)
        super(SimServer, self).__init__(name='NS_IOMANAGER')
        self.daemon = True

        # members
        self.__serving = False
        self.__is_shutdown = Event()
        self.__is_shutdown.set()
        self.sock = None
        self.clients = []
        self.poll = poll
        self.q_read = q_read
        self.q_writ = q_writ
        self.addr = (HOST, port or PORT)
        self.handshake = None

    ## properties

    @property
    def is_shutdown(self):
        return self.__is_shutdown.is_set()

    ## socket interface

    def sock_build(self):
        """builds the server socket"""

        if self.sock is not None:
            self.sock_close()
        self.sock = socket(self.addr_fam, self.sock_type)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.setblocking(0)
        self.sock.bind(self.addr)

    def sock_close(self):
        """clean-up the server socket"""

        while len(self.clients) > 0:
            try:
                self.writ_pkg(self.clients.pop(), SimPkg(tid=SimPkg.T_END))
            except:
                continue
        self.sock.close()
        self.sock = None

    def fileno(self):
        """return socket file number for select"""

        return self.sock.fileno()

    ## server interface

    def run(self):
        """start the server thread"""

        self.__is_shutdown.clear()
        self.__serving = True
        self.sock_build()

        # doomsday loop
        while self.__serving:

            # fd sets
            read_rdy, writ_rdy, erro_rdy = select([self], [], [self], self.poll)

            # handle outgoing packages
            while not self.q_writ.empty():
                try:
                    pkg = self.q_writ.get()
                    for addr in self.clients:
                        self.writ_pkg(addr, pkg)
                except Exception, ex:
                    print ex
                    continue

            # handle incomming packages
            if len(read_rdy) > 0:
                pkg = self.read_pkg()
                if pkg is not None:
                    self.q_read.put_nowait(pkg)

            # handle error sockets
            if len(erro_rdy) > 0:
                print '*' * 40
                print 'socket error! TERMINATION'
                print '*' * 40
                self.__serving = False

        # clean up
        self.sock_close()
        self.__is_shutdown.set()

    def stop(self):
        """stop the server thread"""

        self.__serving = False
        self.__is_shutdown.wait()

    ## utility interface

    def read_pkg(self):
        """read a pkg from a socket

        :Parameters:
            sock : socket
                The socket to read from.
            maxloops : int
                Maximum loop count to try the reading.
                Default=16
        :Returns:
            SimPkg : if received a valid SimPkg
            None : if no data available
        """

        try:

            data, addr = self.sock.recvfrom(MAX_PKG_LEN)
            pkg = SimPkg.from_data(data)

            # switch for package type
            if pkg.tid == SimPkg.T_CON:
                self.accept_client(addr)
                pkg.cont = addr
            elif pkg.tid == SimPkg.T_END:
                self.drop_client(addr)
                pkg.cont = addr
            rval = pkg

        except Exception, ex:

            print ex
            try:
                print data
                self.drop_client(addr)
            except:
                pass
            rval = None

        return rval

    def writ_pkg(self, addr, pkg):
        """write package to socket

        :Parameters:
            addr : tuple
                The socket addr to write to.
            pkg : SimPkg
                The package to write.
        """

        try:

            self.sock.sendto(pkg(), addr)
            print 'sent', pkg.tid, 'to', addr

        except Exception, ex:

            print ex
            self.drop_client(addr)

    def accept_client(self, addr):
        """accept a new client"""

        print 'con from', addr
        self.clients.append(addr)

        # handshaking
        if self.handshake is not None:
            self.writ_pkg(addr, self.handshake)

    def drop_client(self, addr):

        if addr in self.clients:
            print 'closing con', addr
            self.clients.remove(addr)

    ## special methods

    def __len__(self):
        return len(self.clients)


## main

if __name__ == '__main__':

    q_read = Queue()
    q_write = Queue()

    print
    print 'starting server..'
    s = SimServer(q_read, q_write)
    s.start()
    s.handshake = SimPkg(cont=N.ones(5))
    print s
    print 'serving at:', s.addr

    try:

        while True:

            while not s.q_read.empty():
                pkg = s.q_read.get(False)
                print
                print 'received:'
                print pkg
            else:
                select([], [], [], .01)

    except KeyboardInterrupt:

        print 'stoping due to KeyboardInterrupt'

    finally:

        s.stop()
        print s
        print
