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
# nsim - events.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-04-21
#

"""event protocol package"""
__docformat__ = 'restructuredtext'


##---IMPORTS



##---MODULE_ADMIN

__all__ = [
    # constants
    'T_UKN',
    'T_STS',
    'T_POS',
    'T_REC',
    'T_MAP',
    'NOIDENT',
    'NOFRAME',
]


##---EVENTS-TYPE-CODES

T_UKN = 0 # unknown
T_REC = 1 # recorder
T_GTR = 2 # ground truth
T_POS = 4 # positioning
T_STS = 8 # status
T_MAP = {
    0   : 'T_UKN',
    1   : 'T_REC',
    2   : 'T_GRT',
    4   : 'T_POS',
    8   : 'T_STS',
}
NOIDENT = 0L
NOFRAME = 0L


##---MAIN

if __name__ == '__main__':
    pass
