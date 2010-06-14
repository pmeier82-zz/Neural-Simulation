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
# sim - scene/data/lerp.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-06-08
#

"""interpolation routines"""
__docformat__ = 'restructuredtext'


##---IMPORTS

from scipy.interpolate import interp1d, interp2d
import scipy as N
from scipy.linalg import norm


##--FUNCTIONS

def LERP1(alpha, v0, v1):
    """linear interpolation"""

    return ((1 - alpha) * v0) + (alpha * v1)

def LERP2(x, y, v00, v10, v01, v11):
    """bilinear interpolation"""

    return LERP1(
        y,
        LERP1(x, v00, v10),
        LERP1(x, v01, v11)
    )

def LERP3(x, y, z, v000, v100, v010, v110, v001, v101, v011, v111):
    """trilinear interpolation"""

    return LERP1(
        z,
        LERP1(
            y,
            LERP1(x, v000, v100),
            LERP1(x, v010, v110)
        ),
        LERP1(
            y,
            LERP1(x, v001, v101),
            LERP1(x, v011, v111)
        )
    )


##---MAIN

if __name__ == '__main__':

   pass
