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
# nsim - scene/neuron_data/ndata_kernel.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-09-13
#

"""NeuronData implementation based on kernel function"""
__docformat__ = 'restructuredtext'


##---IMPORTS

import scipy as N
from neuron_data import NeuronData
from scene.math3d import vector_norm


##---CLASSES

class Kernel(object):
    """kernel object"""

    ## constructor

    def __init__(self, kernel):
        """
        :Parameters:
            kernel_str : str
                A string that can be evaluated using python eval(). In its
                context the local variables 'pos' (the 3d relative position as
                ndarray) is available. Numpy is available as 'N'.
        """

        # members
        self.kernel_str = kernel

        # check kernel
        self(N.arange(3))

    ## __call__ 

    def __call__(self, pos):
        """evaluate the kernel
        
        :Parameters:
            pos : ndarray
                The 3d relative position.
        """

        return eval(self.kernel)


class KernelND(NeuronData):
    """docstring"""

    ## constructor

    def __init__(self, kernel=[], **kwargs):
        """
        :Parameters:
            kernel : NDKernel or list of NDKernel
                The kernel to generate data with this NeuronData object.
        :Keywords:
            see NeuronData
        :Exceptions:
            see NeuronData
        """

        # super
        super(KernelND, self).__init__(**kwargs)

        # members
        self.kernel_list = None


##---MAIN

if __name__ == '__main__':

    K = Kernel('1.0 / (4 * N.pi * vector_norm(pos)**2)')
    rval = K(N.arange(3))
    print 'calculated:', rval
    print 'expected:   0.0159154943092'
    print N.allclose(rval, 0.0159154943092)
