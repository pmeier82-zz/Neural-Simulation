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
# -*- coding: utf-8 -*-
#
# sim - data_io/package.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-04-21
#

"""package definition for the simulation"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# builtins
from struct import calcsize, pack, unpack
# packages
import scipy as N


##--DIST

__all__ = ['SimPkg']


##---CLASSES

class SimPkg(object):
    """package protocoll for stream-based io"""

    ## class members

    HLEN = calcsize('!BQQH4shh')

    T_UKN = 0   # unknown package
    T_STS = 1   # status package
    T_POS = 2   # position package
    T_WFN = 4   # waveform noise
    T_WFU = 8   # waveform single unit
    T_GTR = 16  # multiunit groundtruth
    T_CON = 32  # connection attempt
    T_END = 64  # connection closure

    T_FRM = 255 # TODO: cleanup this status

    ## constructor

    def __init__(self, tid=T_UKN, ident=0L, frame=0L, cont=N.uint8(0)):
        """
        :Parameters:
            tid : byte >= 0
                The type of content (see package type ids).
            ident : long >= 0
                The object this package refers to (id of SimObject).
            frame : long >= 0
                The frame this package refers to.
            cont : ndarray
                The content of the package as numpy compatible object.
        """

        # members
        self.tid = tid
        self.ident = ident
        self.frame = frame
        self.cont = N.asarray(cont)

    ## methods

    def payload(self):
        """marshalling for bytestreams"""

        # shape
        shape = [-1, -1]
        for i in xrange(len(self.cont.shape)):
            shape[i] = self.cont.shape[i]

        # header
        return pack(
            '!BQQH4shh',
            self.tid,
            self.ident,
            self.frame,
            self.cont.nbytes,
            self.cont.dtype.str[:4],
            shape[0],
            shape[1]
        ) + self.cont.tostring()
    __call__ = payload

    ## special methods

    def __len__(self):
        return self.HLEN + self.cont.nbytes

    def __str__(self):
        return 'SimIOPackage (%d) - frame %d - from %d\n%s' % (
            self.tid, self.frame, self.ident, self.cont
        )

    def __eq__(self, other):

        if not isinstance(other, SimPkg):
            return False
        if self.tid != other.tid:
            return False
        if self.ident != other.ident:
            return False
        if self.frame != other.frame:
            return False
        if not N.allclose(self.cont, other.cont):
            return False
        return True

    ## static factory

    @staticmethod
    def from_data(data):
        """produce a SimPkg from bytedata

        :Parameters:
            data : str
                The data to produce the package from (w/o initial length
                prefix!!).
        """

        # length
        if len(data) < SimPkg.HLEN:
            raise ValueError('length < SimPkg.HLEN')#return False

        # read header
        tid, ident, frame, nbytes, dtype, dim0, dim1 = unpack(
            '!BQQH4shh',
            data[:SimPkg.HLEN]
        )

        # read content
        if len(data) != SimPkg.HLEN + nbytes:
            raise ValueError('length != SimPkg.HLEN + nbytes')#return False
        cont = N.fromstring(
            data[SimPkg.HLEN:SimPkg.HLEN+nbytes],
            dtype=N.dtype(dtype)
        )
        dim = []
        if dim0 >= 0:
            dim.append(dim0)
            if dim1 >= 0:
                dim.append(dim1)
            cont.shape = dim

        # return
        return SimPkg(tid, ident, frame, cont)


##---MAIN

if __name__ == '__main__':

    print
    print 'PACKAGE TEST - constructor'
    mypkg = SimPkg(SimPkg.T_UKN, 1337, 666, N.randn(4,4))
    print mypkg
    print
    print 'PACKAGE TEST - from package'
    newpkg = SimPkg.from_data(mypkg.payload())
    print newpkg
    print
    print 'mypkg == newpkg :', mypkg == newpkg
    print
    print 'PACKAGE TEST DONE'
