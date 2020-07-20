# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/aboutdialogUI.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(739, 583)
        font = QtGui.QFont()
        font.setFamily("Cantarell Thin")
        font.setPointSize(12)
        Dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/rc_/logo-collbook/logomark.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setAutoFillBackground(False)
        Dialog.setStyleSheet("")
        Dialog.setSizeGripEnabled(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_logo = QtWidgets.QFrame(Dialog)
        self.frame_logo.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_logo.sizePolicy().hasHeightForWidth())
        self.frame_logo.setSizePolicy(sizePolicy)
        self.frame_logo.setMinimumSize(QtCore.QSize(674, 230))
        self.frame_logo.setStyleSheet("border-image: url(:/rc_/logo-collbook/horizontal.png) 0 0 0 0 stretch stretch;\n"
"border-width: 0px;\n"
"\n"
"")
        self.frame_logo.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_logo.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_logo.setLineWidth(0)
        self.frame_logo.setObjectName("frame_logo")
        self.verticalLayout.addWidget(self.frame_logo, 0, QtCore.Qt.AlignHCenter)
        self.label_collBookVersion = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setFamily("Cantarell Light")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label_collBookVersion.setFont(font)
        self.label_collBookVersion.setAlignment(QtCore.Qt.AlignCenter)
        self.label_collBookVersion.setObjectName("label_collBookVersion")
        self.verticalLayout.addWidget(self.label_collBookVersion)
        self.label = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setFamily("Cantarell Thin")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pushButton_Close = QtWidgets.QPushButton(Dialog)
        self.pushButton_Close.setObjectName("pushButton_Close")
        self.horizontalLayout.addWidget(self.pushButton_Close)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        self.pushButton_Close.clicked.connect(Dialog.close)
        self.pushButton.clicked.connect(Dialog.showLicense)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "About collBook"))
        self.label_collBookVersion.setText(_translate("Dialog", "Version: "))
        self.label.setText(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Cantarell Thin\',\'Cantarell Thin\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Developed by: <br />Caleb Powell and Jacob Motley</span></p>\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">logo by:<br />Zularizal</span></p>\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://github.com/CapPow/collBook\"><span style=\" text-decoration: underline; color:#2980b9;\">view source code</span></a></p>\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Please cite collNotes and collBook using <a href=\"https://doi.org/10.1002/aps3.11284\"><span style=\" text-decoration: underline; color:#2980b9;\">our paper</span></a> in <span style=\" font-style:italic;\">Applications in Plant Sciences</span>:</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Powell, C., Motley, J., Qin, H., and Shaw, J.. 2019. A born‐digital field‐to‐database solution for collections-based research using collNotes and collBook. <span style=\" font-style:italic;\">Applications in Plant Sciences</span> 7(8):e11284.</p></body></html>"))
        self.pushButton.setText(_translate("Dialog", "License"))
        self.pushButton_Close.setText(_translate("Dialog", "Close"))

import Resources_rc
