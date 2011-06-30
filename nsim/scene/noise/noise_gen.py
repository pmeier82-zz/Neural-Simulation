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
# nsim - scene/noise/noise_gen.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-09-14
#

"""noise generation interfacce"""
__docformat__ = "restructuredtext"


##---IMPORTS

# packages
import scipy as N
from scipy import random as NR


##--ALL

__all__ = [
    'NoiseGen',
]


##---CLASSES

class NoiseGen(object):
    """generic noise generator

    This noise generator will yield multivariate noise samples from a Gaussian
    with a given mean and covariance matrix.
    """

    # constructor
    def __init__(self, mu=None, sigma=None):
        """
        :Parameters:
            mu : ndarray
                1d-array, the mean of the distribution.
                Default=None
            sigma : ndarray
                2d-array, square matrix with same dims as mu. The covariance
                matrix of the distribution.
                Default=None
        """

        if mu is None:
            if sigma is None:
                mu = N.zeros(1)
            else:
                mu = N.zeros(sigma.shape[0])
        if sigma is None:
            sigma = N.eye(mu.size)

        # parameter checks
        if mu.ndim != 1 or sigma.ndim != 2:
            ValueError('expect mu 1dim and sigma 2dim square')
        if mu.size != sigma.shape[0] != sigma.shape[1]:
            ValueError('mu does not match sigma shape')

        # memebers
        self.nvar = mu.size
        self.mu = mu
        self.sigma = sigma

    # methods public
    def query(self, size=1):
        """return noise samples

        :Parameters:
            size : int
                Number of samples to produce.
                Default=1
        """

        return NR.multivariate_normal(
            self.mu,
            self.sigma,
            size
        )


##---MAIN

if __name__ == '__main__':
    pass
