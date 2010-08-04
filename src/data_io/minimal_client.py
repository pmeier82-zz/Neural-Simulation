# -*- coding: utf-8 -*-
#
# posi - minimal.py
#
# Philipp Meier - <pmeier82 at gmail dot com>
# 2010-03-18
#
# $Id: start.py 4707 2010-05-12 15:13:20Z ff $
#

"""positioning of tetrodes"""
__docformat__ = 'restructuredtext'


##---IMPORTS

from PyQt4 import QtCore, QtGui
from client_interface import DataContainer, NTrodeDataInterface, DEFAULT_VELOCITY
from gui import NTrodePlot, Ui_RecorderControll


##---CLASSES

class MinimalClient(QtGui.QDialog, Ui_RecorderControll):
    """control widget for a recorder (tetrode)"""

    ## constructor

    def __init__(
        self,
        parent=None,
        # io object parameters
        cnk_len=0.25,
        addr=('localhost', 31337),
        # gui parameters
        range=1.0,
        # keyword arguments
        ** kwargs
    ):
        """
        :Parameters:
            parent : QWidget
                The QT parent of the GUI elements.
            cnk_len : float
                The internal buffer size. Defines the amount/size of data that
                is buffered, analyzed and displayed to the screen in one cycle.
                Default=0.25
            addr : tuple
                A tuple of (host,port) defining where to reach the server.
                Default=('localhost',31337)
            range : float
                Amplitude range of the displayed data plot[-range,+range].
                Default=1.0
            kwargs : dict
                Additional keywords.
        """

        # GUI SETUP
        super(MinimalClient, self).__init__(parent)
        self.setupUi(self)

        self.dataplot = NTrodePlot(
            parent=self.content,
            nchan=4,
            range=range,
            replot=True
        )
        #self.lo_content.addWidget(self.dataplot)
        self.dataplot.show()
        # IO SETUP
        self.io_params = {
            'cnk_len'   : cnk_len,
            'addr'      : addr,
        }
        self._io = None

        # OTHER SETUP
        self._initialized = False

    ## gui methods

    def closeEvent(self, ev):
        """close event"""

        self.finalize()

    ## methods internal

    def initialize(self):
        """initialize the data handling stuff"""

        # check for status
        if self._initialized:
            self.finalize()

        # initialize members
        self._io = NTrodeDataInterface(**self.io_params)
        self._io.initialize()

        # connections
        self._io.sig_new_data.connect(self.on_new_data)
        self._io.sig_update_pos.connect(self.disp_meter.setValue)
        self._io.sig_update_pos.connect(self.disp_lcd.display)
        self.ctl_btn_move.clicked.connect(self.on_move)
        self.ctl_btn_request.clicked.connect(self._io.request_position)

        # initialize flags
        self._initialized = True

    def finalize(self):
        """clean up the positioning algo"""

        # shutdown members
        if self._io is not None:
            self._io.finalize()
            self._io.deleteLater()
            self._io = None

        # reset flags
        self._initialized = False

    ## slots

    @QtCore.pyqtSlot(DataContainer)
    def on_new_data(self, data):
        """slot to fetch newly available data"""

        noise = data.noise
        wvfrm = data.wform
        gtrth = data.gtrth
        signal = noise.copy()
        for i in xrange(len(wvfrm)):
            for j in xrange(len(gtrth[i])):
                signal[gtrth[i][j, 0]:gtrth[i][j, 1], :] += wvfrm[i][gtrth[i][j, 2]:gtrth[i][j, 3]]
        self.handle_data(signal, noise, wvfrm, gtrth)

    def handle_data(self, signal, noise, wvfrm, gtrth):
        """abstract handler"""

        pass

    @QtCore.pyqtSlot()
    def on_move(self):

        self._io.send_to_position(self.ctl_input_position.value(), DEFAULT_VELOCITY)


##--- MAIN

if __name__ == '__main__':
    pass



