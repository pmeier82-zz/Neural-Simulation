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
from client_interface import ChunkContainer, NTrodeDataInterface, DEFAULT_VELOCITY
from nsim.gui import NTrodePlot, Ui_RecorderControll


##---CLASSES

class MinimalClient(QtGui.QDialog, Ui_RecorderControll):
    """control widget for a recorder (tetrode)"""

    ## constructor

    def __init__(
        self,
        parent=None,
        # io object parameters
        cnklen=0.25,
        addr=('localhost', 31337),
        # gui parameters
        axis_range=1.0,
        # keyword arguments
        ** kwargs
    ):
        """
        :Parameters:
            parent : QWidget
                The QT parent of the GUI elements.
            cnklen : float
                The internal buffer size. Defines the amount/size of data that
                is buffered, analyzed and displayed to the screen in one cycle.
                Default=0.25
            addr : tuple
                A tuple of (host,port) defining where to reach the server.
                Default=('localhost',31337)
            axis_range : float
                Amplitude axis_range of the displayed data plot[-axis_range,+axis_range].
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
            axis_range=axis_range,
            replot=True
        )
        # IO SETUP
        self.io_params = {
            'cnklen'    : cnklen,
            'addr'      : addr,
        }
        self._io = None

        # OTHER SETUP
        self.chunk = None
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
        self.dataplot.show()

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
        self.dataplot.close()
        self.dataplot.deleteLater()
        self.dataplot = None

        # reset flags
        self._initialized = False

    ## slots

    @QtCore.pyqtSlot(ChunkContainer)
    def on_new_data(self, data):
        """slot to fetch newly available data"""
        try:
            # save chunk
            self.chunk = data
            noise = data.noise
            signal = noise.copy()
            # selection: noise
            if 0 not in self._io._config:
                signal[:] = 0.0
            gtrth = {}
            for ident in data.units:
                for item in data.units[ident]['gt_buf']:
                    # selection: waveforms 
                    if 1 in self._io._config:
                        signal[item[1]:item[2], :] += data.units[ident]['wf_buf'][item[0]][item[3]:item[4], :]
                    # selection: groundtruth
                    if 2 in self._io._config:
                        if ident not in gtrth:
                            gtrth[ident] = []
                        gtrth[ident].append(item[0] + int((item[1] - item[0]) / 2))
            self.handle_data(signal, noise, gtrth)
        except:
            print 'error'

    def handle_data(self, signal, noise, gtrth):
        """abstract handler"""

        pass

    @QtCore.pyqtSlot()
    def on_move(self):

        self._io.send_to_position(float(self.ctl_input_position.value()), DEFAULT_VELOCITY)


##--- MAIN

if __name__ == '__main__':
    pass



