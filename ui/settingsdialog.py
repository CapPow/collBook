#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 10:33:55 2019

@author: Caleb Powell

"""
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication

from ui.settingsUI import Ui_settingsWindow

class settingsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.init_ui(parent)
        #TODO add a consideration for if the config file has never been created... fill in default values
        # can use the get() argument for alt values and just code it into the populateSettings() function
           
    def init_ui(self, parent):
        self.parent = parent # this is the master window
        settingsWindow = Ui_settingsWindow()
        settingsWindow.setupUi(self)
        self.settingsWindow = settingsWindow
        self.settings = QSettings()        
        # TODO fix the settings file being saved to " test1.py.conf " and ignoring the organization and application inputs
        #QApplication.setOrganizationName('Powell')
        QCoreApplication.setOrganizationName("pdProject");
        #QApplication.setOrganizationDomain()
        QApplication.setApplicationName('pdDesk')
        self.settingsWindow.value_CollectionName.setPlainText(self.get('value_CollectionName'))
        #QApplication.setApplicationVersion()
        self.settings.setFallbacksEnabled(False)    # File only, no fallback to registry or or.
        self.populateSettings()
        self.settingsWindow.button_SaveExit.clicked.connect(self.saveButtonClicked)
        self.settingsWindow.button_Cancel.clicked.connect(self.cancelButtonClicked)

    def saveButtonClicked(self):
        """ hides the preferences window and saves the user entries """
        self.saveSettings()
        # force pdf_preview window to resize ui elements.
        self.parent.pdf_preview.initViewer(self.parent)
        self.parent.updatePreview()
        self.parent.updateAutoComplete()
        self.hide()
    
    def cancelButtonClicked(self):
        """ hides the preferences window and resets user entries to last
        known good saved values """
        self.hide()
        self.populateSettings()
        
    def has(self, key):
        return self.settings.contains(key)

    def setValue(self, key, value):
        return self.settings.setValue(key, value)

    def get(self, key, altValue = ""):
        result = self.settings.value(key, altValue)
        if result == 'true':
            result = True
        elif result == 'false':
            result = False
        return result
    
    def populateQComboBoxSettings(self, obj, value):
        """ sets a QComboBox based on a string value. Presumed to be a more
        durable method. obj is the qComboBox object, and value is a string
        to search for"""
        index = obj.findText(value)
        obj.setCurrentIndex(index)
    
    def convertCheckState(self, stringState):
        """ given a string either "true" or "false" returns the proper Qt.CheckState"""
        if str(stringState).lower() != 'true':
            return Qt.Unchecked
        else:
            return Qt.Checked
    
    def kingdomChanged(self, QString):
        """ called when value_Kingdom changes text. Calls populateSources, and 
        """
        self.populateSources(QString)
    
    def populateSources(self, QString):
        """ called when value_Kingdom changes text. Decides what the options
        should be for value_TaxAlignSource (taxanomic alignment source)."""

        kingdom = QString
        source = self.settingsWindow.value_TaxAlignSource
        sourceValue = source.currentText()  # save initial selection
        source.clear()  # clear existing options
        # conditionally build a list of those which to add.
        # NOTE: keeping Local options in index 0 position
        if kingdom == 'Plantae':
            toAdd = ['ITIS (local)', 'Catalog of Life (web API)', 'ITIS (web API)', 'Taxonomic Name Resolution Service (web API)']
        elif kingdom == 'Fungi':
            toAdd = ['MycoBank (local)', 'Catalog of Life (web API)', 'MycoBank (web API)']
        source.addItems(toAdd)
        newIndex = source.findText(sourceValue) # look for new index of initial selection
        if newIndex == -1:  # if it is no longer in the list
            newIndex = 0  # , settle for index 0 (the local option)
        source.setCurrentIndex(newIndex)  # set the selection after the population change.

    def toggleTNRSSettings(self, QString):
        """ called when value_TaxAlignSource changes text. Decides if the 
        groupbox_TNRS should be enabled or not"""
        if str(QString) == 'Taxonomic Name Resolution Service (web API)':
            b = True
        else:
            b = False    
        self.settingsWindow.groupbox_TNRS.setEnabled(b)

    def populateSettings(self):
        """ uses self.settings to populate the preferences widget's selections"""
        parent = self.settingsWindow

        #QComboBox
        value_AuthChangePolicy = self.get('value_AuthChangePolicy', 'Fill blanks')
        self.populateQComboBoxSettings( parent.value_AuthChangePolicy, value_AuthChangePolicy)        
        value_NameChangePolicy = self.get('value_NameChangePolicy', 'Always ask')
        self.populateQComboBoxSettings( parent.value_NameChangePolicy, value_NameChangePolicy)
        value_TaxAlignSource = self.get('value_TaxAlignSource', 'ITIS (local)')
        self.populateQComboBoxSettings( parent.value_TaxAlignSource, value_TaxAlignSource)
        value_Kingdom = self.get('value_Kingdom', 'Plantae')
        self.populateQComboBoxSettings( parent.value_Kingdom, value_Kingdom)
        
        #QLineEdit  .setText
        value_VerifiedBy = self.get('value_VerifiedBy')
        parent.value_VerifiedBy.setText(value_VerifiedBy)

        #QPlainTextEdit .setPlainText        
        value_CollectionName = self.get('value_CollectionName')
        parent.value_CollectionName.setPlainText(value_CollectionName)
        
        #QCheckBox .checkStateSet
        value_inc_Associated = self.convertCheckState(self.get('value_inc_Associated'))
        parent.value_inc_Associated.setCheckState(value_inc_Associated)
        value_inc_Barcode =  self.convertCheckState(self.get('value_inc_Barcode'))
        parent.value_inc_Barcode.setCheckState(value_inc_Barcode)
        value_inc_CollectionName =  self.convertCheckState(self.get('value_inc_CollectionName'))
        parent.value_inc_CollectionName.setCheckState(value_inc_CollectionName)
        value_inc_VerifiedBy =  self.convertCheckState(self.get('value_inc_VerifiedBy'))
        parent.value_inc_VerifiedBy.setCheckState(value_inc_VerifiedBy)
        
        #QSpinBox .setValue
        value_X = int(self.get('value_X', 140))
        parent.value_X.setValue(value_X)
        value_Y = int(self.get('value_Y', 90))
        parent.value_Y.setValue(value_Y)
        value_RelFont = int(self.get('value_RelFont',12))
        parent.value_RelFont.setValue(value_RelFont)
        value_TNRS_Threshold = int(self.get('value_TNRS_Threshold', 85))
        parent.value_TNRS_Threshold.setValue(value_TNRS_Threshold)
    
    def saveSettings(self):
        """ stores the preferences widget's selections to self.settings"""
        parent = self.settingsWindow
        
        #QComboBox
        value_AuthChangePolicy = parent.value_AuthChangePolicy.currentText()
        self.setValue('value_AuthChangePolicy',value_AuthChangePolicy)
        value_NameChangePolicy = parent.value_NameChangePolicy.currentText()
        self.setValue('value_NameChangePolicy',value_NameChangePolicy)
        value_TaxAlignSource = parent.value_TaxAlignSource.currentText()
        self.setValue('value_TaxAlignSource', value_TaxAlignSource)
        value_Kingdom = parent.value_Kingdom.currentText()
        self.setValue('value_Kingdom', value_Kingdom)

        #QLineEdit
        value_VerifiedBy = parent.value_VerifiedBy.text()
        self.setValue('value_VerifiedBy',value_VerifiedBy)

        #QPlainTextEdit        
        value_CollectionName = parent.value_CollectionName.toPlainText()
        self.setValue('value_CollectionName', value_CollectionName)
        
        #QCheckBox
        value_inc_Associated = parent.value_inc_Associated.isChecked()
        self.setValue('value_inc_Associated',value_inc_Associated)
        value_inc_Barcode = parent.value_inc_Barcode.isChecked()
        self.setValue('value_inc_Barcode',value_inc_Barcode)
        value_inc_CollectionName = parent.value_inc_CollectionName.isChecked()
        self.setValue('value_inc_CollectionName',value_inc_CollectionName)
        value_inc_VerifiedBy = parent.value_inc_VerifiedBy.isChecked()
        self.setValue('value_inc_VerifiedBy',value_inc_VerifiedBy)
        
        #QSpinBox
        value_X = parent.value_X.value()
        self.setValue('value_X',value_X)
        value_Y = parent.value_Y.value()
        self.setValue('value_Y',value_Y)
        value_RelFont = parent.value_RelFont.value()
        self.setValue('value_RelFont', value_RelFont)
        value_TNRS_Threshold = parent.value_TNRS_Threshold.value()
        self.setValue('value_TNRS_Threshold', value_TNRS_Threshold)       
        
