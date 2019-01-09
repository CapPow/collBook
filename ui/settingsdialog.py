#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 10:33:55 2019

@author: Caleb Powell

"""
#from PyQt5 import Qt
#from PyQt5 import QtCore
#from PyQt5.QtCore import QAbstractTableModel
#from PyQt5.QtCore import QDir
#from PyQt5.QtCore import QStringListModel
#from PyQt5.QtCore import QVariant
#from PyQt5.QtGui import QColor
#from PyQt5.QtGui import QIcon
#from PyQt5.QtWidgets import QFileSystemModel

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QSettings

from ui.settingsUI import Ui_settingsWindow

class settingsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        w = Ui_settingsWindow()
        w.setupUi(self)
        self.settings = QSettings('settings.ini', QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)    # File only, no fallback to registry or or.
        
        w.button_SaveExit.clicked.connect(self.saveSettings)
        w.button_Cancel.clicked.connect(self.hide)
        self.readSettings(w)
        
        w.value_AuthChangePolicy
        
        
    def saveSettings(self):
        print('SAVING')
    
    def readSettings(self, parent):
        
        #QComboBox
        value_AuthChangePolicy = parent.value_AuthChangePolicy.currentText()
        value_NameChangePolicy = parent.value_NameChangePolicy.currentText()
        value_TaxAlignSource = parent.value_TaxAlignSource.currentText()
        
        print(value_TaxAlignSource)
        
        #QLineEdit
        value_VerifiedBy = parent.value_VerifiedBy.text()
        print(value_VerifiedBy)
        
        #QPlainTextEdit        
        value_CollectionName = parent.value_CollectionName.toPlainText()
        print(value_CollectionName)
        
        #QCheckBox
        value_inc_Associated = parent.value_inc_Associated.isChecked()
        value_inc_Barcode = parent.value_inc_Barcode.isChecked()
        value_inc_CollectionName = parent.value_inc_CollectionName.isChecked()
        value_inc_VerifiedBy = parent.value_inc_VerifiedBy.isChecked()
        print(value_inc_CollectionName)
        
        #QSpinBox
        value_X = parent.value_X.value()
        value_Y = parent.value_Y.value()
        print(value_X)

        
        
        
        
