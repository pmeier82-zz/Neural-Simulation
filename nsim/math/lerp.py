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
# nsim - math/lerp.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-09-08
#

"""linear interpolation routines

Implemented for the  1d, 2d, and 3d case. all higher dimensional cases are
reduced to a concatenation of 1d linear interpolations."""
__docformat__ = 'restructuredtext'


##--FUNCTIONS

def lerp1(alpha, v0, v1):
    """linear interpolation - 1-dimensional case"""

    return ((1.0 - alpha) * v0) + (alpha * v1)

def lerp2(alpha_x, alpha_y,
          v00, v10,
          v01, v11):
    """linear interpolation - 2-dimensional case"""

    return lerp1(
        alpha_y,
        lerp1(alpha_x, v00, v10),
        lerp1(alpha_x, v01, v11)
    )

def lerp3(alpha_x, alpha_y, alpha_z,
          v000, v100, v010, v110,
          v001, v101, v011, v111):
    """linear interpolation - 3-dimensional case"""

    return lerp1(
        alpha_z,
        lerp1(
            alpha_y,
            lerp1(alpha_x, v000, v100),
            lerp1(alpha_x, v010, v110)
        ),
        lerp1(
            alpha_y,
            lerp1(alpha_x, v001, v101),
            lerp1(alpha_x, v011, v111)
        )
    )


##---MAIN

__all__ = ['lerp1', 'lerp2', 'lerp3']

if __name__ == '__main__':
    pass
