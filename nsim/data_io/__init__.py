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
# sim - data_io/__init__.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-04-21
#

"""data io classes for the simulation"""
__docformat__ = 'restructuredtext'


##---IMPORTS

from client import SimIOClientNotifier, SimIOConnection
from client_interface import ChunkContainer, NTrodeDataInterface
from minimal_client import MinimalClient
from package import SimPkg, recv_pkg, send_pkg
from server import SimIOManager, SimIOProtocol, SimIOServer


##---PACKAGE_ADMIN

__all__ = [
    # client
    'SimIOClientNotifier',
    'SimIOConnection',
    # client_interface
    'ChunkContainer',
    'NTrodeDataInterface',
    # minimal_client
    'MinimalClient',
    # server
    'SimIOManager',
    'SimIOProtocol',
    'SimIOServer',
    # package
    'SimPkg',
    'recv_pkg',
    'send_pkg',
]


##---MAIN

if __name__ == '__main__':
    pass
