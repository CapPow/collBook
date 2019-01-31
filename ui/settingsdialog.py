#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 10:33:55 2019

@author: Caleb Powell

"""
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication

from ui.settingsUI import Ui_settingsWindow

class settingsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.init_ui(parent)
           
    def init_ui(self, parent):
        self.parent = parent # this is the master window
        settingsWindow = Ui_settingsWindow()
        settingsWindow.setupUi(self)
        self.settingsWindow = settingsWindow
        self.settings = QSettings('collBook', 'collBook')        
        #self.settingsWindow.value_CollectionName.setPlainText(self.get('value_CollectionName'))
        self.settings.setFallbacksEnabled(False)    # File only, no fallback to registry.
        # before we populate them, verify the file exists
        self.populateSettings()
        self.settingsWindow.button_SaveExit.clicked.connect(self.saveButtonClicked)
        self.settingsWindow.button_Cancel.clicked.connect(self.cancelButtonClicked)
        self.settingsWindow.toolButton_GetLogoPath.clicked.connect(self.getLogoPath)
        self.genDummyCatalogNumber()
        # be sure the settings file exists
        if not self.settings.value('version', False):
            self.saveSettings()
        self.setMaxZoom()
        # can also later do a check if the version is not up-to-date

    def setMaxZoom(self):
        screenSize = (self.parent.geometry())
        screenX = screenSize.width()
        xMax = screenX * 0.6
        screenY = screenSize.height()
        yMax = screenY * 0.75
        #  resulting pdfs are 96dpi skip calling getPixmap twice, Assume 96
        #  96dpi / 25.4mm per inch = 3.780 dots per mm
        label_X = int(self.settingsWindow.value_X.value() * (3.780))
        label_Y = int(self.settingsWindow.value_Y.value() * (3.780))
        max_XZoom = xMax / label_X
        max_YZoom = yMax / label_Y
        max_Zoom = int(min(max_XZoom, max_YZoom) * 100)
        self.parent.w.value_zoomLevel.setMaximum(max_Zoom)
        currentZoom = int(self.parent.w.value_zoomLevel.value())
        if currentZoom > max_Zoom:
            valueToSet = (max_Zoom)
        else:
            valueToSet = currentZoom
        self.parent.w.value_zoomLevel.setValue(valueToSet)
        self.parent.w.label_zoomLevel.setText(f'{str(valueToSet).rjust(4," ")}%')  # update the label
            

    def saveButtonClicked(self):
        """ hides the preferences window and saves the user entries """
        # check the new limitations on zoomlevel
        self.setMaxZoom()
        self.saveSettings()
        # force pdf_preview window to resize ui elements.
        self.parent.pdf_preview.initViewer(self.parent)
        self.parent.p.initLogoCanvas()  # build the logo backdrop for labels.
        self.genDummyCatalogNumber()
        self.parent.updatePreview()
        self.parent.updateAutoComplete()
        self.hide()

    def cancelButtonClicked(self):
        """ hides the preferences window and resets user entries to last
        known good saved values """
        self.hide()
        self.populateSettings()
        
    def getLogoPath(self):
        """ opens a QFileDialog to select an image"""
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Logo Image",
                                                            QtCore.QDir.homePath(), 'Image Files(*.png *.jpg *.bmp)')
        if fileName:  # if an image was selected, store the path
            self.settingsWindow.value_LogoPath.setText(fileName)

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
    
    def updateCatalogNumberPreview(self, QString):
        """ called when a change is made to any of the appropriate fields in 
        catalogNumberPage. Updates the example preview catalog number """
        
        prefix = self.settingsWindow.value_catalogNumberPrefix.text()
        digits = int(self.settingsWindow.value_catalogNumberDigits.value())
        startingNum = str(self.settingsWindow.value_catalogNumberStartingNum.value())
        startingNum = startingNum.zfill(digits)  # fill in leading zeroes
        previewText = f'{prefix}{startingNum}'  # assemble the preview string.
        self.settingsWindow.label_catalogNumber_Preview.setText(previewText)  # set it

    def updateStartingCatalogNumber(self, val):
        """ called when value_catalogNumberdigits changes and alters the max
        value allowed in value_catalogNumberStartingNum. Also, called when
        Catalog numbers are applied, to increment the value_catalogNumberStartingNum"""
        sender = self.sender()
        # check if it is appropriate to alter the maximum digits for starting value
        if sender.objectName() == "value_catalogNumberDigits":
            maxDigits = int(val)
            newMax = int(''.ljust(maxDigits, '9'))
            self.settingsWindow.value_catalogNumberStartingNum.setMaximum(newMax)
        else:  # otherwise just edit the starting value
            self.settingsWindow.value_catalogNumberStartingNum.setValue(val)
            self.setValue('value_catalogNumberStartingNum', val)
        self.updateCatalogNumberPreview

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
            toAdd = ['ITIS (local)', 'Catalog of Life (web API)', 'Taxonomic Name Resolution Service (web API)']
        elif kingdom == 'Fungi':
            toAdd = ['MycoBank (local)', 'Catalog of Life (web API)']
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

    def scalingChanged(self, Qint):
        parent = self.settingsWindow
        val = f'({str(Qint)}%)'.rjust(8, ' ')
        parent.label_scalingValue.setText(val)
    
    def opacityChanged(self, Qint):
        parent = self.settingsWindow
        val = f'({str(Qint)}%)'.rjust(8, ' ')
        parent.label_opacityValue.setText(val)
    
    def genDummyCatalogNumber(self):
        """ generates a single dummy catalog number for label previews"""
        incDummy = self.get('value_inc_Barcode', False)
        if incDummy:
            catDigits = int(self.get('value_catalogNumberDigits'))
            catPrefix = self.get('value_catalogNumberPrefix')
            dummyCatNumber = f'{catPrefix}{str(0).zfill(catDigits)}'
        else:
            dummyCatNumber = False
        self.dummyCatNumber = dummyCatNumber

    def populateSettings(self):
        """ uses self.settings to populate the preferences widget's selections"""
        parent = self.settingsWindow

        #QComboBox
        value_AuthChangePolicy = self.get('value_AuthChangePolicy', 'Always ask')
        self.populateQComboBoxSettings( parent.value_AuthChangePolicy, value_AuthChangePolicy)        
        value_NameChangePolicy = self.get('value_NameChangePolicy', 'Always ask')
        self.populateQComboBoxSettings( parent.value_NameChangePolicy, value_NameChangePolicy)
        value_TaxAlignSource = self.get('value_TaxAlignSource', 'ITIS (local)')
        self.populateQComboBoxSettings( parent.value_TaxAlignSource, value_TaxAlignSource)
        value_Kingdom = self.get('value_Kingdom', 'Plantae')
        self.populateQComboBoxSettings( parent.value_Kingdom, value_Kingdom)
        value_LogoAlignment = self.get('value_LogoAlignment','Centered')
        self.populateQComboBoxSettings( parent.value_LogoAlignment, value_LogoAlignment)
        
        #QLineEdit  .setText
        value_VerifiedBy = self.get('value_VerifiedBy')
        parent.value_VerifiedBy.setText(value_VerifiedBy)
        value_LogoPath = self.get('value_LogoPath')
        parent.value_LogoPath.setText(value_LogoPath)
        value_catalogNumberPrefix = self.get('value_catalogNumberPrefix')
        parent.value_catalogNumberPrefix.setText(value_catalogNumberPrefix)

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
        
        #QGroupbox (checkstate)
        value_inc_Logo = self.convertCheckState(self.get('value_inc_Logo'))
        parent.value_inc_Logo.setChecked(value_inc_Logo)
        value_assignCatalogNumbers = self.convertCheckState(self.get('value_assignCatalogNumbers'))
        parent.value_assignCatalogNumbers.setChecked(value_assignCatalogNumbers)

        #QSpinBox .setValue
        value_X = int(self.get('value_X', 140))
        parent.value_X.setValue(value_X)
        value_Y = int(self.get('value_Y', 90))
        parent.value_Y.setValue(value_Y)
        value_RelFont = int(self.get('value_RelFont',12))
        parent.value_RelFont.setValue(value_RelFont)
        value_TNRS_Threshold = int(self.get('value_TNRS_Threshold', 85))
        parent.value_TNRS_Threshold.setValue(value_TNRS_Threshold)
        value_LogoMargin = int(self.get('value_LogoMargin', 2))
        parent.value_LogoMargin.setValue(value_LogoMargin)
        value_catalogNumberDigits = int(self.get('value_catalogNumberDigits', 1))
        parent.value_catalogNumberDigits.setValue(value_catalogNumberDigits)
        value_catalogNumberStartingNum = int(self.get('value_catalogNumberStartingNum', 0))
        parent.value_catalogNumberStartingNum.setValue(value_catalogNumberStartingNum)
        value_max_Associated = int(self.get('value_max_Associated', 10))
        parent.value_max_Associated.setValue(value_max_Associated)
    
        #slider
        value_LogoScaling = int(self.get('value_LogoScaling', 100))
        parent.value_LogoScaling.setValue(value_LogoScaling)
        self.scalingChanged(value_LogoScaling)
        value_LogoOpacity = int(self.get('value_LogoOpacity', 30))
        parent.value_LogoOpacity.setValue(value_LogoOpacity)
        self.opacityChanged(value_LogoOpacity)
        # note the self.parent.label here, accessing mainwindow.
        value_zoomLevel = int(self.get('value_zoomLevel', 100))
        self.parent.w.value_zoomLevel.setValue(value_zoomLevel)

        #radiobutton
        value_DarkTheme = self.get('value_DarkTheme', False)
        parent.value_DarkTheme.setChecked(value_DarkTheme)
        value_LightTheme = self.get('value_LightTheme', True)
        parent.value_LightTheme.setChecked(value_LightTheme)

        #clean up
        self.updateCatalogNumberPreview

    def saveSettings(self):
        """ stores the preferences widget's selections to self.settings"""
        parent = self.settingsWindow
        # save the version number
        version = self.parent.w.version
        self.setValue('version', version)

        #QComboBox
        value_AuthChangePolicy = parent.value_AuthChangePolicy.currentText()
        self.setValue('value_AuthChangePolicy',value_AuthChangePolicy)
        value_NameChangePolicy = parent.value_NameChangePolicy.currentText()
        self.setValue('value_NameChangePolicy',value_NameChangePolicy)
        value_TaxAlignSource = parent.value_TaxAlignSource.currentText()
        self.setValue('value_TaxAlignSource', value_TaxAlignSource)
        value_Kingdom = parent.value_Kingdom.currentText()
        self.setValue('value_Kingdom', value_Kingdom)
        value_LogoAlignment = parent.value_LogoAlignment.currentText()
        self.setValue('value_LogoAlignment', value_LogoAlignment)

        #QLineEdit
        value_VerifiedBy = parent.value_VerifiedBy.text()
        self.setValue('value_VerifiedBy',value_VerifiedBy)
        value_LogoPath = parent.value_LogoPath.text()
        self.setValue('value_LogoPath',value_LogoPath)
        value_catalogNumberPrefix = parent.value_catalogNumberPrefix.text()
        self.setValue('value_catalogNumberPrefix', value_catalogNumberPrefix)

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
        self.setValue('value_inc_VerifiedBy', value_inc_VerifiedBy)

        #QGroupbox
        value_inc_Logo = parent.value_inc_Logo.isChecked()
        self.setValue('value_inc_Logo', value_inc_Logo)
        value_assignCatalogNumbers = parent.value_assignCatalogNumbers.isChecked()
        self.setValue('value_assignCatalogNumbers', value_assignCatalogNumbers)

        #QSpinBox
        value_X = parent.value_X.value()
        self.setValue('value_X',value_X)
        value_Y = parent.value_Y.value()
        self.setValue('value_Y',value_Y)
        value_RelFont = parent.value_RelFont.value()
        self.setValue('value_RelFont', value_RelFont)
        value_TNRS_Threshold = parent.value_TNRS_Threshold.value()
        self.setValue('value_TNRS_Threshold', value_TNRS_Threshold)
        value_LogoMargin = parent.value_LogoMargin.value()
        self.setValue('value_LogoMargin', value_LogoMargin)
        value_catalogNumberDigits = parent.value_catalogNumberDigits.value()
        self.setValue('value_catalogNumberDigits', value_catalogNumberDigits)
        value_catalogNumberStartingNum = parent.value_catalogNumberStartingNum.value()
        self.setValue('value_catalogNumberStartingNum', value_catalogNumberStartingNum)
        value_max_Associated = parent.value_max_Associated.value()
        self.setValue('value_max_Associated', value_max_Associated)

        #slider
        value_LogoScaling = parent.value_LogoScaling.value()
        self.setValue('value_LogoScaling', value_LogoScaling)
        value_LogoOpacity = parent.value_LogoOpacity.value()
        self.setValue('value_LogoOpacity', value_LogoOpacity)
        value_zoomLevel = self.parent.w.value_zoomLevel.value()
        self.setValue('value_zoomLevel', value_zoomLevel)
        
        #radiobutton
        value_DarkTheme = parent.value_DarkTheme.isChecked()
        self.setValue('value_DarkTheme', value_DarkTheme)
        value_LightTheme = parent.value_LightTheme.isChecked()
        self.setValue('value_LightTheme', value_LightTheme)

