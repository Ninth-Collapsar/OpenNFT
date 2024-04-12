# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plugins.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dlgPlugins(object):
    def setupUi(self, dlgPlugins):
        dlgPlugins.setObjectName("dlgPlugins")
        dlgPlugins.resize(360, 211)
        self.btnPlugins = QtWidgets.QDialogButtonBox(dlgPlugins)
        self.btnPlugins.setGeometry(QtCore.QRect(270, 10, 81, 191))
        self.btnPlugins.setOrientation(QtCore.Qt.Vertical)
        self.btnPlugins.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.btnPlugins.setObjectName("btnPlugins")
        self.lvPlugins = QtWidgets.QListView(dlgPlugins)
        self.lvPlugins.setGeometry(QtCore.QRect(10, 10, 256, 192))
        self.lvPlugins.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.lvPlugins.setObjectName("lvPlugins")

        self.retranslateUi(dlgPlugins)
        self.btnPlugins.accepted.connect(dlgPlugins.accept)
        self.btnPlugins.rejected.connect(dlgPlugins.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgPlugins)

    def retranslateUi(self, dlgPlugins):
        _translate = QtCore.QCoreApplication.translate
        dlgPlugins.setWindowTitle(_translate("dlgPlugins", "Dialog"))

