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
# sim - data_io/client_thread.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-06-21
#

"""socket select thread for data exchange"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
from Queue import Queue
from select import select
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR
from threading import Event, Thread
# own packages
from package import SimPkg


##---CLASSES

class DataThread(Thread):
    """UDP socket thread, communicating via recv and send Queue using SimPkg"""

    ## constructor

    def __init__(
        self,
        addr_host=None,
        addr_peer=None,
        q_recv=None,
        q_send=None,
        poll=0.001,
        maxlen=32768,
    ):
        """socket io thread for datagrams of the SimPkg type

        This class will start a new thread to handle communication with a remote
        location using SimPkg as the data format.

        :Parameters:
            addr_host : addr
                Host address and port tuple. If not supplied or None, will not
                bind at all.
                Default=None
            addr_peer: (host, port)
                peer address and port tuple.
                Default=None
            q_recv: Queue
                Queue for receiving packages.
                Default=None
            q_send : Queue
                Queue for sending packages, if not supplied a new Queue will be
                setup internally
            poll : float
                Polling timeout in seconds.
                Default=0.001
            maxlen : int
                maxlength of package buffer for recvfrom calls
                Default=32768
        """

        # thread init
        super(DataThread, self).__init__(name='NS_DATA_THREAD')
        self.daemon = True

        # members
        self.__online = False
        self.__is_shutdown = Event()
        self.__is_shutdown.set()
        self.__sock = None
        self.__poll = float(poll)
        self.__q_recv = q_recv or Queue()
        self.__q_send = q_send or Queue()
        self.__addr_host = addr_host
        self.__addr_peer = addr_peer
        self.__maxlen = int(maxlen)

    ## properties

    @property
    def is_shutdown(self):
        return self.__is_shutdown.is_set()

    @property
    def addr_host(self):
        return self.__addr_host

    @property
    def addr_peer(self):
        return self.__addr_peer

    @property
    def q_recv(self):
        return self.__q_recv

    @property
    def q_send(self):
        return self.__q_send

    ## internal socket interface

    def __sock_build(self):
        """builds the socket"""

        if self.__sock is not None:
            self.__sock_close()
        self.__sock = socket(AF_INET, SOCK_DGRAM)
        self.__sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        if self.__addr_host is None:
            self.__sock.sendto('\x00', ('localhost', 80))
        else:
            self.__sock.bind(self.__addr_host)
        self.__addr_host = self.__sock.getsockname()

    def __sock_close(self):
        """clean-up the socket"""

        self.__send(SimPkg(tid=SimPkg.T_END))
        self.__sock.close()
        self.__sock = None

    ## thread interface

    def run(self):
        """thread main"""

        # init
        self.__sock_build()
        self.__online = True
        self.__is_shutdown.clear()

        # doomsday loop
        try:
            while self.__online:
                # select
                read_rdy, _, _ = select([self.__sock], [], [], self.__poll)
                # receive
                if len(read_rdy) > 0:
                    data = self.__recv()
                    if data is not None:
                        self.__q_recv.put_nowait(data)
                # send
                while not self.__q_send.empty():
                    self.__send(self.__q_send.get_nowait())
        except Exception, ex:
            print ex
            self.__q_recv.put_nowait((ex, None))
        finally:
            self.__sock_close()
            self.__is_shutdown.set()

    def stop(self):
        """stop the thread"""

        self.__online = False
        self.__is_shutdown.wait()

    ## internal utility interface

    def __recv(self):
        """read package from the socket

        :Returns:
            SimPkg, host_addr : if received a valid SimPkg
            None : else
        """

        try:
            data, addr = self.__sock.recvfrom(self.__maxlen)
            pkg = SimPkg.from_data(data)
            if self.__addr_peer is not None:
                assert addr == self.__addr_peer, \
                    '%s == %s -> %s' % (addr, self.__addr_peer, addr == self.__addr_peer)
            return pkg, addr
        except Exception, ex:
            print ex
            rval = None

    def __send(self, pkg):
        """write package to the socket

        :Parameters:
            pkg : SimPkg
                The package to write.
        """

        try:
            if self.__addr_peer is not None:
                self.__sock.sendto(pkg(), self.__addr_peer)
        except Exception, ex:
            print ex


##---MAIN

if __name__ == '__main__':

    print
    print 'starting server..'
    dt = DataThread(addr_peer=('localhost', 31337))
    dt.start()
    select([], [], [], .2)
    print dt
    print 'serving at:', dt.addr_host
    print 'sending to:', dt.addr_peer

    con = False

    try:
        while True:
            if con is False:
                dt.q_send.put(SimPkg(tid=SimPkg.T_CON))
                con = True
#            else:
#                dt.q_send.put(SimPkg(tid=SimPkg.T_END))
            while not dt.q_recv.empty():
                pkg = dt.q_recv.get_nowait()
                print
                print 'received:'
                print pkg[0]
                print 'from', pkg[1]
            select([], [], [], 1)

    except KeyboardInterrupt:
        print
        print 'stoping due to KeyboardInterrupt'
        dt.stop()

    finally:
        print dt
