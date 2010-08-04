# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'init_dialog.ui'
#
# Created: Wed Aug  4 19:41:47 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_InitDialog(object):
    def setupUi(self, InitDialog):
        InitDialog.setObjectName("InitDialog")
        InitDialog.resize(426, 231)
        InitDialog.setMinimumSize(QtCore.QSize(100, 100))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/neural_sim_client.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        InitDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(InitDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.stackedWidget = QtGui.QStackedWidget(InitDialog)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtGui.QWidget()
        self.page.setObjectName("page")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName("page_2")
        self.stackedWidget.addWidget(self.page_2)
        self.verticalLayout.addWidget(self.stackedWidget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.main_list = QtGui.QListWidget(InitDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.main_list.sizePolicy().hasHeightForWidth())
        self.main_list.setSizePolicy(sizePolicy)
        self.main_list.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.main_list.setProperty("showDropIndicator", False)
        self.main_list.setAlternatingRowColors(True)
        self.main_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.main_list.setObjectName("main_list")
        self.horizontalLayout.addWidget(self.main_list)
        self.grpbox_include = QtGui.QGroupBox(InitDialog)
        self.grpbox_include.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.grpbox_include.setObjectName("grpbox_include")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.grpbox_include)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.check_noise = QtGui.QCheckBox(self.grpbox_include)
        self.check_noise.setObjectName("check_noise")
        self.verticalLayout_2.addWidget(self.check_noise)
        self.check_waveform = QtGui.QCheckBox(self.grpbox_include)
        self.check_waveform.setObjectName("check_waveform")
        self.verticalLayout_2.addWidget(self.check_waveform)
        self.check_groundtruth = QtGui.QCheckBox(self.grpbox_include)
        self.check_groundtruth.setObjectName("check_groundtruth")
        self.verticalLayout_2.addWidget(self.check_groundtruth)
        self.check_positions = QtGui.QCheckBox(self.grpbox_include)
        self.check_positions.setObjectName("check_positions")
        self.verticalLayout_2.addWidget(self.check_positions)
        self.check_all = QtGui.QCheckBox(self.grpbox_include)
        self.check_all.setObjectName("check_all")
        self.verticalLayout_2.addWidget(self.check_all)
        self.horizontalLayout.addWidget(self.grpbox_include)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(InitDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Abort | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(InitDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), InitDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), InitDialog.reject)
        QtCore.QObject.connect(self.check_all, QtCore.SIGNAL("clicked(bool)"), self.check_positions.setChecked)
        QtCore.QObject.connect(self.check_all, QtCore.SIGNAL("clicked(bool)"), self.check_groundtruth.setChecked)
        QtCore.QObject.connect(self.check_all, QtCore.SIGNAL("clicked(bool)"), self.check_waveform.setChecked)
        QtCore.QObject.connect(self.check_all, QtCore.SIGNAL("clicked(bool)"), self.check_noise.setChecked)
        QtCore.QMetaObject.connectSlotsByName(InitDialog)

    def retranslateUi(self, InitDialog):
        InitDialog.setWindowTitle(QtGui.QApplication.translate("InitDialog", "Initialization", None, QtGui.QApplication.UnicodeUTF8))
        self.main_list.setSortingEnabled(True)
        self.grpbox_include.setTitle(QtGui.QApplication.translate("InitDialog", "Interest Declaration", None, QtGui.QApplication.UnicodeUTF8))
        self.check_noise.setText(QtGui.QApplication.translate("InitDialog", "noise", None, QtGui.QApplication.UnicodeUTF8))
        self.check_waveform.setText(QtGui.QApplication.translate("InitDialog", "waveforms", None, QtGui.QApplication.UnicodeUTF8))
        self.check_groundtruth.setText(QtGui.QApplication.translate("InitDialog", "groundtruth", None, QtGui.QApplication.UnicodeUTF8))
        self.check_positions.setText(QtGui.QApplication.translate("InitDialog", "positions", None, QtGui.QApplication.UnicodeUTF8))
        self.check_all.setText(QtGui.QApplication.translate("InitDialog", "CHECK ALL", None, QtGui.QApplication.UnicodeUTF8))

import res_rc
