#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 18:27:51 2019

@author: Caleb Powell
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QHBoxLayout
import Resources_rc

class progressBar(QWidget):

    def initProgressBar(self, parent=None):
        self.parent = parent
        self.label_status = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_status.sizePolicy().hasHeightForWidth())
        self.label_status.setSizePolicy(sizePolicy)
        self.label_status.setMinimumSize(QtCore.QSize(0, 15))
        self.label_status.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_status.setObjectName("label_status")
    
        self.progressBar = QtWidgets.QProgressBar(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setMinimumSize(QtCore.QSize(0, 15))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
    
        
        #self.pushButton_Cancel = QtWidgets.QPushButton(self)
        self.pushButton_Cancel = QtWidgets.QToolButton(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_Cancel.sizePolicy().hasHeightForWidth())
        self.pushButton_Cancel.setSizePolicy(sizePolicy)
        self.pushButton_Cancel.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/rc_/x-circle.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_Cancel.setIcon(icon)
        self.pushButton_Cancel.setIconSize(QtCore.QSize(15, 15))
        #self.pushButton_Cancel.setAutoDefault(False)
        #self.pushButton_Cancel.setDefault(False)
        #self.pushButton_Cancel.setFlat(False)
        self.pushButton_Cancel.setObjectName("pushButton_Cancel")
        self.pushButton_Cancel.setEnabled(False)
        
        self.pushButton_Cancel.status = False
        
        self.pushButton_Cancel.clicked.connect(self.flipCancelSwitch)
        
    
        widgetBox = QWidget(self)
        horizontalLayout = QHBoxLayout()
        horizontalLayout.setContentsMargins(6, 3, 6, 3)
        widgetBox.setLayout(horizontalLayout)
        widgetBox.layout().addWidget(self.label_status)
        widgetBox.layout().addWidget(self.progressBar)
        widgetBox.layout().addWidget(self.pushButton_Cancel)
        
        parent.addWidget(widgetBox, 1)
        parent.setSizeGripEnabled(False)
        
    def flipCancelSwitch(self):
        self.pushButton_Cancel.status = True
        self.progressBar.setProperty("value", 0)
