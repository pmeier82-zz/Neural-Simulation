# -*- coding: utf-8 -*-
#
# posi - data_interface.py
#
# Philipp Meier - <pmeier82 at gmail dot com>
# 2010-03-11
#
# $Id: interface.py 4931 2010-07-29 20:38:50Z phil $
#

"""data interface

This interface provides an (qt) event based interface to aquire and buffer data
from a (potentially remote) data source (abstracted in another class). Incomming
data is buffered until a desired amount is stored. The stored package is then
passed on.
"""
__docformat__ = 'restructuredtext'


##---IMPORTS

from PyQt4 import QtCore, QtGui
import scipy as N
from nsim.gui import Ui_InitDialog
from package import SimPkg
from client import SimIOClientNotifier, SimIOConnection


##---CONSTANTS

#DEFAULT_VELOCITY = 25.0        # realistic value
DEFAULT_VELOCITY = 9999.0       # development value


##---CLASSES

class ChunkContainer(object):
    """container class to store data for one chunk

    was introduced because python strings as dictionary keys get somehow
    converted to QString after passing through the signal->slot system.
    """

    def __init__(self, cnklen):
        """
        :Parameters:
            cnklen : int
                defining how long this chunk is in samples
        """

        self.cnklen = int(cnklen)
        self.cnkptr = 0
        self.noise = None
        self.units = {}
        self._finalized = False

    def append(self, item_list):
        """append to the container the contents of a SimPkg
        
        will only append up to the cnklen!
        
        :Parameters:
            item_list : list
                The contents of a T_REC package.
        :Return:
            None : if append was ok and did not overshoot the chunk length
            list : residual item_list if the append overshoots the chunk length
        """

        # checks
        if len(item_list) == 0:
            raise ValueError('contents have to include at least the noise strip')
        if (len(item_list) - 1) % 3 != 0:
            raise ValueError('invalid content count! has to be noise + 3tuples')
        # TODO: more checks ?
        # prepare
        rval = []
        noise = item_list.pop(0)
        appendlen, nchan = noise.shape
        if self.noise is None:
            self.noise = N.empty((self.cnklen, nchan))
        # normal append case
        thislen = appendlen
        if self.cnkptr + thislen >= self.cnklen:
            thislen = self.cnklen - self.cnkptr
        # append noise
        copy_ar(
            noise,
            slice(0, thislen),
            self.noise,
            slice(self.cnkptr, self.cnkptr + thislen)
        )
        if thislen != appendlen:
            rval.append(noise[thislen:, :].copy())
        # append unit data
        while len(item_list) > 0:
            # get data
            ident = item_list.pop(0)
            if isinstance(ident, N.ndarray):
                ident = ident[0]
            wform = item_list.pop(0)
            gtrth = item_list.pop(0)
            if len(gtrth) == 0:
                continue
            # do we know this ident?
            if ident not in self.units:
                self.units[ident] = {'wf_buf':[], 'gt_buf':[]}
            # handle waveform
            wform_key = -1
            for i in xrange(len(self.units[ident]['wf_buf'])):
                if N.allclose(wform, self.units[ident]['wf_buf'][i]):
                    wform_key = i
                    break
            if wform_key == -1:
                self.units[ident]['wf_buf'].append(wform)
                wform_key = len(self.units[ident]['wf_buf']) - 1
            # handle ground truth
            gtrth_resid = []
            for item in gtrth:
                # interval out of scope
                if item[0] + self.cnkptr > self.cnklen:
                    item = [item[0] - thislen, item[1] - thislen, item[2], item[3]]
                    gtrth_resid.append(item)
                # interval ok, but end out of scope
                elif item[1] + self.cnkptr > self.cnklen:
                    self.units[ident]['gt_buf'].append([
                        wform_key,
                        item[0] + self.cnkptr,
                        self.cnklen,
                        item[2],
                        thislen - item[0] + item[2]
                    ])
                    gtrth_resid.append([
                        0,
                        item[1] - thislen,
                        item[3] - item[1] + thislen,
                        item[3]
                    ])
                else:
                    self.units[ident]['gt_buf'].append([
                        wform_key,
                        item[0] + self.cnkptr,
                        item[1] + self.cnkptr,
                        item[2],
                        item[3]
                    ])
            # rval building
            if len(gtrth_resid) > 0:
                gtrth_resid = N.vstack(gtrth_resid)
                rval.extend([ident, wform, gtrth_resid])
        # return
        self.cnkptr += thislen
        return rval


class InitDlg(QtGui.QDialog, Ui_InitDialog):

    def __init__(self, parent=None):

        # super
        super(InitDlg, self).__init__(parent)
        self.setupUi(self)

    @staticmethod
    def init_dialog(data, parent=None):
        """shows an init dlg and return its choices

        This class methods shows an init dlg and returns the choices.

        :Parameters:
            data : ndarray
                Contents of a status package.
            parent : QWidget
                Qt parent.
        :Returns:
            ident : long
            sample_rate : float
            config : list
        """

        # checks and inits
        ident = None
        sample_rate = None
        frame_size = None
        config = []

        try:
            # no recorders in scene?
            assert len(data[data[:, 1] == 20, 0]) > 0

            # build dlg
            dlg = InitDlg(parent=parent)
            for entry in data:
                if entry[1] == 10:
                    item = QtGui.QListWidgetItem('N - %s' % long(entry[0]))
                    item.setFlags(QtCore.Qt.NoItemFlags)
                    dlg.main_list.addItem(item)
                elif entry[1] == 20:
                    item = QtGui.QListWidgetItem('R - %s' % long(entry[0]))
                    item.setFlags(
                        QtCore.Qt.ItemIsSelectable |
                        QtCore.Qt.ItemIsEnabled
                    )
                    dlg.main_list.addItem(item)
                else:
                    continue
            dlg.show()
            dlg.raise_()
            dlg.activateWindow()
            assert dlg.exec_() > 0

            # set ident
            ident = long(float(dlg.main_list.currentItem().text()[4:]))
            sample_rate = float(data[data[:, 1] == 0, 0])

            # set config
            # config is a list of items:
            # 0:noise, 1:waveforms, 2:groundtruth, 3:positions
            if dlg.check_noise.isChecked():
                config.append(0)
            if dlg.check_waveform.isChecked():
                config.append(1)
            if dlg.check_groundtruth.isChecked():
                config.append(2)
            if dlg.check_positions.isChecked():
                config.append(3)
        except Exception, ex:
            print str(ex)
            # TODO: meaningfull failure handling ?!
        finally:
            return ident, sample_rate, config


class QNotifier(QtCore.QObject, SimIOClientNotifier):
    sig_notify = QtCore.pyqtSignal()
    def __init__(self, **kwargs):
        QtCore.QObject.__init__(self, kwargs.get('parent', None))
        SimIOClientNotifier.__init__(self, **kwargs)
    def notify(self):
        self.sig_notify.emit()


class NTrodeDataInterface(QtCore.QObject):
    """interface to multichanneled data from a remote data source"""

    ## qt-signals

    sig_new_data = QtCore.pyqtSignal(ChunkContainer)
    sig_update_pos = QtCore.pyqtSignal(float)

    ## constructor

    def __init__(
        self,
        # internals
        cnklen=0.25,
# <REFACTOR>
#        position_tolerance = 0.1,
# </REFACTOR>
        # io class
        io_cls=SimIOConnection,
        addr=('localhost', 31337),
        # qt parent
        parent=None,
    ):
        """
        :Parameters:
            cnklen : float
                The length of data chunk in seconds. The actuall length in
                samples will be calculate once the io - object is connected and
                the sample rate is known.
                Default = 0.1
            io_cls : class
                The io class. Should have members 'delegate', 'q_r' and 'q_s'
                Default = None
            addr : tuple len 2
                A tuple specifying the address of the server to connect to.
                Default = None
            parent : QObject
                Qt parent.
                Default = None
# <REFACTOR>
#            position_tolerance: float
#                Defines the tolerance with which two positions are thought to be
#                equal due to noise in the measurement. If two successive
#                position are unequal, the electrode is moving.
#                Default=0.1
# </REFACTOR>
        """

        # super
        super(NTrodeDataInterface, self).__init__(parent)

        # public members
# <REFACTOR>
#        self.position_tolerance = float(position_tolerance)
# </REFACTOR>
        self.cnklen_init = float(cnklen)
        self.addr = addr

        # members
        self._cnk = None            # the chunk container
        self._cnklen = None         # prop: length of one chunk
        self._identity = None       # prop: identity
        self._io = None             # the io object
        self._io_cls = io_cls       # io object class
        self._io_notifier = None    # notifier for the io object
        self._position = 0.0        # prop: position
        self._sample_rate = None    # prop: sample_rate
        self._status = None         # prop: status
        self._config = None         # prop: config

    def initialize(self):
        """initialize the object"""

        # build and start io object
        self._io_notifier = QNotifier()
        self._io = self._io_cls(self.addr, delegate=self._io_notifier)
        self._io_notifier.sig_notify.connect(self.on_notify)
        self._io.start()

    def finalize(self):
        """clean up the interface and its connection"""

        if self._io is not None:
            if self._io.is_alive():
                self._io.stop()
        self._io = None

    ## properties

    def get_cnklen(self):
        return self._cnklen
    def set_cnklen(self, value):
        if self._sample_rate is None:
            return
        self._cnklen = int(float(value) * self._sample_rate)
        self._cnk = ChunkContainer(self._cnklen)
    cnklen = property(get_cnklen, set_cnklen)

    def get_identity(self):
        return self._identity
    identity = property(get_identity)

    def get_position(self):
        return self._position
    position = property(get_position)

    def get_sample_rate(self):
        return self._sample_rate
    sample_rate = property(get_sample_rate)

    def get_status(self):
        return self._status
    status = property(get_status)

    ## methods behavior

    def handle_recorder_package(self, pkg):
        """write the package data into the chunk buffer"""

        # checks
        if self._cnklen is None or self._cnk is None:
            raise ValueError('trying to handle a recorder package when the chunk length is not known!')
        if pkg.tid != SimPkg.T_REC:
            raise ValueError('trying to handle non recorder package!')

        # inits
        residual = [cont.cont for cont in pkg.cont]
        while len(residual) > 0:
            residual = self._cnk.append(residual)
            if len(residual) > 0:
                self.sig_new_data.emit(self._cnk)
                self._cnk = ChunkContainer(self._cnklen)

    ## qt slots

    @QtCore.pyqtSlot()
    def on_notify(self):
        """called if notified for new package"""

        # XXX: this is called too often on shutdown! investigate

        if self._io is None or not self._io.is_alive():
            return

        while not self._io.q_recv.empty():

            # try to get a package
            try:
                pkg = self._io.q_recv.get(0)
            except:
                break

            # we need to initialize first!
            if self._status is None:
                if pkg.tid == SimPkg.T_STS:
                    # intitialize internals
                    self._identity, self._sample_rate, self._config = \
                        InitDlg.init_dialog(pkg.cont[0].cont)
                    self.cnklen = self.cnklen_init
                    self._status = pkg.cont[0].cont
                    # request position to get initial update
                    self.request_position()
                else:
                    continue

            # if waveform or position package, drop if its not for us
            if pkg.tid in [SimPkg.T_REC, SimPkg.T_POS]:
                if self.identity is not None:
                    if pkg.ident != self.identity:
                        continue

            # what package has been aquired
            if pkg.tid == SimPkg.T_STS:
                self._status = pkg.cont[0].cont
            elif pkg.tid == SimPkg.T_POS:
                try:
                    self._position = float(pkg.cont[0].cont[0])
                    self.sig_update_pos.emit(self._position)
                except:
                    pass
            elif pkg.tid == SimPkg.T_REC:
                self.handle_recorder_package(pkg)
            else:
                print SimPkg.T_MAP[pkg.tid]

    @QtCore.pyqtSlot(float)
    @QtCore.pyqtSlot(float, float)
    def send_to_position(self, position, velocity=DEFAULT_VELOCITY):
        """request to send the recorder to a position

        :Parameters:
            position : float
                The position along the recorders movement trajectory. Zero is
                defined as the entry point, so usually only positive values are
                meaningfull here. Position along the trajector in µm.
            velocity : float
                The velocity to use for the movement in µm / s.
                Default = 9999.0
        """

        self._io.q_send.put(
            SimPkg(
                tid=SimPkg.T_POS,
                ident=self._identity,
                cont=(N.array([position, velocity]),)
            )
        )

    @QtCore.pyqtSlot()
    def request_position(self):
        """retrieve the current position of the device"""

        self._io.q_send.put(SimPkg(tid=SimPkg.T_POS, ident=self.identity))

    ## other stuff

# <REFACTOR>
    # TODO: implement emergency stop behavior
    @QtCore.pyqtSlot()
    def emergency_stop(self):
        """stop the electrode immediatly
        call this function only, if somethingwent terribly wrong
        """

        pass
# </REFACTOR>

# <REFACTOR>
#    def position_equal(self,pos1, pos2):
#        """Returns true if the two positions are equal with a certain tolerance,
#        false otherwise
#        """
#        if pos1 is None or pos2 is None:
#            return False
#        return abs(pos1-pos2) < self.position_tolerance
# </REFACTOR>


##---FUNCTIONS - historic

def copy_ar(src, src_slc, dst, dst_slc):
    """copy src[src_slc] to dst[dst_slc]

    Helper function to copy an array slice from an source array `src` into a
    destination array `dst`. The slices (`src_slc` and `dst_slc`) must agree in
    size and define what slice will be copied where.
    """

    assert isinstance(src, N.ndarray) and isinstance(dst, N.ndarray)
    assert dst_slc.stop - dst_slc.start == src_slc.stop - src_slc.start
    dst[dst_slc] = src[src_slc].copy()

def copy_gt(wf, gt, dst, cap=0, offset=0):
    """copy part of the wf and gt matches 0:cap from scr to dst
    :Parameters:
        wf : list of waveforms (ndarray)
        gt : list groundtruth interval (ndarray)
        dst : list destination to append to
        cap : int giving the capping behavior
        offset : int giving a global offset
    """

    for i in xrange(len(wf)):
        gt_new = []
        for j in xrange(0, gt[i].shape[0]):
            if cap > 0:
                if gt[i][j, 0] >= cap:
                    # totally off
                    continue
                else:
                    if gt[i][j, 1] >= cap:
                        # cut it
                        gt_new.append([
                            gt[i][j, 0] + offset,
                            offset + cap,
                            gt[i][j, 2],
                            cap - gt[i][j, 0] + gt[i][j, 2]
                        ])
                    else:
                        # its ok
                        gt_new.append([
                            gt[i][j, 0] + offset,
                            gt[i][j, 1] + offset,
                            gt[i][j, 2],
                            gt[i][j, 3]
                        ])
            elif cap < 0:
                if gt[i][j, 1] < -cap:
                    # totally off
                    continue
                else:
                    if gt[i][j, 0] < -cap:
                        # cut it
                        gt_new.append([
                            0,
                            gt[i][j, 1] + cap,
                            gt[i][j, 3] - gt[i][j, 1] - cap,
                            gt[i][j, 3]
                        ])
                    else:
                        # its ok
                        gt_new.append([
                            gt[i][j, 0],
                            gt[i][j, 1],
                            gt[i][j, 2],
                            gt[i][j, 3]
                        ])
            else:
                gt_new.append([
                    gt[i][j, 0] + offset,
                    gt[i][j, 1] + offset,
                    gt[i][j, 2],
                    gt[i][j, 3]
                ])
        if len(gt_new) > 0:
            dst.append(wf[i])
            dst.append(N.asarray(gt_new))


##---MAIN

if __name__ == '__main__':

    app = QtGui.QApplication([])

    io = NTrodeDataInterface()
    io.initialize()
