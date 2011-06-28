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
# nsim - start_client.py
#
# Philipp Meier - <pmeier82 at gmail dot com>
# 2010-03-18
#
# $Id: start.py 4925 2010-07-29 19:45:54Z phil $
#

"""positioning of tetrodes"""
__docformat__ = 'restructuredtext'


##---IMPORTS

from PyQt4 import QtGui
from nsim.io import MinimalClient


##---CLASSES

class TestClient(MinimalClient):
    """test client"""

    def handle_data(self, signal, noise, gtrth):
        """abstract handler"""

        try:
            self.dataplot.set_data(signal)
        except Exception, ex:

            print
            print ex


##---MAIN

def main(ip_str='130.149.24.29'):

    app = QtGui.QApplication([])

    win = TestClient(addr=(ip_str, 31337))
    win.initialize()
    win.show()

    return app.exec_()


if __name__ == '__main__':

    import sys
    sys.exit(main())
