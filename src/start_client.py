# -*- coding: utf-8 -*-
#
# posi - minimal.py
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
from data_io import MinimalClient


##---CLASSES

class TestClient(MinimalClient):
    """test client"""

    def handle_data(self, signal, noise, wvfrm, gtrth):
        """abstract handler"""

        try:
            self.dataplot.set_data(signal)
        except Exception, ex:

            print
            print ex


##---MAIN

def main(ip_str='130.149.23.127'):

    app = QtGui.QApplication([])

    win = TestClient(addr=(ip_str, 31337))
    win.initialize()
    win.show()

    return app.exec_()


if __name__ == '__main__':

    import sys
    sys.exit(main())
