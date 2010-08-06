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
# sim - start.py
#
# Philipp Meier - <pmeier82 at googlemail dot com>
# 2010-01-21
#

"""gui module for the neural simulation

This module provides gui frontend to the neural simulation. Simulation scenes
can be edited and the simulation can be controlled. The gui logs all relevant
events a log box and provides a frointend to create scenes or load canned scene
files.

This module is only the gui frontend, for details on the simulation see
simulation.py.
"""
__doctype__ = 'restructuredtext'


##---IMPORTS

import sys
import traceback
from PyQt4 import QtCore, QtGui
from nsim.gui import (
    Ui_AddNeuronDialog,
    Ui_AddRecorderDialog,
    Ui_SimGui
)
from nsim.simulation import BaseSimulation, SimExternalDelegate


##---CONSTANTS

LOG_BUF_LEN = 512


##---CLASSES

class SimQt4Delegate(QtCore.QObject, SimExternalDelegate):
    """QObject to provide qt-signal from the simulation for the gui"""

    ## signals

    sig_frame = QtCore.pyqtSignal(long)
    sig_frame_size = QtCore.pyqtSignal(int)
    sig_log = QtCore.pyqtSignal(str)
    sig_sample_rate = QtCore.pyqtSignal(float)

    ## constructor

    def __init__(self, parent):
        """
        :Parameters:
            parent : SimulationGui
                The qt parent object. This is strictly required, as the
                delegate poses as a glue/relay class between the python
                simulation and the qt gui component.
        """

        # check for parent
#        if not issublass(parent, QtCore.QObject)

        # super
        QtCore.QObject.__init__(self, parent)
        SimExternalDelegate.__init__(self)

        # connections
        self.sig_frame.connect(self.parent().on_update_frame)
        self.sig_frame_size.connect(self.parent().on_update_frame_size)
        self.sig_log.connect(self.parent().on_append_log)
        self.sig_sample_rate.connect(self.parent().on_update_sample_rate)

    ## event delegate methods

    def frame(self, frame):
        """update frame"""

        self.sig_frame.emit(frame)

    def frame_size(self, frame_size):
        """update frame size"""

        self.sig_frame_size.emit(frame_size)

    def log(self, log_str):
        """log a sting"""

        self.sig_log.emit(log_str)

    def sample_rate(self, sample_rate):
        """update sample rate"""

        self.sig_sample_rate.emit(sample_rate)


class SimulationGui(QtGui.QMainWindow, Ui_SimGui):
    """a BaseSimulation instance with a control and info gui"""

    ## constructor

    def __init__(self, parent=None):
        """
        :Parameters:
            parent : QObject
                The QT framework parent.
                Default=None
        """

        # super and ui setup
        super(SimulationGui, self).__init__(parent)
        self.setupUi(self)

        # internal member - simulation and event delegate
        self._sim_gui_handle = SimQt4Delegate(parent=self)
        self._sim = BaseSimulation(externals=[self._sim_gui_handle])
        self._timer = QtCore.QTimer()

        # gui member - models
        self._log_model = QtGui.QStringListModel()
        self.lst_log.setModel(self._log_model)
        self._scene_model = QtGui.QStandardItemModel()
        self._trn_sim = QtGui.QStandardItem('Simulation')
        self._scene_model.appendRow(self._trn_sim)
        self._trn_ndata = QtGui.QStandardItem('NeuronData')
        self._scene_model.appendRow(self._trn_ndata)
        self._trn_nrn = QtGui.QStandardItem('Neurons')
        self._scene_model.appendRow(self._trn_nrn)
        self._trn_rec = QtGui.QStandardItem('Recorders')
        self._scene_model.appendRow(self._trn_rec)
        self._scene_model.setHorizontalHeaderLabels(['Name', 'Value'])
        self.tre_scene.setModel(self._scene_model)
        self._io_model = QtGui.QStandardItemModel()
        self.tre_output.setModel(self._io_model)

        # gui members - reusable dialogs
        self._err = QtGui.QErrorMessage.qtHandler()
        self.progress.setVisible(False)
        self.progress.reset()

        # connections - sim internals
        self._timer.timeout.connect(self._sim.simulate)

        # connections - control panel
        self.btn_reset.clicked.connect(self.on_input_cmdpnl_reset)
        self.btn_steps.clicked.connect(self.on_input_cmdpnl_steps)
        self.btn_timer.clicked.connect(self.on_input_cmdpnl_timer)
        self.cb_frame_size.activated.connect(self.on_input_cmdpnl_frame_size)
        self.cb_sample_rate.activated.connect(self.on_input_cmdpnl_sample_rate)

        # connections - scene dock
        self.btn_dscene_sc_load.clicked.connect(self.scene_load)
        self.btn_dscene_sc_save.clicked.connect(self.scene_save)
        self.btn_dscene_neuron.clicked.connect(self.scene_add_neuron)
        self.btn_dscene_neuron_data.clicked.connect(self.scene_add_neuron_data)
        self.btn_dscene_recorder.clicked.connect(self.scene_add_recorder)
        self.btn_dscene_refresh.clicked.connect(self.scene_build_model)
        self.btn_dscene_remove.clicked.connect(self.scene_remove)

        # connections - output dock
        self.btn_dio_restart.clicked.connect(self.io_restart)
        self.btn_dio_refresh.clicked.connect(self.io_build_model)

        # connections - actions
        self.actionAbout.triggered.connect(self.on_about)
        self.actionAbout_Qt.triggered.connect(self.on_about_qt)
        self.actionPreferences.triggered.connect(self.comming_soon)

        # init gui
        self.on_input_cmdpnl_reset()

    ## delegate event slots

    def on_update_info_internal(self, info):
        """update internal infos"""
        pass

    def on_update_info_ndata(self, info):
        """update neuron data infos"""
        pass

    def on_update_info_neuron(self, info):
        """update neuron infos"""
        pass

    def on_update_info_recorder(self, info):
        """update recorder infos"""
        pass

    def on_update_info_complete(self, info):
        """update complete infos"""
        pass

    @QtCore.pyqtSlot(str)
    def on_append_log(self, log_str):
        """log a sting"""

        if self._log_model.rowCount() > LOG_BUF_LEN:
            self._log_model.removeRow(0)
        self._log_model.insertRow(self._log_model.rowCount())
        self._log_model.setData(
            self._log_model.index(self._log_model.rowCount() - 1),
            str(log_str)
        )
        self.lst_log.scrollTo(
            self._log_model.index(self._log_model.rowCount() - 1)
        )

    @QtCore.pyqtSlot(long)
    def on_update_frame(self, frame):
        """update frame index"""

        self.edt_frame.setText(str(frame))

    @QtCore.pyqtSlot(int)
    def on_update_frame_size(self, frame_size):
        """update frame size"""

        if self.cb_frame_size.findText(str(frame_size)) < 0:
            self.cb_frame_size.addItem(str(frame_size))
        self.cb_frame_size.setCurrentIndex(
            self.cb_frame_size.findText(str(frame_size))
        )

    @QtCore.pyqtSlot(float)
    def on_update_sample_rate(self, sample_rate):
        """update sample rate"""

        if self.cb_sample_rate.findText(str(sample_rate)) < 0:
            self.cb_sample_rate.addItem(str(sample_rate))
        self.cb_sample_rate.setCurrentIndex(
            self.cb_sample_rate.findText(str(sample_rate))
        )

    ## gui user input slots - command panel

    @QtCore.pyqtSlot(int)
    def on_input_cmdpnl_frame_size(self, inp):

        try:
            self._sim.frame_size = float(self.cb_frame_size.itemText(inp))
        finally:
            self.cb_frame_size.clearFocus()
            self.scene_build_model()

    @QtCore.pyqtSlot(int)
    def on_input_cmdpnl_sample_rate(self, inp):

        try:
            self._sim.sample_rate = float(self.cb_sample_rate.itemText(inp))
        finally:
            self.cb_sample_rate.clearFocus()
            self.scene_build_model()

    @QtCore.pyqtSlot()
    def on_input_cmdpnl_reset(self):

        if self._timer.isActive():
            self.on_input_cmdpnl_timer()
        self._log_model.removeRows(0, self._log_model.rowCount())
        self._sim.initialize()
        self.scene_build_model()
        self.io_build_model()

    @QtCore.pyqtSlot()
    def on_input_cmdpnl_steps(self):

        try:
            nframes = int(self.edt_steps.text())
        except:
            return

        # progress dialog for longer stuff
        self.progress.reset()
        self.progress.setRange(0, nframes)
        self.progress.setValue(0)
        self.progress.setVisible(True)

        for i in xrange(nframes):
            self._sim.simulate()
            self.progress.setValue(i + 1)
        self.progress.reset()
        self.progress.setVisible(False)

    @QtCore.pyqtSlot()
    def on_input_cmdpnl_timer(self):
        if self._timer.isActive():
            # stop timer
            self._timer.stop()
            self._set_enabled(True)
            self.btn_timer.setText('Start Timer')
            self.on_append_log('Timer stopped!')
        else:
            # start timer
            try:
                step_size = int(self.edt_timer.text())
                self._timer.setInterval(step_size)
            except:
                return
            self._set_enabled(False)
            self.btn_timer.setText('Stop Timer')
            self.on_append_log('Timer started!')
            self._timer.start()

    ## scene dock slots

    @QtCore.pyqtSlot()
    def scene_add_neuron_data(self):

        try:
            # chose files
            rval = QtGui.QFileDialog.getOpenFileNames(
                self,
                'Select files to open'
            )
            if len(rval) == 0:
                return
            rval = map(str, rval)

            # progress dialog
            self.progress.reset()
            self.progress.setRange(0, len(rval))
            self.progress.setValue(0)
            self.progress.setVisible(True)

            # load neuron datas
            ndatas = 0
            for path in rval:
                ndatas += self._sim.neuron_data.insert(path)
                self.progress.setValue(self.progress.value() + 1)
            self.progress.reset()
            self.progress.setVisible(False)
            self.scene_build_model()
            QtGui.QMessageBox.information(
                self,
                'Info',
                'found %d neuron data archives' % ndatas
            )

        except:
            self.error_dialog()

    @QtCore.pyqtSlot()
    def scene_add_neuron(self):

        try:

            # do we have neuron data?
            if len(self._sim.neuron_data) == 0:
                QtGui.QMessageBox.warning(
                    self,
                    'REMINDER',
                    'No NeuronData loaded! Please load NeuronData first.'
                )
                return

            # user input
            dialog = AddNeuronDialog(self, self._sim.neuron_data)
            dialog.show()
            dialog.raise_()
            dialog.activateWindow()
            if dialog.exec_() == 0:
                return

            # build parameters
            kwargs = {}
            if str(dialog.edt_name.text()) != '':
                val = str(dialog.edt_name.text())
                kwargs.update(name=val)
            if str(dialog.edt_position.text()) != '':
                val = map(float, str(dialog.edt_position.text()).split(' '))
                kwargs.update(position=val)
            if str(dialog.edt_orientation.text()) != '':
                val = str(dialog.edt_orientation.text())
                if val.lower() == 'false':
                    val = False
                elif val.lower() == 'true':
                    val = True
                else:
                    val = map(float, val.split(' '))
                kwargs.update(orientation=val)
            kwargs.update(neuron_data=str(dialog.cb_data.currentText()))
            if str(dialog.edt_frate.text()) != '':
                val = float(dialog.edt_frate.text())
                kwargs.update(rate_of_fire=val)
            if str(dialog.edt_ampl.text()) != '':
                val = float(dialog.edt_ampl.text())
                kwargs.update(amplitude=val)
            if str(dialog.edt_cluster.text()) != '':
                val = int(dialog.edt_cluster.text())
                kwargs.update(cluster=val)

            # build neuron
            rval = self._sim.register_neuron(**kwargs)
            self.scene_build_model()
            QtGui.QMessageBox.information(
                self,
                'Neuron added',
                'Neuron: %s\n\nCalled with:\n%s' % (rval, kwargs)
            )

        except:
            self.error_dialog()

    @QtCore.pyqtSlot()
    def scene_add_recorder(self):

        try:

            # user input
            dialog = AddRecorderDialog(self)
            dialog.show()
            dialog.raise_()
            dialog.activateWindow()
            if dialog.exec_() == 0:
                return

            # build parameters
            kwargs = {}
            if str(dialog.edt_name.text()) != '':
                val = str(dialog.edt_name.text())
                kwargs.update(name=val)
            if str(dialog.edt_position.text()) != '':
                val = map(float, str(dialog.edt_position.text()).split(' '))
                kwargs.update(position=val)
            if str(dialog.edt_orientation.text()) != '':
                val = map(float, str(dialog.edt_orientation.text()).split(' '))
                kwargs.update(orientation=val)
            if str(dialog.edt_snr.text()) != '':
                val = float(dialog.edt_snr.text())
                kwargs.update(snr=val)

            # build recorder
            rval = self._sim.register_recorder(**kwargs)
            self.scene_build_model()
            QtGui.QMessageBox.information(
                self,
                'Recorder added',
                'Recorder: %s\n\nCalled with:\n%s' % (rval, kwargs)
            )

        except:
            self.error_dialog()

    @QtCore.pyqtSlot()
    def scene_load(self):

        try:

            rval = str(QtGui.QFileDialog.getOpenFileName(self))
            if rval == '' or rval == 'None' or rval is None:
                return
            self._sim.scene_config_load(rval)
            self.scene_build_model()

        except:
            self.error_dialog()

    @QtCore.pyqtSlot()
    def scene_save(self):

        try:

            rval = str(QtGui.QFileDialog.getSaveFileName(self))
            if rval == '' or rval == 'None' or rval is None:
                return
            self._sim.scene_config_save(rval)

        except:
            self.error_dialog()

    @QtCore.pyqtSlot()
    def scene_remove(self):

        try:

            # get model index
            try:
                idx = self.tre_scene.selectedIndexes()[0]
                sel_node = self._scene_model.itemFromIndex(idx)
            except:
                return

            # find corret parent node
            rm_node = None
            if sel_node.type() in [1001, 1002]:
                rm_node = sel_node
            else:
                if sel_node.parent() is not None:
                    if sel_node.parent().type() in [1001, 1002]:
                        rm_node = sel_node.parent()
            if rm_node is None:
                return

            # find neuron for node
            for key, obj in self._sim.items():
                if obj.name == str(rm_node.child(0, 1).text()):
                    break

            # remove
            if self._sim.remove_object(key) is False:
                raise ValueError('deletion was not successfull :(')
            self.scene_build_model()

        except:
            self.error_dialog()

    @QtCore.pyqtSlot()
    def scene_build_model(self):

        try:

            # sim
            self._trn_sim.removeRows(0, self._trn_sim.rowCount())
            self._trn_sim.appendRow([
                QtGui.QStandardItem('Name'),
                QtGui.QStandardItem(str(self._sim))
            ])
            self._trn_sim.appendRow([
                QtGui.QStandardItem('Sample Rate'),
                QtGui.QStandardItem(str(self._sim.sample_rate))
            ])
            self._trn_sim.appendRow([
                QtGui.QStandardItem('Current Frame'),
                QtGui.QStandardItem(str(self._sim.frame))
            ])
            self._trn_sim.appendRow([
                QtGui.QStandardItem('Frame Size'),
                QtGui.QStandardItem(str(self._sim.frame_size))
            ])
            dbg = QtGui.QStandardItem('#DEBUG#')
            for k in self._sim.__dict__.keys():
                dbg.appendRow([
                    QtGui.QStandardItem(str(k)),
                    QtGui.QStandardItem(str(self._sim.__dict__[k]))
                ])
            self._trn_sim.appendRow(dbg)
            # TODO: more usefull infos from sim?!

            # neuron data cache
            self._trn_ndata.removeRows(0, self._trn_ndata.rowCount())
            for k in self._sim.neuron_data.keys():
                ndata_node = QtGui.QStandardItem(str(k))
                ndata = self._sim.neuron_data[k]
                dbg = QtGui.QStandardItem('#DEBUG#')
                for key, value in ndata.__dict__.items():
                    dbg.appendRow([
                        QtGui.QStandardItem(str(key)),
                        QtGui.QStandardItem(str(value))
                    ])
                ndata_node.appendRow(dbg)
                self._trn_ndata.appendRow(ndata_node)

            # neurons
            self._trn_nrn.removeRows(0, self._trn_nrn.rowCount())
            for nrn_key in self._sim.neuron_keys:

                n = self._sim[nrn_key]
                nrn = NeuronNode(str(n))
                self._trn_nrn.appendRow(nrn)
                nrn.appendRow([
                    QtGui.QStandardItem('Name'),
                    QtGui.QStandardItem(str(n.name))
                ])
                nrn.appendRow([
                    QtGui.QStandardItem('Ident'),
                    QtGui.QStandardItem(str(nrn_key))
                ])
                nrn.appendRow([
                    QtGui.QStandardItem('Position'),
                    QtGui.QStandardItem(str(n.position))
                ])
                nrn.appendRow([
                    QtGui.QStandardItem('Orientation'),
                    QtGui.QStandardItem(str(n.orientation))
                ])
                nrn.appendRow([
                    QtGui.QStandardItem('Rate of Fire'),
                    QtGui.QStandardItem(str(n.rate_of_fire))
                ])
                nrn.appendRow([
                    QtGui.QStandardItem('Amplitude'),
                    QtGui.QStandardItem(str(n.amplitude))
                ])
                nrn.appendRow([
                    QtGui.QStandardItem('Active'),
                    QtGui.QStandardItem(str(n.active))
                ])
                dbg = QtGui.QStandardItem('#DEBUG#')
                for k in n.__dict__.keys():
                    dbg.appendRow([
                        QtGui.QStandardItem(str(k)),
                        QtGui.QStandardItem(str(n.__dict__[k]))
                    ])
                nrn.appendRow(dbg)

            # recorders
            self._trn_rec.removeRows(0, self._trn_rec.rowCount())
            for rec_key in self._sim.recorder_keys:

                r = self._sim[rec_key]
                rec = RecorderNode(str(r))
                self._trn_rec.appendRow(rec)
                rec.appendRow([
                    QtGui.QStandardItem('Name'),
                    QtGui.QStandardItem(str(r.name))
                ])
                rec.appendRow([
                    QtGui.QStandardItem('Ident'),
                    QtGui.QStandardItem(str(rec_key))
                ])
                rec.appendRow([
                    QtGui.QStandardItem('Position'),
                    QtGui.QStandardItem(str(r.position))
                ])
                rec.appendRow([
                    QtGui.QStandardItem('Orientation'),
                    QtGui.QStandardItem(str(r.orientation))
                ])
                rec.appendRow([
                    QtGui.QStandardItem('Active'),
                    QtGui.QStandardItem(str(r.active))
                ])
                rec.appendRow([
                    QtGui.QStandardItem('Points'),
                    QtGui.QStandardItem(str(r.points))
                ])
                dbg = QtGui.QStandardItem('#DEBUG#')
                for k in r.__dict__.keys():
                    dbg.appendRow([
                        QtGui.QStandardItem(str(k)),
                        QtGui.QStandardItem(str(r.__dict__[k]))
                    ])
                rec.appendRow(dbg)

        except:
            self.error_dialog()

    ## output dock slots

    @QtCore.pyqtSlot()
    def io_restart(self):

        try:

            self._sim.io_man.initialize()
            self.io_build_model()

        except:
            self.error_dialog()

    @QtCore.pyqtSlot()
    def io_build_model(self):

        try:

            self._io_model.clear()
            self._io_model.setHorizontalHeaderLabels(['Name', 'Value'])
            dbg = QtGui.QStandardItem('#DEBUG#')
            for k, v in self._sim.io_man.__dict__.items():
                dbg.appendRow([
                    QtGui.QStandardItem(str(k)),
                    QtGui.QStandardItem(str(v))
                ])
            self._io_model.appendRow(dbg)

        except:
            self.error_dialog()

    ## dialog spawners

    @QtCore.pyqtSlot()
    def on_about(self):
        QtGui.QMessageBox.about(
            self,
            'About Neural Simulation',
            """
            NEURAL SIMULATION

            (c) 2010 Philipp Meier

            Berlin Institute of Technology
            School for Electrical Engineering and Computer Science
            Neural Information Processing Group

            GNU Public License v3

            Software and source code available on request:
            pmeier82 [at] googlemail [dot] com
            """
        )

    @QtCore.pyqtSlot()
    def on_about_qt(self):

        QtGui.QMessageBox.aboutQt(self)

    @QtCore.pyqtSlot()
    def comming_soon(self):

        QtGui.QMessageBox.information(
            self,
            'Ooouuups..',
            'Coming soon..\n..promissed :-)'
        )

    def error_dialog(self):
        try:
            from debug_helpers import print_top_100
            print_top_100()
            ei = sys.exc_info()

            QtGui.QMessageBox.critical(
                self,
                'EXCEPTION',
                '\n'.join(traceback.format_exception(*ei))
            )
        finally:
            del ei
            sys.exc_clear()

    ## events

    def closeEvent(self, evt):

        if self._timer.isActive():
            self.on_input_cmdpnl_timer()
        self.on_append_log('')
        self.on_append_log('..shutting down!')
        self._sim.finalize()
        QtGui.QMessageBox.information(
            self,
            'Shutdown',
            'Shutdown was successful'
        )

    ## methods private

    def _set_enabled(self, toggle=True):

        # gui elements to toggle in a list
        gui_list = [
            self.gb_steps,
            self.edt_timer,
            self.cb_frame_size,
            self.cb_sample_rate
        ]
        gui_list.extend(self.findChildren(QtGui.QDockWidget))

        # set enabled state for components
        for gui_item in gui_list:
            try:
                gui_item.setEnabled(toggle)
            except:
                pass


## sim-ui dialogs

class AddNeuronDialog(QtGui.QDialog, Ui_AddNeuronDialog):

    def __init__(self, parent=None, ndata={}):

        super(AddNeuronDialog, self).__init__(parent)
        self.setupUi(self)
        self.populate_cb_data(ndata)

    @QtCore.pyqtSlot()
    def populate_cb_data(self, ndata):
        self.cb_data.clear()
        for item in ndata.keys():
            self.cb_data.addItem(str(item))


class AddRecorderDialog(QtGui.QDialog, Ui_AddRecorderDialog):

    def __init__(self, parent=None):

        super(AddRecorderDialog, self).__init__(parent)
        self.setupUi(self)


## sim-ui elements

class NeuronNode(QtGui.QStandardItem):
    def type(self):
        return QtGui.QStandardItem.UserType + 1


class RecorderNode(QtGui.QStandardItem):
    def type(self):
        return QtGui.QStandardItem.UserType + 2


##---MAIN

def main(args):

    app = QtGui.QApplication(args)
#    app.lastWindowClosed.connect(app.quit)

    win = SimulationGui()
    win.show()

    return app.exec_()

if __name__ == '__main__':

    import sys
    sys.exit(main(sys.argv))
