# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/phil/SVN/Python/SpikePy/sim/gui/add_recorder.ui'
#
# Created: Wed May 26 12:23:13 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AddRecorderDialog(object):
    def setupUi(self, AddRecorderDialog):
        AddRecorderDialog.setObjectName("AddRecorderDialog")
        AddRecorderDialog.resize(182, 147)
        AddRecorderDialog.setModal(True)
        self.lo_vert0 = QtGui.QVBoxLayout(AddRecorderDialog)
        self.lo_vert0.setObjectName("lo_vert0")
        self.lo_form0_2 = QtGui.QFormLayout()
        self.lo_form0_2.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.lo_form0_2.setObjectName("lo_form0_2")
        self.lbl_name = QtGui.QLabel(AddRecorderDialog)
        self.lbl_name.setObjectName("lbl_name")
        self.lo_form0_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.lbl_name)
        self.edt_name = QtGui.QLineEdit(AddRecorderDialog)
        self.edt_name.setObjectName("edt_name")
        self.lo_form0_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.edt_name)
        self.lbl_position = QtGui.QLabel(AddRecorderDialog)
        self.lbl_position.setObjectName("lbl_position")
        self.lo_form0_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.lbl_position)
        self.edt_position = QtGui.QLineEdit(AddRecorderDialog)
        self.edt_position.setText("")
        self.edt_position.setObjectName("edt_position")
        self.lo_form0_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.edt_position)
        self.lbl_orientation = QtGui.QLabel(AddRecorderDialog)
        self.lbl_orientation.setObjectName("lbl_orientation")
        self.lo_form0_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.lbl_orientation)
        self.edt_orientation = QtGui.QLineEdit(AddRecorderDialog)
        self.edt_orientation.setText("")
        self.edt_orientation.setObjectName("edt_orientation")
        self.lo_form0_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.edt_orientation)
        self.lbl_snr = QtGui.QLabel(AddRecorderDialog)
        self.lbl_snr.setToolTip("")
        self.lbl_snr.setObjectName("lbl_snr")
        self.lo_form0_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.lbl_snr)
        self.edt_snr = QtGui.QLineEdit(AddRecorderDialog)
        self.edt_snr.setText("")
        self.edt_snr.setObjectName("edt_snr")
        self.lo_form0_2.setWidget(3, QtGui.QFormLayout.FieldRole, self.edt_snr)
        self.lo_vert0.addLayout(self.lo_form0_2)
        self.bbox_dialog = QtGui.QDialogButtonBox(AddRecorderDialog)
        self.bbox_dialog.setStandardButtons(QtGui.QDialogButtonBox.Abort | QtGui.QDialogButtonBox.Save)
        self.bbox_dialog.setCenterButtons(True)
        self.bbox_dialog.setObjectName("bbox_dialog")
        self.lo_vert0.addWidget(self.bbox_dialog)
        self.lbl_position.setBuddy(self.edt_position)
        self.lbl_orientation.setBuddy(self.edt_orientation)

        self.retranslateUi(AddRecorderDialog)
        QtCore.QObject.connect(self.bbox_dialog, QtCore.SIGNAL("accepted()"), AddRecorderDialog.accept)
        QtCore.QObject.connect(self.bbox_dialog, QtCore.SIGNAL("rejected()"), AddRecorderDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddRecorderDialog)
        AddRecorderDialog.setTabOrder(self.edt_name, self.edt_position)
        AddRecorderDialog.setTabOrder(self.edt_position, self.edt_orientation)
        AddRecorderDialog.setTabOrder(self.edt_orientation, self.edt_snr)
        AddRecorderDialog.setTabOrder(self.edt_snr, self.bbox_dialog)

    def retranslateUi(self, AddRecorderDialog):
        AddRecorderDialog.setWindowTitle(QtGui.QApplication.translate("AddRecorderDialog", "Add Recorder", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_name.setText(QtGui.QApplication.translate("AddRecorderDialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.edt_name.setToolTip(QtGui.QApplication.translate("AddRecorderDialog", "Optional name for the recorder as string. E.g \"Tetrode 13\"", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_position.setText(QtGui.QApplication.translate("AddRecorderDialog", "Position", None, QtGui.QApplication.UnicodeUTF8))
        self.edt_position.setToolTip(QtGui.QApplication.translate("AddRecorderDialog", "Enter the 3-dimensional scene position as a whitespace seperated sequence \"x, y, z\". E.g. \"10.0 15.0 25.666\" (Default= [0, 0, 0])", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_orientation.setText(QtGui.QApplication.translate("AddRecorderDialog", "Orientation", None, QtGui.QApplication.UnicodeUTF8))
        self.edt_orientation.setToolTip(QtGui.QApplication.translate("AddRecorderDialog", "Enter the 3-dimensional orientation vector as a whitespace seperated sequence (x, y, z). The orientation is also the direction of movement for the recorder!!  E.g. \"1.0 0.0 0.0\" (Default=[0,0,1])", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_snr.setText(QtGui.QApplication.translate("AddRecorderDialog", "SNR", None, QtGui.QApplication.UnicodeUTF8))
        self.edt_snr.setToolTip(QtGui.QApplication.translate("AddRecorderDialog", "The SNR (Signal to Noise Ratio) of the recorder. A scaling factor for the noise process as a float. E.g. \"3.0\" (Default=1.0)", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    AddRecorderDialog = QtGui.QDialog()
    ui = Ui_AddRecorderDialog()
    ui.setupUi(AddRecorderDialog)
    AddRecorderDialog.show()
    sys.exit(app.exec_())

