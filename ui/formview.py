#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 11:23:32 2019

@author: Caleb Powell
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.QtCore import Qt


class formView(QtWidgets.QTabWidget):

    def __init__(self, parent = None):
        super(formView, self).__init__(parent)
        #self.init_ui(parent)

    
    def init_ui(self, parent):
        self.parent = parent
        
        #print(dir(self))
        
    #   def init_ui(self, parent):

        #t # this is the master window


    def fillFormFields(self, rowData):
        """ accepts a dictionary of rowdata and populates the appropriate
        formview fields"""

        self = self.parent  # make it easier to address the parent's elements
        rowData = rowData[0]  # the input rowData
        
        #dateEdit .setDate
        eventDate = rowData.get('eventDate','')
        self.dateEdit_eventDate.setDate(QDate.fromString(eventDate,"yyyy-MM-dd"))
        
        #QComboBox 
        reproductiveCondition = rowData.get('reproductiveCondition','')
        reproductiveConditionIndex = self.comboBox_reproductiveCondition.findText(reproductiveCondition)
        if reproductiveConditionIndex < 0:
            reproductiveConditionIndex = 0
        self.comboBox_reproductiveCondition.setCurrentIndex(reproductiveConditionIndex)

        #QSpinBox .setValue
        try:
            individualCount = int(rowData.get('individualCount',''))
            self.spinBox_individualCount.setValue(individualCount)
        except:
            pass
        
        # QCheckBox
        # NOTE Will have to make similar adjustment for the saving and editing of this value
        establishmentMeans = rowData.get('establishmentMeans','')
        if establishmentMeans in ['cultivated', True, 1]:
            self.checkBox_establishmentMeans.setCheckState(Qt.Checked)
        
        #QPlainTextEdit .setPlainText 
        locality = rowData.get('locality','')
        self.plainTextEdit_locality.setPlainText(locality)
        #QLineEdit  .setText
        recordedBy = rowData.get('recordedBy','')
        self.lineEdit_recordedBy.setText(recordedBy)
        associatedCollectors = rowData.get('associatedCollectors','')
        self.lineEdit_associatedCollectors.setText(associatedCollectors)
        associatedTaxa = rowData.get('associatedTaxa','')
        self.lineEdit_associatedTaxa.setText(associatedTaxa)
        habitat = rowData.get('habitat','')
        self.lineEdit_habitat.setText(habitat)
        locationNotes = rowData.get('lineEdit_locationNotes','')
        self.lineEdit_locationNotes.setText(locationNotes)
        decimalLatitude = rowData.get('decimalLatitude','')
        self.lineEdit_decimalLatitude.setText(decimalLatitude)
        decimalLongitude = rowData.get('decimalLongitude','')
        self.lineEdit_decimalLongitude.setText(decimalLongitude)
        coordinateUncertaintyInMeters = rowData.get('coordinateUncertaintyInMeters','')
        self.lineEdit_coordinateUncertaintyInMeters.setText(coordinateUncertaintyInMeters)
        stateProvince = rowData.get('stateProvince','')
        self.lineEdit_stateProvince.setText(stateProvince)
        county = rowData.get('county','')
        self.lineEdit_county.setText(county)
        municipality = rowData.get('municipality','')
        self.lineEdit_municipality.setText(municipality)
        path = rowData.get('path','')
        self.lineEdit_path.setText(path)
        occurrenceRemarks = rowData.get('occurrenceRemarks','')
        self.lineEdit_occurrenceRemarks.setText(occurrenceRemarks)
        substrate = rowData.get('substrate','')
        self.lineEdit_substrate.setText(substrate)
        catalogNumber = rowData.get('catalogNumber','')
        self.lineEdit_catalogNumber.setText(catalogNumber)
        otherCatalogNumber = rowData.get('otherCatalogNumber','')
        self.lineEdit_otherCatalogNumber.setText(otherCatalogNumber)
        
        # note these two currently violate naming conventions
        scientificName = rowData.get('scientificName','')
        self.lineEdit_sciName.setText(scientificName)
        scientificNameAuthority = rowData.get('scientificNameAuthority','')
        self.lineEdit_sciNameAuthority.setText(scientificNameAuthority)


    def determineDataLevel(self):
        """ determines the level of data selected according to the table_view"""
        selType, siteNum, specimenNum = self.parent.getTreeSelectionType()


    def siteFieldChanged(self, fieldName):
        """ saves changes to site level data """


    def specimenFieldChanged(self, fieldName):
        """ saves changes to specimen level data"""

