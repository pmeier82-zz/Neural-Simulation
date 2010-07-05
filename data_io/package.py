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
# sim - data_io/package.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-04-21
#

"""package protocol for the simulation"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
from struct import calcsize, pack, unpack
# packages
import scipy as N


##---PACKAGE DISTRO

__all__ = ['SimPkg', 'SimPkgPing']


##---CLASSES

class ContentItem(object):
    """one item in a package"""

    ## class members

    HLEN = calcsize('!hhH4s') # dim[0], dim[1], nbytes, dtype

    ## constructor

    def __init__(self, cont):

        # check by type
        if isinstance(cont, ContentItem):
            self.cont = cont.cont
        elif isinstance(cont, N.ndarray):
            self.cont = cont
        else:
            self.cont = N.asarray(cont)

        # check cont for shape
        if len(self.cont.shape) > 2:
            raise ValuleError('shape shoud be <= 2')

    ## properties

    @property
    def dim(self):
        rval = [-1, -1]
        for i in xrange(len(self.cont.shape)):
            if i > 1:
                break
            rval[i] = self.cont.shape[i]
        return  rval

    @property
    def dtype(self):
        return self.cont.dtype

    @property
    def header(self):
        return pack(
            '!hhH4s',
            self.dim[0],
            self.dim[1],
            self.cont.nbytes,
            self.cont.dtype.str
        )

    @property
    def payload(self):
        return ''.join([self.header, self.cont.tostring()])
    __call__ = payload

    ## special methods

    def __len__(self):
        return self.HLEN + self.cont.nbytes

    def __str__(self):
        return 'ContentItem[%d,%d] %d bytes (%s)' % (self.dim[0], self.dim[1], self.cont.nbytes, self.dtype.str)


class SimPkg(object):
    """package protocoll base class"""

    ## class members

    HLEN = calcsize('!BQQB') # tid, ident, frame, nitems

    T_UKN = 0   # unknown
    T_CON = 1   # connection new
    T_END = 2   # connection end
    T_STS = 4   # status

    T_POS = 8   # position
    T_REC = 16  # recorder

    T_PING = 128    # ping
    T_PONG = 256    # pong

    SEND_ALWAYS = [0, 1, 2, 4]

    NOIDENT = 0L
    NOFRAME = 0L

    ## constructor

    def __init__(self, tid=None, ident=None, frame=None, cont=None):
        """
        :Parameters:
            tid : byte >= 0
                The type of content (see package type ids).
            ident : long >= 0 or None
                The object this package refers to (id of SimObject).
            frame : long >= 0 or None
                The frame this package refers to.
            cont : ndarray
                The content of the package as numpy compatible object.
        """



        # members
        self.tid = tid or self.T_UKN
        self.ident = ident or self.NOIDENT
        self.frame = frame or self.NOFRAME
        self.cont = []

        # contents
        if not isinstance(cont, list):
            cont = [cont]
        for item in cont:
            self.cont.append(ContentItem(item))

    ## properties

    @property
    def header(self):
        return pack('!BQQB', self.tid, self.ident, self.frame, self.nitems)

    @property
    def nitems(self):
        return len(self.cont)

    @property
    def payload(self):
        return ''.join([self.header] + [item.payload for item in self.cont])
    __call__ = payload

    ## special methods

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
            if not N.allclose(self.cont[i].cont, other.cont[i].cont):
                return False
        return True

    def __len__(self):
        return self.HLEN + sum([len(self.cont[i]) for i in xrange(self.nitems)])

    def __str__(self):
        rval = 'SimIOPackage (%d) - frame %d - from %d' % (
            self.tid, self.frame, self.ident
        )
        if self.nitems == 0:
            rval += '\nempty'
        else:
            for item in self.cont:
                rval += '\n%s' % item
        return rval

    ## from byte data factory

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
        tid, ident, frame, nitems= unpack('!BQQB', data[:idx])
        cont = []

        # content loop
        while idx < len(data):

            # read contents header
            dim0, dim1, nbytes, dtype_str = unpack('!hhH4s', data[idx:idx+ContentItem.HLEN])

            idx += ContentItem.HLEN

            # read content data
            cont_item = N.fromstring(
                data[idx:idx+nbytes],
                dtype=N.dtype(dtype_str)
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
        return SimPkg(tid, ident, frame, cont)

## special packages

class SimPkgPing(SimPkg):
    """ping package"""

    def __init__(self):

        super(SimPkgPing, self).__init__(tid=SimPkg.T_PING, cont=N.randn())


##---MAIN

if __name__ == '__main__':

    print
    print 'PACKAGE TEST - constructor'
    mypkg = SimPkg(SimPkg.T_UKN, 1337, 666, [N.randn(4,4), N.arange(10)])
    print mypkg
    print
    print 'PACKAGE TEST - from package'
    newpkg = SimPkg.from_data(mypkg.payload)
    print newpkg
    print
    print 'mypkg == newpkg :', mypkg == newpkg
    print
    print 'PACKAGE TEST DONE'
