## -*- coding: utf-8 -*-
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
# nsim - scene_generator.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-09-17
#

from __future__ import division

"""tool to generate a scene archive for the Neural Simulation

This module provides a GUI based approach to scene building. A initial scene can
be configured and saved as a loadable archive. The loadable archives are HDF5
containers with a predefined structure, as explained here:

SCENE ARCHIVE (.sca) - HDF5 container
    #TYPE : string node
        all groups must contain a '#TYPE' identifying its purpose as a string.
        available #TYPE identifiers are:
            SCENE_ARCHIVE : for the root node
            CONFIG        : for the NS config group
            NEURON_DATA   : for the neuron data group
            NeuronData    : for NeuronData nodes
            SCENE         : for the scene group
            SimObject     : SimObject nodes
    #CLASS : string node
        various groups define a parameter set to instantiate a class. this
        string holds the name of the class as given by class.__class__.
    
    The basic structure for a scene archive is:
        
        ROOT
         |- #TYPE = 'SCENE_ARCHIVE'
         |- CONFIG
         |   |- #TYPE = 'CONFIG'
         |   |- frame_size = 1024
         |   |- sample_rate = 16000.0
         |   |- [...]
         |- NEURON_DATA
         |   |- #TYPE = 'NEURON_DATA'
         |   |- NDATA00
         |   |   |- #TYPE = 'NeuronData'
         |   |   |- #CLASS = '<neurondata subclass name>'
         |   |   |- [...]
         |   |- NDATA01
         |   |   |- #TYPE = 'NeuronData'
         |   |   |- #CLASS = '<neurondata subclass name>'
         |   |   |- [...]
         |   |- [...]
         |- SCENE
             |- #TYPE = 'SCENE'
             |- SIMOBJ00
             |   |- #TYPE = 'SimObject'
             |   |- #CLASS = '<simobject subclass name>'
             |   |- [...]
             |- SIMOBJ01
             |   |- #TYPE = 'SimObject'
             |   |- #CLASS = '<simobject subclass name>'
             |   |- [...]
             |- [...]
    
    All nodes are tagged with at #TYPE tag and when a node specifies a parameter
    set for a class, a #CLASS tag is additionally given.
    
    [t.b.c]  
"""
__docformat__ = 'restructuredtext'


##---IMPORTS

import scipy as N
from gui.Ui_scene_gen import Ui_SceneGenerator
from PySide import QtCore, QtGui
from tables import openFile


##---CONSTANTS

WF = [
    - 0.0014034089,
    - 0.002245145,
    - 0.003079994,
    - 0.004163863,
    - 0.0070844376,
    - 0.020370215,
    - 0.027436305,
    - 0.02857418,
    - 0.026155144,
    - 0.022309005,
    - 0.01807256,
    - 0.013534825,
    - 0.008330006,
    - 0.0034387822,
    2.2056947E-5,
    0.0023328324,
    0.003821157,
    0.004755203,
    0.0053204517,
    0.005637154,
    0.005784857,
    0.005816808,
    0.005769473,
    0.005667955,
    0.0055297515,
    0.0053672874,
    0.005189528,
    0.0050029815,
    0.0048123444,
    0.004620978,
    0.0044312533,
    0.0042448267,
    0.0040628263,
    0.0038860017,
    0.003714828,
    0.003549579,
    0.003390394,
    0.0032373113,
    0.0030903,
    0.0029492783,
    0.0028141278,
    0.002684705,
    0.0025608384,
    0.0024423588,
    0.0023290904,
    0.0022208546,
    0.0021174715,
    0.002018759,
    0.0019245415,
    0.0018346395,
    0.001748883,
    0.0016670927,
    0.0015891049,
    0.0015147646,
    0.0014439181,
    0.0013764189,
    0.0013121216,
    0.0012508878,
    0.0011925797,
    0.0011370727,
    0.0010842364,
    0.0010339515,
    9.861033E-4,
    9.4057573E-4,
    8.97265E-4,
    8.5606385E-4,
    8.168654E-4,
    7.795761E-4,
    7.4411003E-4,
    7.1037916E-4,
    6.783019E-4,
    6.4780086E-4,
    6.1880064E-4,
    5.912264E-4,
    5.6501065E-4,
    5.4008764E-4,
    5.163933E-4,
    4.9386563E-4,
    4.7244882E-4,
    4.5208808E-4,
    4.3272844E-4,
    4.1432166E-4,
    3.9682208E-4,
]


##---CLASSES

class SceneGenerator(QtGui.QMainWindow, Ui_SceneGenerator):
    """scene generator gui form"""

    def __init__(self, parent=None, **kwargs):
        """
        :Parameters:
            parent : QWidget
                qt parent
        """

        # super and gui init
        super(SceneGenerator, self).__init__(parent)
        self.setupUi(self)

        # connections
        self.wf_widget = WFWidget(self.frame)
        self.verticalLayout_2.addWidget(self.wf_widget)

        self.pushButton.clicked.connect(self.on_pb)

    @QtCore.Slot()
    def on_pb(self):
        """bushButton clicked slot"""

        self.wf_widget.set_waveform(WF)


class WFWidget(QtGui.QWidget):
    """waveform slider widget"""

    def __init__(self, parent=None, nsample=15):
        """
        :Parameters:
            parent : QWidget
                qt parent
            nsample : int
                initial sample length.
                Default=15
        """

        #super
        super(WFWidget, self).__init__(parent)

        #members
        self.nsample = 0
        self.wf_base = []
        self.wf_poly = None
        self.margin = 25
        self.mouse_drawing = None

        # inits
        self.setPalette(QtGui.QPalette(QtGui.QColor(250, 250, 250)))
        self.setAutoFillBackground(True)
        self.set_waveform(WF)

    def set_waveform(self, wf):
        """set a new waveform"""

        # asserts
        assert isinstance(wf, (list, N.ndarray))
        self.wf_base = WFWidget.normalise_wf(wf)
        self.nsample = len(self.wf_base)
        self.update()

    ## QT events

    def mousePressEvent(self, evt):

        if evt.button() == QtCore.Qt.LeftButton:

            # get x if its inside the margins
            x = int(evt.pos().x())
            if x < self.margin or x > self.width() - self.margin:
                print 'offboard'
                return

            # get sample
            dx = (self.width() - 2 * self.margin) / (self.nsample - 1)
            self.mouse_drawing = int((x - self.margin + 0.5 * dx) / dx)
            print 'sample:', self.mouse_drawing

    def mouseReleaseEvent(self, evt):

        if evt.button() == QtCore.Qt.LeftButton:
            if self.mouse_drawing is not None:
                # get y if its inside the margins
                y = int(evt.pos().y())
                if y < self.margin or y > self.height() - self.margin:
                    print 'offboard'
                    return

                # get new sample position
                yrh = (self.height() - 2 * self.margin) / 2.0
                y -= self.margin
                y -= yrh
                y /= yrh
                self.wf_base[self.mouse_drawing] = -y
                print 'sample_y:', self.wf_base[self.mouse_drawing]
                self.mouse_drawing = None
                self.update()

    def paintEvent(self, evt):

        # get painter
        painter = QtGui.QPainter(self)
        # write zero line
        yzero = self.height() / 2.0
        painter.setPen(QtCore.Qt.red)
        painter.drawLine(
            QtCore.QLineF(
                self.margin, yzero,
                self.width() - self.margin, yzero
            )
        )
        painter.drawRect(
            QtCore.QRect(
                self.margin,
                self.margin,
                self.width() - 2 * self.margin,
                self.height() - 2 * self.margin
            )
        )
        # write waveform
        if self.wf_base is not None:
            if len(self.wf_base) > 0:
                painter.setPen(QtCore.Qt.blue)
                self.wf_poly = WFWidget.wf_to_poly(
                    self.wf_base,
                    self.width(), self.margin, 0,
                    self.height(), self.margin, 0
                )
                painter.drawPolyline(self.wf_poly)

    ## static methods

    @staticmethod
    def wf_to_poly(wf, xr, xm, xo, yr, ym, yo):
        """yield a list of QPolygon instance representing the waveform
        
        :Parameters:
            wf : list
                list of the waveform samples
            xstuff : tuple
                tuple defining the x axis. 0) range, 1) offset, 2) margin 
            ystuff : tuple
                tuple defining the y axis. 0) range, 1) offset, 2) margin
        """

        # inits
        yrh = (yr - 2.0 * ym) / 2.0
        dx = (xr - 2 * xm) / float(len(wf) - 1)

        # generate
        plist = []
        for i in xrange(len(wf)):
            plist.append(
                QtCore.QPoint(
                    xo + xm + i * dx,
                    - 1.0 * wf[i] * yrh + yrh + yo + ym
                )
            )

        # return
        return QtGui.QPolygon(plist)

    @staticmethod
    def normalise_wf(wf):
        """normalise wf to values on the interval [-1.0,+1.0]"""

        mywf = N.asarray(wf)
        factor = 1.0 / N.absolute(mywf).max()
        return factor * mywf


class SceneArchiveContainer(object):
    """scene archive container (.sca) class
        
    defining the structure inside an hdf5 container to hold the entire scene
    """

    def _init__(self, path_to_arc):
        """
        :Parameters:
            path_to_arc : str
                Path to the hdf5 archive in the local file system.
        """

        # get handle to archive
        try:
            self._arc = openFile(path_to_arc, 'r')
        except:
            self._arc = openFile(path_to_arc, 'w')
        self._grp_config = None
        self._grp_ndata = None
        self._grp_scene = None

        # establish main structure
        if '/__TYPE__' not in self._arc:
            self._arc.createArray(self._arc.root, '__TYPE__', 'SCENE_ARCHIVE')
        if self._has_main_grp('CONFIG'):
            self._grp_config = self._get_main_grp('CONFIG')
        else:
            self._grp_config = self._arc.createGroup(self._arc.root, 'CONFIG')
            self._arc.createArray(self._grp_config, '__TYPE__', 'CONFIG')
        if self._has_main_grp('NEURON_DATA'):
            self._grp_ndata = self._get_main_grp('NEURON_DATA')
        else:
            self._grp_ndata = self._arc.createGroup(self._arc.root, 'NEURON_DATA')
            self._arc.createArray(self._grp_ndata, '__TYPE__', 'NEURON_DATA')
        if self._has_main_grp('SCENE'):
            self._grp_scene = self._get_main_grp('SCENE')
        else:
            self._grp_scene = self._arc.createGroup(self._arc.root, 'SCENE')
            self._arc.createArray(self._grp_scene, '__TYPE__', 'SCENE')

    ## internal helper functions

    def _has_main_grp(self, grp_type):
        """return True if the main group of grp_type is present, False else"""

        return self._get_main_grp(grp_type) is not None

    def _get_main_grp(self, grp_type):
        """returns the main group of grp_type if present, None else"""

        rval = None
        for grp in self._arc.walkGroups():
            if '__TYPE__' in grp:
                if grp.__TYPE__.read() == grp_type:
                    rval = grp
                    break
        return rval

    @staticmethod
    def make_tag(tag_name):
        return '#%s' % tag_name

    ## data interface - CONFIG

    def get_config(self):
        """get CONFIG section as dict"""

        rval = {}
        for item in self._arc.walkNodes(self._grp_config):
            if item.name.startswith('#'):
                continue
            rval[item.name] = item.read()
        return rval

    def set_config(self, config):
        """set CONFIG section from dict"""

        assert isinstance(config, dict)

        for k, v in config:
            try:
                node = getattr(self._grp_config, k)
                setattr(self._grp_config, k, v)
            except:
                self._arc.createArray(self._grp_config, k, v)

    def get_config_item(self, key):
        """get single config item"""

        rval = None
        try:
            return getattr(self._grp_config, key)
        except:
            return None

    def set_config_item(self, key, val):
        """set single config item"""

        setattr(self._grp_config, key, val)

    ## data interface - NEURON_DATA

    def load_ndata(self, key):
        """load a neuron data from the archive"""




##---MAIN

def main(args):

    app = QtGui.QApplication(args)
#    app.lastWindowClosed.connect(app.quit)

    win = SceneGenerator()
    win.show()

    return app.exec_()

if __name__ == '__main__':

    import sys
    sys.exit(main(sys.argv))
