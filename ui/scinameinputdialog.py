#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 00:42:21 2019

@author: john
"""

from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QGridLayout, QLabel, QLineEdit, QStyle,
    QWidget, QCompleter)
from PyQt5.QtWidgets import QApplication

from ui.scinameinputdialogUI import Ui_Dialog

class sciNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.init_ui(parent)    
        #TODO add a consideration for if the config file has never been created... fill in default values
        # can use the get() argument for alt values and just code it into the populateSettings() function
    def init_ui(self, parent):
        self.parent = parent # this is the master window
        dlg = Ui_Dialog()
        dlg.setupUi(self)
        dlg.lineEdit.setFocus(True)        
        self.dlg = dlg
        self.btn = self.dlg.buttonBox.button(QDialogButtonBox.Yes) 
        self.dlg.buttonBox.button(QDialogButtonBox.No).setAutoDefault(False)
        self.btn.setEnabled(False)
        self.dlg.lineEdit.textChanged.connect(self.enableYesBox)

    def enableYesBox(self, userInput):
        """ connected to editingFinished on lineEdit """
        if len(userInput) > 4:
            self.btn.setEnabled(True)
            self.btn.setDefault(True)
        
    def textBox(self, wordList, message = "", title = "", ):
        if title != '':
            self.setWindowTitle(title)
        self.dlg.label.setText(message)
        dlgCompleter = QCompleter(wordList, self.dlg.lineEdit)
        self.dlg.lineEdit.setCompleter(dlgCompleter)
        answer = self.exec_()
        if answer:
            result = self.dlg.lineEdit.text()
            return result