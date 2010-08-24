# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'recorder_controll.ui'
#
# Created: Fri Aug 20 19:51:36 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui, Qwt5

class Ui_RecorderControll(object):
    def setupUi(self, RecorderControll):
        RecorderControll.setObjectName("RecorderControll")
        RecorderControll.resize(414, 82)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/neural_sim_client.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        RecorderControll.setWindowIcon(icon)
        self.lo_main = QtGui.QVBoxLayout(RecorderControll)
        self.lo_main.setObjectName("lo_main")
        self.lo_controls = QtGui.QHBoxLayout()
        self.lo_controls.setObjectName("lo_controls")
        self.ctl_input_position = Qwt5.QwtCounter(RecorderControll)
        self.ctl_input_position.setMinimumSize(QtCore.QSize(165, 0))
        self.ctl_input_position.setNumButtons(3)
        self.ctl_input_position.setProperty("basicstep", 5.0)
        self.ctl_input_position.setMaxValue(1000.0)
        self.ctl_input_position.setStepButton2(2)
        self.ctl_input_position.setStepButton3(5)
        self.ctl_input_position.setEditable(True)
        self.ctl_input_position.setObjectName("ctl_input_position")
        self.lo_controls.addWidget(self.ctl_input_position)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.lo_controls.addItem(spacerItem)
        self.ctl_btn_move = QtGui.QPushButton(RecorderControll)
        self.ctl_btn_move.setObjectName("ctl_btn_move")
        self.lo_controls.addWidget(self.ctl_btn_move)
        self.ctl_btn_request = QtGui.QPushButton(RecorderControll)
        self.ctl_btn_request.setObjectName("ctl_btn_request")
        self.lo_controls.addWidget(self.ctl_btn_request)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.lo_controls.addItem(spacerItem1)
        self.lo_main.addLayout(self.lo_controls)
        self.lo_display = QtGui.QHBoxLayout()
        self.lo_display.setObjectName("lo_display")
        self.disp_lcd = QtGui.QLCDNumber(RecorderControll)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.disp_lcd.sizePolicy().hasHeightForWidth())
        self.disp_lcd.setSizePolicy(sizePolicy)
        self.disp_lcd.setMinimumSize(QtCore.QSize(100, 30))
        self.disp_lcd.setFrameShape(QtGui.QFrame.StyledPanel)
        self.disp_lcd.setFrameShadow(QtGui.QFrame.Sunken)
        self.disp_lcd.setLineWidth(3)
        self.disp_lcd.setMidLineWidth(3)
        self.disp_lcd.setSmallDecimalPoint(False)
        self.disp_lcd.setNumDigits(7)
        self.disp_lcd.setMode(QtGui.QLCDNumber.Dec)
        self.disp_lcd.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.disp_lcd.setProperty("value", 0.0)
        self.disp_lcd.setProperty("intValue", 0)
        self.disp_lcd.setObjectName("disp_lcd")
        self.lo_display.addWidget(self.disp_lcd)
        self.disp_meter = Qwt5.QwtThermo(RecorderControll)
        self.disp_meter.setMinimumSize(QtCore.QSize(300, 30))
        self.disp_meter.setScalePosition(Qwt5.QwtThermo.BottomScale)
        self.disp_meter.setFillColor(QtGui.QColor(0, 170, 0))
        self.disp_meter.setMaxValue(1000.0)
        self.disp_meter.setProperty("value", 500.0)
        self.disp_meter.setObjectName("disp_meter")
        self.lo_display.addWidget(self.disp_meter)
        self.lo_main.addLayout(self.lo_display)

        self.retranslateUi(RecorderControll)
        QtCore.QMetaObject.connectSlotsByName(RecorderControll)

    def retranslateUi(self, RecorderControll):
        RecorderControll.setWindowTitle(QtGui.QApplication.translate("RecorderControll", "Recorder Controll", None, QtGui.QApplication.UnicodeUTF8))
        self.ctl_btn_move.setText(QtGui.QApplication.translate("RecorderControll", "move", None, QtGui.QApplication.UnicodeUTF8))
        self.ctl_btn_request.setText(QtGui.QApplication.translate("RecorderControll", "?", None, QtGui.QApplication.UnicodeUTF8))

import res_rc
