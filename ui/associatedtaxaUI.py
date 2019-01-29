# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/associatettaxaUI.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_associatedTaxaMainWindow(object):
    def setupUi(self, associatedTaxaMainWindow):
        associatedTaxaMainWindow.setObjectName("associatedTaxaMainWindow")
        associatedTaxaMainWindow.setWindowModality(QtCore.Qt.NonModal)
        associatedTaxaMainWindow.resize(336, 443)
        self.gridLayout = QtWidgets.QGridLayout(associatedTaxaMainWindow)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget_associatedTaxa = QtWidgets.QListWidget(associatedTaxaMainWindow)
        self.listWidget_associatedTaxa.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listWidget_associatedTaxa.setResizeMode(QtWidgets.QListView.Adjust)
        self.listWidget_associatedTaxa.setObjectName("listWidget_associatedTaxa")
        self.gridLayout.addWidget(self.listWidget_associatedTaxa, 3, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_2 = QtWidgets.QPushButton(associatedTaxaMainWindow)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_3.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(associatedTaxaMainWindow)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_3.addWidget(self.pushButton)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.button_cancel = QtWidgets.QPushButton(associatedTaxaMainWindow)
        self.button_cancel.setObjectName("button_cancel")
        self.horizontalLayout.addWidget(self.button_cancel)
        self.button_save = QtWidgets.QPushButton(associatedTaxaMainWindow)
        self.button_save.setObjectName("button_save")
        self.horizontalLayout.addWidget(self.button_save)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit_newAssociatedTaxa = QtWidgets.QLineEdit(associatedTaxaMainWindow)
        self.lineEdit_newAssociatedTaxa.setObjectName("lineEdit_newAssociatedTaxa")
        self.horizontalLayout_2.addWidget(self.lineEdit_newAssociatedTaxa)
        self.buttonAdd = QtWidgets.QPushButton(associatedTaxaMainWindow)
        self.buttonAdd.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/rc_/plus-square.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonAdd.setIcon(icon)
        self.buttonAdd.setObjectName("buttonAdd")
        self.horizontalLayout_2.addWidget(self.buttonAdd)
        self.gridLayout.addLayout(self.horizontalLayout_2, 4, 0, 1, 1)
        self.label_UserMsg = QtWidgets.QLabel(associatedTaxaMainWindow)
        self.label_UserMsg.setObjectName("label_UserMsg")
        self.gridLayout.addWidget(self.label_UserMsg, 0, 0, 1, 1)
        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(3, 7)

        self.retranslateUi(associatedTaxaMainWindow)
        self.buttonAdd.clicked.connect(associatedTaxaMainWindow.addAssociatedTaxa)
        self.button_save.clicked.connect(associatedTaxaMainWindow.saveAssociatedTaxa)
        self.button_cancel.clicked.connect(associatedTaxaMainWindow.hide)
        self.pushButton_2.clicked.connect(associatedTaxaMainWindow.selectNone)
        self.pushButton.clicked.connect(associatedTaxaMainWindow.selectAll)
        QtCore.QMetaObject.connectSlotsByName(associatedTaxaMainWindow)

    def retranslateUi(self, associatedTaxaMainWindow):
        _translate = QtCore.QCoreApplication.translate
        associatedTaxaMainWindow.setWindowTitle(_translate("associatedTaxaMainWindow", "Associated Taxa"))
        self.listWidget_associatedTaxa.setSortingEnabled(True)
        self.pushButton_2.setText(_translate("associatedTaxaMainWindow", "select none"))
        self.pushButton.setText(_translate("associatedTaxaMainWindow", "select all"))
        self.button_cancel.setText(_translate("associatedTaxaMainWindow", "Cancel"))
        self.button_save.setText(_translate("associatedTaxaMainWindow", "Save"))
        self.label_UserMsg.setText(_translate("associatedTaxaMainWindow", "Select associated taxa."))

import Resources_rc
