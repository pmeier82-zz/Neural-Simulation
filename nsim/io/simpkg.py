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
# nsim - io/simpkg.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-04-21
#

"""frame package protocol"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
from struct import calcsize, pack, unpack
# packages
import scipy as sp


##---MODULE_ADMIN

__all__ = [
    # classes
    'ContentItem',
    'SimPkg',
    # functions
    'recv_pkg',
    'send_pkg',
    'receive_n_bytes',
    # constants
    'T_UKN',
    'T_CON',
    'T_END',
    'T_STS',
    'T_POS',
    'T_REC',
    'T_XXX',
    'T_MAP',
    'NOIDENT',
    'NOFRAME',
]


##---CONSTANTS

T_UKN = 0   # unknown
T_CON = 1   # connection new
T_END = 2   # connection end
T_STS = 4   # status
T_POS = 8   # position
T_REC = 16  # recorder
T_XXX = 32  # stopper item for th queue
T_MAP = {
    0   : 'T_UKN',
    1   : 'T_CON',
    2   : 'T_END',
    4   : 'T_STS',
    8   : 'T_POS',
    16  : 'T_REC',
}
NOIDENT = 0L
NOFRAME = 0L


##---CLASSES

class ContentItem(object):
    """one item in a package"""

    ## class members

    HDEF = '!hhI4s' # dim[0], dim[1], nbytes, dtype
    HLEN = calcsize(HDEF)

    ## constructor

    def __init__(self, cont):

        # check by type
        self.cont = None
        if isinstance(cont, ContentItem):
            self.cont = cont.cont
        elif isinstance(cont, sp.ndarray):
            self.cont = cont
        elif cont is None:
            self.cont = sp.array([])
        else:
            self.cont = sp.asarray(cont)

        # check cont for shape
        if len(self.cont.shape) > 2:
            raise ValueError('shape should be <= 2')

    ## properties

    def get_dim(self):
        rval = [-1, -1]
        for i in xrange(len(self.cont.shape)):
            if i > 1:
                break
            rval[i] = self.cont.shape[i]
        return rval
    dim = property(get_dim)

    def get_dtype(self):
        return self.cont.dtype
    dtype = property(get_dtype)

    def get_header(self):
        return pack(
            self.HDEF,
            self.dim[0],
            self.dim[1],
            self.cont.nbytes,
            self.cont.dtype.str
        )
    header = property(get_header)

    def get_payload(self):
        return ''.join([self.header, self.cont.tostring()])
    payload = property(get_payload)

    ## special methods

    def __call__(self):
        return self.payload

    def __len__(self):
        return self.HLEN + self.cont.nbytes

    def __str__(self):
        return 'ContentItem[%d,%d] %d bytes (%s)' % (self.dim[0], self.dim[1], self.cont.nbytes, self.dtype.str)


class SimPkg(object):
    """package protocoll base class"""

    ## class members

    HDEF = '!BQQB' # tid, ident, frame, nitems
    HLEN = calcsize(HDEF)

    ## constructor

    def __init__(self, tid=None, ident=None, frame=None, cont=()):
        """
        :Parameters:
            tid : byte >= 0
                The type of content (see package type ids).
            ident : long >= 0 or None
                The object this package refers to (id of SimObject).
            frame : long >= 0 or None
                The frame this package refers to.
            args : tuple
                The content of the package as numpy compatible objects.
        """



        # members
        self.tid = tid or T_UKN
        self.ident = ident or NOIDENT
        self.frame = frame or NOFRAME
        self.cont = []

        # contents
        if not isinstance(cont, tuple):
            cont = (cont,)
        for item in cont:
            self.cont.append(ContentItem(item))

    ## properties

    @property
    def header(self):
        return pack(self.HDEF, self.tid, self.ident, self.frame, self.nitems)

    @property
    def nitems(self):
        return len(self.cont)

    @property
    def payload(self):
        return ''.join([self.header] + [item.payload for item in self.cont])

    @property
    def packed_size(self):
        return pack('!I', len(self))

    ## special methods

    def __call__(self):
        return self.payload

    def __eq__(self, other):
        if not isinstance(other, SimPkg):
            return False
        if self.tid != other.tid:
            return False
        if self.ident != other.ident:
            return False
        if self.frame != other.frame:
            return False
        if len(self.cont) != len(other.cont):
            return False
        for i in xrange(len(self.cont)):
            if not sp.allclose(self.cont[i].cont, other.cont[i].cont):
                return False
        return True

    def __len__(self):
        return self.HLEN + sum([len(self.cont[i]) for i in xrange(self.nitems)])

    def __str__(self):
        rval = 'SimIOPackage(%s) #[%d] - frame %d - from %d' % (
            T_MAP[self.tid], self.nitems, self.frame, self.ident
        )
        if self.nitems == 0:
            rval += '\nempty'
        else:
            for item in self.cont:
                rval += '\n%s' % item
        return rval

    @staticmethod
    def len_from_bin(data):
        """decode package length from unsigned short in network-byteorder"""

        return unpack('!I', data)[0]

    @staticmethod
    def from_data(data):
        """produce a SimPkg from bytedata

        :Parameters:
            data : str
                The data to produce the package from.
        """

        # length check
        if len(data) < SimPkg.HLEN:
            raise ValueError('length < SimPkg.HLEN')

        # read header
        idx = SimPkg.HLEN
        tid, ident, frame, nitems = unpack(SimPkg.HDEF, data[:idx])
        cont = []

        # content loop
        while idx < len(data):

            # read contents header
            dim0, dim1, nbytes, dtype_str = unpack(ContentItem.HDEF, data[idx:idx + ContentItem.HLEN])

            idx += ContentItem.HLEN

            # read content data
            cont_item = sp.fromstring(
                data[idx:idx + nbytes],
                dtype=sp.dtype(dtype_str)
            )
            if dim0 >= 0:
                if dim1 >= 0:
                    dim = [dim0, dim1]
                else:
                    dim = [dim0]
                cont_item.shape = dim

            cont.append(cont_item)
            idx += nbytes

        # return
        assert len(cont) == nitems, 'cont list length (%s) does not match nitems (%s)!' % (len(cont), nitems)
        return SimPkg(tid, ident, frame, tuple(cont))


##---FUNCTIONS

def receive_n_bytes(sock, nbytes):
    """receive until nbytes have been received"""

    received = 0
    buf = ''
    while received != nbytes:
        temp = sock.recv(nbytes - received)
        if not temp:
            raise IOError('remote connection closed')
        buf += temp
        received = len(buf)
    return buf

def recv_pkg(sock, recv_chunk_size=4096):
    """receive one SimPkg"""

    try:
        # get size
        len_recv, data = 0, []
        data_size = sock.recv(4)
        len_data = SimPkg.len_from_bin(data_size)
        # get data
        while len_recv < len_data:
            cnk_len = recv_chunk_size
            if len_data - len_recv < cnk_len:
                cnk_len = len_data - len_recv
            temp = sock.recv(cnk_len)
            data.append(temp)
            len_recv += len(temp)
        return SimPkg.from_data(''.join(data))
    except Exception, ex:
        print ex
        print len(data_size), data_size
        return None

def send_pkg(sock, pkg):
    """send one SimPkg"""

    sock.sendall(pkg.packed_size)
    sock.sendall(pkg())


##---MAIN

if __name__ == '__main__':

    print
    print 'PACKAGE TEST - constructor with randn(4,4) and arange(10)'
    mypkg = SimPkg(T_UKN, 1337, 666, (sp.randn(4, 4), sp.arange(10)))
    print mypkg
    print
    print 'PACKAGE TEST - from package'
    newpkg = SimPkg.from_data(mypkg.payload)
    print newpkg
    print
    print 'mypkg == newpkg :', mypkg == newpkg
    print
    print ' --- %s \n --- \n equals \n --- %s \n --- \n %s' % (mypkg(), newpkg(), mypkg() == newpkg())
    print
    print 'unpack(\'!I\', newpkg.packed_size)[0] == len(newpkg) :', unpack('!I', newpkg.packed_size)[0] == len(newpkg)
    print
    print 'PACKAGE TEST DONE'
