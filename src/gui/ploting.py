# -*- coding: utf-8 -*-
#
# posi - ntrode_plot.py
#
# Philipp Meier - <pmeier82 at gmail dot com>
# 2010-03-16

"""ploting facilities for the neural simulation client"""
__docformat__ = 'restructuredtext'


##---IMPORTS

# packages
from PyQt4 import QtCore, QtGui, Qwt5
import scipy as N


##---CONSTANTS

# TimeSeriesPlot constants
BACKGROUND = QtCore.Qt.black
CURVECOLOR = QtCore.Qt.green
ORIGINCOLOR = QtCore.Qt.darkYellow
EVENTCOLOR = QtCore.Qt.red
GTRUTHCOLOR = QtCore.Qt.blue


##---CLASSES

class MatrixData(Qwt5.QwtRasterData):
    """QWT RasterData implementation for matrix (2d) colormaps"""

    ## constructor

    def __init__(self):

        # super
        super(MatrixData, self).__init__()

        # members
        self.data = None

    ## implementations

    def copy(self):
        return self

    def range(self):
        try:
            return Qwt5.QwtDoubleInterval(self.data.min(), self.data.max())
        except:
            return Qwt5.QwtDoubleInterval(0.0, 1.0)

    def value(self, x, y):
        try:
            return self.data[x, self.data.shape[0] - y]
        except:
            return 0.0

    ## set data method

    @QtCore.pyqtSlot(N.ndarray)
    def set_data(self, data):
        try:
            if self.data is None or self.data.shape != data.shape:
                self.setBoundingRect(
                    QtCore.QRectF(
                        0.0,
                        0.0,
                        data.shape[0],
                        data.shape[1]
                    )
                )
            self.data = data
        except:
            self.data = None


class MatShow(Qwt5.QwtPlot):
    """Plot showing a matrix as colormap"""

    ## constructor

    def __init__(self, parent=None):
        """
        :Parameters:
            parent : QObject
                QT parent.
        """

        # super
        super(MatShow, self).__init__(parent)

        # layout
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(True)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setLineWidth(0)
        self.setCanvasLineWidth(0)
        self.setAutoReplot(True)
#        self.setSizePolicy(SIZE_POL)

        # matplot
        colmap = Qwt5.QwtLinearColorMap()
        self._mat = Qwt5.QwtPlotSpectrogram()
        self._mat.setColorMap(colmap)
        self._mat.attach(self)

        # matrix data
        self._data = MatrixData()
        self._mat.setData(self._data)

        # axis and scales
        self.axisWidget(Qwt5.QwtPlot.yRight).setColorBarEnabled(True)
        self.axisWidget(Qwt5.QwtPlot.yRight).setColorMap(
            self._data.range(),
            self._mat.colorMap()
        )
        self.enableAxis(Qwt5.QwtPlot.yRight, True)
        self.enableAxis(Qwt5.QwtPlot.yLeft, False)
        self.enableAxis(Qwt5.QwtPlot.xTop, False)
        self.enableAxis(Qwt5.QwtPlot.xBottom, False)

    ## set data method

    @QtCore.pyqtSlot(N.ndarray)
    def set_data(self, data):
        """update the plot with new data

        :Parameters:
            data : ndarray
                A 2d array with data to show.
        """

        # set data
        self._data.set_data(data)

        # recalculate colorbar axis
        self.axisWidget(Qwt5.QwtPlot.yRight).setColorMap(
            self._data.range(),
            self._mat.colorMap()
        )
        self.setAxisScale(
            Qwt5.QwtPlot.yRight,
            data.min(),
            data.max()
        )


class TimeSeriesPlot(Qwt5.QwtPlot):
    """a plot for a single channel time series data with event markers"""

    ## constructor

    def __init__(self, parent=None, range=2.0, replot=False):
        """
        :Parameters:
            parent : QObject
                Qt parent.
                Default=None
            range : float
                Axis range. Axis will have range [-range,range].
            replot : bool
                If True, replot after set_data() was called, else do not replot.
        """

        # super
        super(TimeSeriesPlot, self).__init__(parent)

        # members
        self.range = range
        self.replot_on_update = replot

        # layout
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(True)
        self.setAxisScale(Qwt5.QwtPlot.yLeft, -float(self.range), float(self.range))
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setCanvasBackground(BACKGROUND)

        # data curve
        self._data = d = Qwt5.QwtPlotCurve('data')
        d.setPen(QtGui.QPen(CURVECOLOR))
        d.attach(self)

        # events curve
        self._events = e = Qwt5.QwtPlotCurve('events')
        e.setStyle(Qwt5.QwtPlotCurve.NoCurve)
        e.setSymbol(
            Qwt5.QwtSymbol(
                Qwt5.QwtSymbol.DTriangle,
                QtGui.QBrush(EVENTCOLOR),
                EVENTCOLOR,
                QtCore.QSize(15, 15)
            )
        )
        e.attach(self)

        # gtruth curve
        self._gtruth = g = Qwt5.QwtPlotCurve('groundtruth')
        g.setStyle(Qwt5.QwtPlotCurve.NoCurve)
        g.setSymbol(
            Qwt5.QwtSymbol(
                Qwt5.QwtSymbol.UTriangle,
                QtGui.QBrush(GTRUTHCOLOR),
                GTRUTHCOLOR,
                QtCore.QSize(15, 15)
            )
        )
        g.attach(self)

        # zeroline marker
        self._zeroline = z = Qwt5.QwtPlotMarker()
        z.setLinePen(QtGui.QPen(ORIGINCOLOR))
        z.setLineStyle(Qwt5.QwtPlotMarker.HLine)
        z.attach(self)

    ## slots
    @QtCore.pyqtSlot(N.ndarray, N.ndarray)
    def set_data(self, data, events=None, gtruth=None):
        """update the plot with new chunk of data

        :Parameters:
            data : ndarray
                A 1d array with data to show.
            events : ndarray
                A 1d array of event times to show.
        """

        # data
        self._data.setData(N.arange(data.size), data)

        # events
        if events is None:
            ev = N.zeros(0)
        else:
            ev = N.asarray(events)
        self._events.setData(ev, N.ones(ev.size) * self.range)

        # gtruth
        if gtruth is None:
            gt = N.zeros(0)
        else:
            gt = N.asarray(list(gtruth))
        self._gtruth.setData(gt, N.ones(gt.size) * -self.range)

        # replot
        if self.replot_on_update is True:
            self.replot()


class NTrodePlot(QtGui.QWidget):
    """a plot for (multichanneled) timeseries data"""

    ## constructor
    def __init__(self, parent=None, nchan=4, range=2.0, replot=False):
        """
        :Parameters:
            parent : QObject
                Qt parent
                Default = None
        """

        # super
        parent = None
        super(NTrodePlot, self).__init__(parent)
        self.resize(300, 100)
        self.replot_on_update = replot

        # internal members
        self.nchan = nchan
        self.range = range
        self._err = QtGui.QErrorMessage.qtHandler()

        # gui members
        self.area_btn = QtGui.QWidget(self)
        self.area_plt = QtGui.QWidget(self)

        # layouts
        self.lo = QtGui.QVBoxLayout(self)
        self.lo.addWidget(self.area_btn)
        self.lo.addWidget(self.area_plt)
        self.lo_btn = QtGui.QHBoxLayout(self.area_btn)
        self.lo_plt = QtGui.QVBoxLayout(self.area_plt)

        # add plots
        self.plt = []
        for i in xrange(self.nchan):
            self.plt.append(TimeSeriesPlot(parent=self.area_plt, range=self.range))
            self.lo_plt.addWidget(self.plt[i])

        # size policy
#        self.setSizePolicy(SIZE_POL)

    ## slots
    @QtCore.pyqtSlot(N.ndarray, N.ndarray)
    def set_data(self, data, events=None, gtruth=None):
        """update data plots

        :Parameters:
            data : ndarray
                The data to update.
            events
                Event data for markers.
            gtruth
                Groundtruth data for markers.
        """

        try:
            if data.shape[1] != self.nchan:
                raise ValueError(
                    'wrong shape on data! shape:%s, nchan:%s' %
                    (data.shape, self.nchan)
                )
            for i, plt in enumerate(self.plt):
                try:
                    plt.set_data(data[:, i], events, gtruth)
                except Exception, ex:
                    self._err.showMessage(str(ex))

            if self.replot_on_update is True:
                for plt in self.plt:
                    plt.replot()

        except Exception, ex:
            self._err.showMessage(str(ex))


class QualityPlot(Qwt5.QwtPlot):
    """a plot for a single channel time series data with event markers"""

    ## constructor
    def __init__(self, parent=None, range=2.0):
        """
        :Parameters:
            parent : QObject
                Qt parent.
                Default=None
            range : float
                Axis range. Axis will have range [-range,range].
        """

        # super
        super(QualityPlot, self).__init__(parent)
        self.resize(400, 300)

        # internal members
        self._err = QtGui.QErrorMessage.qtHandler()
        self.range = range

        # size policy
#        self.setSizePolicy(SIZE_POL)

        # layout
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(True)
        self.setAxisScale(Qwt5.QwtPlot.yLeft, -float(self.range), float(self.range))
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setAutoReplot(True)
        self.setCanvasBackground(QtCore.Qt.white)
#        self.setSizePolicy(SIZE_POL)

        # curve
        self._data = d = Qwt5.QwtPlotCurve('data')
        d.setPen(QtGui.QPen(QtCore.Qt.black))
        d.setStyle(Qwt5.QwtPlotCurve.NoCurve)
        d.setSymbol(
            Qwt5.QwtSymbol(
                Qwt5.QwtSymbol.Star1,
                QtGui.QBrush(CURVECOLOR),
                CURVECOLOR,
                QtCore.QSize(15, 15)
            )
        )
        d.attach(self)

        # qsnr
        self._qsnrcurve = d = Qwt5.QwtPlotCurve('qsnr')
        d.setPen(QtGui.QPen(QtCore.Qt.red))
        d.setStyle(Qwt5.QwtPlotCurve.NoCurve)
        d.setSymbol(
            Qwt5.QwtSymbol(
                Qwt5.QwtSymbol.Star1,
                QtGui.QBrush(QtCore.Qt.red),
                QtCore.Qt.red,
                QtCore.QSize(15, 15)
            )
        )
        d.attach(self)

        # qstereo
        self._qstereocurve = d = Qwt5.QwtPlotCurve('qstereo')
        d.setPen(QtGui.QPen(QtCore.Qt.blue))
        d.setStyle(Qwt5.QwtPlotCurve.NoCurve)
        d.setSymbol(
            Qwt5.QwtSymbol(
                Qwt5.QwtSymbol.Star1,
                QtGui.QBrush(QtCore.Qt.blue),
                QtCore.Qt.blue,
                QtCore.QSize(15, 15)
            )
        )
        d.attach(self)

        # events
        self._events = e = Qwt5.QwtPlotCurve('events')
        e.setStyle(Qwt5.QwtPlotCurve.NoCurve)
        e.setSymbol(
            Qwt5.QwtSymbol(
                Qwt5.QwtSymbol.DTriangle,
                QtGui.QBrush(EVENTCOLOR),
                EVENTCOLOR,
                QtCore.QSize(15, 15)
            )
        )
        e.attach(self)

        # zeroline marker
        self._zeroline = z = Qwt5.QwtPlotMarker()
        z.setLinePen(QtGui.QPen(ORIGINCOLOR))
        z.setLineStyle(Qwt5.QwtPlotMarker.HLine)
        z.attach(self)



    ## slots
    @QtCore.pyqtSlot(N.ndarray, N.ndarray)
    def set_data(self, xticks, data, events=N.zeros(0)):
        """update the plot with new chunk of data

        :Parameters:
            xticks: ndarray containing the x coordinates of the datapoints in
                    data
            data : ndarray
                A 1d array with data to show.
            events : ndarray
                A 1d array of event times to show.
        """

        # data
        self._data.setData(xticks, data)

        # events
        self._events.setData(events, N.ones(events.size) * self.range)

        # range
        if data is not None and data.size > 0:
            self.setAxisScale(Qwt5.QwtPlot.yLeft, data.min() - 1, data.max() + 1)

#        # replot
#        self.replot()

    ## slots
    @QtCore.pyqtSlot(N.ndarray, N.ndarray)
    def set_qsnr(self, xticks, qsnr):
        """update the plot with new chunk of data"""
        # data
        self._qsnrcurve.setData(xticks, qsnr)

    ## slots
    @QtCore.pyqtSlot(N.ndarray, N.ndarray)
    def set_qstereo(self, xticks, qstereo):
        """update the plot with new chunk of data"""
        # data
        self._qstereocurve.setData(xticks, qstereo)

##---MAIN
if __name__ == '__main__':
    pass
