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
# sim - data_io/data_thread.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-06-21
#

"""socket select server for continuous connection"""
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
    """UDP socket thread, communicating via recv and send Queue"""

    ## constructor

    def __init__(
        self,
        poll=0.001,
        maxlen=32768,
        addr=None,
        is_server=False,
        q_recv=None,
        q_send=None,
    ):
        """socket io thread for datagrams of the SimPkg type

        This class will start a new thread to handle communication with a remote
        location. If the server parameter is set, this will be a listen only
        server slot. If the client parameter is set, this will be a connection
        dedicated to communicate to the gien client address. So give one or the
        other.

        :Parameters:
            poll : float
                Polling timeout in seconds.
                Default=0.001
            maxlen : int
                maxlength of package buffer for recvfrom calls
                Default=32768
            addr : (host, port)
                host address and port tuple, if not supplied a generic generic
                address will be chosen in server mode. Required for client mode.
                Default=None
            is_server : bool
                Flag deciding client (False) or server (True) operation mode.
                Default=False
            q_recv : Queue
                Queue for received packages, if not supplied a new Queue will be
                setup internally
            q_send : Queue
                Queue for sending packages, if not supplied a new Queue will be
                setup internally
        """

        # default queues if not supplied
        if q_recv is None:
            q_recv = Queue()
        if q_send is None and is_server is False:
            q_send = Queue()

        # thread init
        super(DataThread, self).__init__(name='NS_DATA_THREAD')
        self.daemon = True

        # members
        self.__online = False
        self.__is_shutdown = Event()
        self.__is_shutdown.set()
        self.__sock = None
        self.__poll = float(poll)
        self.__q_recv = q_recv
        self.__q_send = q_send
        self.__addr = addr
        self.__is_server = is_server
        self.__maxlen = int(maxlen)

    ## properties

    @property
    def is_shutdown(self):
        return self.__is_shutdown.is_set()

    @property
    def addr(self):
        return self.__addr

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
        if self.__is_server is True:
            self.__sock.bind(self.__addr)
            self.__addr = self.__sock.getsockname()

    def __sock_close(self):
        """clean-up the socket"""

        if self.__is_server is False:
            self.__send(SimPkg(tid=SimPkg.T_END))
        self.__sock.close()
        self.__sock = None

    ## data thread interface

    def fileno(self):
        """return socket file number for select and co"""

        return self.__sock.fileno()

    def run(self):
        """data thread main"""

        # set up
        self.__sock_build()
        self.__online = True
        self.__is_shutdown.clear()

        # doomsday loop
        try:
            while self.__online:

                read_rdy, _, _ = select([self.__sock], [], [], self.__poll)

                if len(read_rdy) > 0:
                    self.__q_recv.put_nowait(self.__recv())

                if self.__is_server is False:
                    while not self.__q_send.empty():
                        self.__send(self.__q_send.get_nowait())

        except Exception, ex:
            print ex

        finally:
            self.__sock_close()
            self.__is_shutdown.set()

    def stop(self):
        """stop the server thread"""

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
            if self.__is_server is False:
                assert addr == self.__addr
            pkg = pkg, addr
        except:
            pkg = None
        return pkg

    def __send(self, pkg):
        """write package to the socket if in client mode

        :Parameters:
            pkg : SimPkg
                The package to write.
        """

        try:
            if self.__is_server is False:
                self.__sock.sendto(pkg(), self.__addr)
        except Exception, ex:
            print ex

class DataClient(DataThread):
    """class that abstract a client connection"""

    def __init__(self, client_addr):
        pass
        q_writ




##---MAIN

if __name__ == '__main__':

    print
    print 'starting server..'
    dt = DataThread(addr=('', 31337), is_server=True)
    q_recv = dt.q_recv
    dt.start()
    select([], [], [], .2)
    print dt
    print 'serving at:', dt.addr
    print q_recv is dt.q_recv

    try:
        while True:
            while not q_recv.empty():
                pkg = q_recv.get_nowait()
                print
                print 'received:'
                print pkg[0]
                print 'from', pkg[1]
            else:
                select([], [], [], .1)

    except KeyboardInterrupt:
        print
        print 'stoping due to KeyboardInterrupt'
        dt.stop()

    finally:
        print dt
