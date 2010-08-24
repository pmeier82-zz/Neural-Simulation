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
from nsim.gui import Ui_MultiElectrodeClient, NTrodePlot
import scipy as N


##---CLASSES

class MinimalClient(QtGui.QMainWindow, Ui_MultiElectrodeClient):
    """control widget for a recorder (tetrode)"""

    ## constructor

    def __init__(
        self,
        parent=None,
        # io object parameters
        cnklen=0.25,
        addr=('localhost', 31337),
        # ntrode plot parameters
        axis_range=1.0,
        do_plotting=True,
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
            do_plotting : bool
                if true, plot the raw signal, set this to false and call
                self.dataplot.set_data() in subclasses. 
                Default=True
            kwargs : dict
                Additional keywords.
        """

        # GUI SETUP
        super(MinimalClient, self).__init__(parent)
        self.setupUi(self)

        # remove the first toolbox widget
        wid = self.toolBox.widget(0)
        self.toolBox.removeItem(0)
        wid.deleteLater()

        # add ntrode plot widget
        self.dataplot = NTrodePlot(
            nchan=4,
            axis_range=axis_range,
            replot=True
        )
        self.toolBox.addItem(self.dataplot, 'MultiElectrode DataPlot')

        # IO SETUP
        self.io_params = {
            'cnklen'    : cnklen,
            'addr'      : addr,
        }
        self._io = None

        # OTHER SETUP
        self.chunk = None
        self._initialized = False
        self.do_plotting = do_plotting

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
        self._io.sig_update_pos.connect(self.on_pos)
        self.posi_btn_go.clicked.connect(self.on_move)
        self.posi_btn_request.clicked.connect(self.on_request)
        self.posi_slider_target.valueChanged.connect(self.on_target_slider)

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

    @QtCore.pyqtSlot(ChunkContainer)
    def on_new_data(self, chunk):
        """slot to fetch newly available chunk"""
        try:
            # save chunk
            self.chunk = chunk
            noise = chunk.noise
            # selection: noise
            if 0 not in self._io._config:
                signal = N.zeros_like(noise)
            else:
                signal = noise.copy()
            # selection waveforms
            if 1 in self._io._config:
                signal += chunk.waveform
            # selection: groundtruth
            gtrth = {}
            if 2 in self._io._config:
                for ident in chunk.units:
                    temp = []
                    for item in chunk.units[ident]['gt_buf']:
                        if item[3] == 0:
                            temp.append(item[1])
                    if len(temp) > 0:
                        gtrth[ident] = N.asarray(temp)
            # handle chunk
            self.handle_data(signal, noise, gtrth)
            # update dataplot
            if self.do_plotting:
                self.dataplot.set_data(signal)
        except Exception, ex:
            print str(ex)

    def handle_data(self, signal, noise, gtrth):
        pass

    @QtCore.pyqtSlot(int)
    @QtCore.pyqtSlot(float)
    def on_pos(self, pos):
        pos = int(pos)
        self.posi_slider_position.setValue(pos)
        self.posi_edit_position.setText(str(pos))

    @QtCore.pyqtSlot()
    def on_move(self):
        pos = float(self.posi_edit_target.text())
        self.posi_slider_target.setValue(int(pos))
        self._io.send_to_position(pos)

    @QtCore.pyqtSlot()
    def on_request(self):
        self._io.request_position()

    @QtCore.pyqtSlot(int)
    @QtCore.pyqtSlot(float)
    def on_target_slider(self, pos):
        self.posi_edit_target.setText(str(pos))



##--- MAIN

if __name__ == '__main__':
    pass
