#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 11:23:32 2019

@author: Caleb Powell
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

class formView(QtWidgets.QStackedWidget):
#class formView(QtWidgets.QTabWidget):
# changing to stackedWidget removes the ability to edit site level data on a per specimen basis
# solves user interaction confusion issues at the cost of optional deeper refinements
    
    def __init__(self, parent = None):
        super(formView, self).__init__(parent)
        
    def init_ui(self, parentInstance, parentClass):
        #  TODO understand what the root of the parent mix up is here.
        # Setting it like this and modifying at the end of the formFields is a workaround
        # Without workaround, cannot simultaniously address designer objects form UI file
        # and instance relationships, such as functons I've defined in parent file
        self.parent = parentClass
        self.parentClass = parentClass

    # set up a map for the fields and objects
    # structured as { columnName : ( read Function, save_Function, object )}
        self.formFields = {
                'labelProject': (self.read_QPlainTextEdit, self.save_selectSites_QPlainTextEdit, self.parent.plainTextEdit_labelProject),
                'fieldNotes': (self.read_QPlainTextEdit, self.save_selectSites_QPlainTextEdit, self.parent.plainTextEdit_fieldNotes),
                'identificationReferences': (self.read_QPlainTextEdit, self.save_QPlainTextEdit, self.parent.plainTextEdit_identificationReferences),
                'identificationRemarks': (self.read_QPlainTextEdit, self.save_QPlainTextEdit, self.parent.plainTextEdit_identificationRemarks),
                'eventRemarks':(self.read_QLineEdit, self.save_selectSites_QLineEdit, self.parent.lineEdit_eventRemarks),
                'samplingEffort':(self.read_QLineEdit, self.save_selectSites_QLineEdit, self.parent.lineEdit_samplingEffort),                
                'eventDate': (self.read_QDateEdit, self.save_QDateEdit, self.parent.dateEdit_eventDate),
                'reproductiveCondition': (self.read_QComboBox, self.save_QComboBox, self.parent.comboBox_reproductiveCondition),
                'individualCount': (self.read_QSpinBox, self.save_QSpinBox,  self.parent.spinBox_individualCount),
                'establishmentMeans': (self.read_establishmentMeans, self.save_establishmentMeans, self.parent.checkBox_establishmentMeans),  # special objectType
                'locality': (self.read_QPlainTextEdit, self.save_QPlainTextEdit, self.parent.plainTextEdit_locality),
                'recordedBy': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_recordedBy),
                'associatedCollectors': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_associatedCollectors),
                'associatedTaxa': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_associatedTaxa),
                'habitat': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_habitat),
                'locationRemarks': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_locationRemarks),
                'decimalLatitude': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_decimalLatitude),
                'decimalLongitude': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_decimalLongitude),
                'coordinateUncertaintyInMeters': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_coordinateUncertaintyInMeters),
                'minimumElevationInMeters': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_minimumElevationInMeters),
                'stateProvince': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_stateProvince),
                'county': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_county),
                'municipality': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_municipality),
                'path': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_path),
                'occurrenceRemarks': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_occurrenceRemarks),
                'substrate': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_substrate),
                'catalogNumber': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_catalogNumber),
                'recordNumber': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_recordNumber),
                'scientificName': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_sciName),  # breaks naming convention
                'scientificNameAuthorship':(self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_sciNameAuthority),  # breaks naming convention
                }
        self.connectFields()
        self.parent = parentInstance

        # Set up input validation on the GPS fields        
        # LatRe & LonRe Patterns credited to "Jason Rutberg" from http://www.regexlib.com/
        latRE = QRegExp("^-?(90|[1-8][0-9]|[1-9])\.{1}\d{1,8}")
        #latRE = QRegExp("^-?([1-8]?[1-9]|[1-9]0)\.{1}\d{1,8}")
        lat_validator = QRegExpValidator(latRE, self.parentClass.lineEdit_decimalLatitude)
        self.parentClass.lineEdit_decimalLatitude.setValidator(lat_validator)
        lonRE = QRegExp("^-?([1-9]|[1-9][0-9]|[1][0-8][0]|[1][0-7][0-9])\.{1}\d{1,8}")
        #lonRE = QRegExp("^-?([1]?[0-9][0-9]|[1]?[1-8][0]|[1-9]?[0-9])\.{1}\d{1,8}")
        lon_validator = QRegExpValidator(lonRE, self.parentClass.lineEdit_decimalLongitude)
        self.parentClass.lineEdit_decimalLongitude.setValidator(lon_validator)
        uncertRE = QRegExp("^\d{1,5}\.{1}\d{1,8}")
        uncert_validator = QRegExpValidator(uncertRE, self.parentClass.lineEdit_coordinateUncertaintyInMeters)
        self.parentClass.lineEdit_coordinateUncertaintyInMeters.setValidator(uncert_validator)
        elevRE = QRegExp("^\d{1,4}\.{1}\d{1,8}")
        elev_validator = QRegExpValidator(uncertRE, self.parentClass.lineEdit_minimumElevationInMeters)
        self.parentClass.lineEdit_minimumElevationInMeters.setValidator(elev_validator)

    def connectFields(self):
        """ connect formview fields to save functions 
        with 'data changed' signals. """
        for colName, val in  self.formFields.items():
            _, saveFunc, qtObject = val  # break out the value tuple
            qtObject.colName = colName  # assign each object it's associated column name
            if isinstance(qtObject, QtWidgets.QDateEdit):
                qtObject.dateChanged.connect(saveFunc)
            elif isinstance(qtObject, QtWidgets.QComboBox):
                qtObject.currentTextChanged.connect(saveFunc)
            elif isinstance(qtObject, QtWidgets.QLineEdit):
                qtObject.textChanged.connect(saveFunc)
            elif isinstance(qtObject, QtWidgets.QCheckBox):
                qtObject.toggled.connect(saveFunc) #  Note, if any other checkboxes are added this will be problematic
            elif isinstance(qtObject, QtWidgets.QSpinBox):
                qtObject.valueChanged.connect(saveFunc)
            elif isinstance(qtObject, QtWidgets.QPlainTextEdit):
                qtObject.textChanged.connect(saveFunc)

    def fillFormFields(self):
        """ Used to populate the form_View fields. Reads each key in
        formFields, retrieves the appropriate value and
        applies the associated read_Function. """
        rowData = self.parent.getVisibleRowData()
        if rowData:
            rowData = rowData[0] #  rowData is delivered as a list of rows, in this case we always want the first row
            for colName, val in self.formFields.items():
                readFunc, _, qtObject = val  # break out the value tuple
                value = rowData.get(colName, '')
                qtObject.blockSignals(True)  # Pause data changed signals
                readFunc(qtObject, value)
                qtObject.blockSignals(False)  # Resume data changed signals

    def saveChanges(self, colName, value, selectSites = False):
        """ Actualy stores the changes. Called by the other save_xxx funcs."""
        df = self.parent.m.datatable
        if selectSites:  # if the saveFunc requested only selectedSites
            selectedSites = self.parent.getSelectSitesToApply()
            if len(selectedSites) > 0:  # and if there ARE sites selected
                df.loc[df['siteNumber'].isin(selectedSites), colName] = value
            else:  # if requested selected sites ,and none selected. Done.
                return None
        else:  # if saveFunc did not request selected sites
            visibleRows = self.parent.getVisibleRows()  # identify what is currently within the user's scope
            df.loc[visibleRows, colName] = value  # and select it
        if colName == 'associatedTaxa':
            df = df.apply(self.parent.associatedTaxaWindow.cleanAssociatedTaxa, axis = 1)
            self.parent.associatedTaxaWindow.isWaitingOnUser = False
        #  it may be worth while to do something similar for associatedCollectors & recordedBy
        self.parent.m.update(df)

    def read_QLineEdit(self, obj, value):
        obj.setText(value)

    def save_QLineEdit(self, value):
        sender = self.sender()
        colName = sender.colName
        self.saveChanges(colName, value)

    def save_selectSites_QLineEdit(self, value):
        sender = self.sender()
        colName = sender.colName
        self.saveChanges(colName, value, selectSites=True)

    def read_QDateEdit(self, obj, value):
        obj.setDate(QDate.fromString(value, "yyyy-MM-dd"))

    def save_QDateEdit(self, obj):
        sender = self.sender()
        colName = sender.colName
        value = obj.toString("yyyy-MM-dd")
        self.saveChanges(colName, value)

    def read_QComboBox(self, obj, value):
        valuePosition = obj.findText(value)
        if valuePosition < 0:
            valuePosition = 0
        obj.setCurrentIndex(valuePosition)

    def save_QComboBox(self, obj):
        sender = self.sender()
        colName = sender.colName
        value = obj.strip()
        self.saveChanges(colName, value)

    def read_QSpinBox(self, obj, value):
        try:
            value = int(value)
            obj.setValue(value)
        except ValueError:
            obj.clear()

    def save_QSpinBox(self, obj):
        sender = self.sender()
        colName = sender.colName
        value = str(obj)
        if value == '0':
            value = ''    
        self.saveChanges(colName, value)

    def read_establishmentMeans(self, obj, value):
        """ establishmentMeans is forced into a binary condition
        of cultivated True False this function handles the conversions"""
        if value in ['cultivated', True, 1]:
            obj.setCheckState(Qt.Checked)
        else:
            obj.setCheckState(Qt.Unchecked)

    def save_establishmentMeans(self, obj):
        sender = self.sender()
        colName = sender.colName
        if obj in ['cultivated', True, 1]:
            value = "cultivated"
            self.saveChanges(colName, value)
        else:
            self.saveChanges(colName,'')

    def read_QPlainTextEdit(self, obj, value):
        obj.setPlainText(value)

    def save_QPlainTextEdit(self):
        sender = self.sender()
        colName = sender.colName
        value = sender.toPlainText()
        self.saveChanges(colName, value)
        
    def save_selectSites_QPlainTextEdit(self):
        sender = self.sender()
        colName = sender.colName
        value = sender.toPlainText()
        self.saveChanges(colName, value, selectSites=True)

    def determineDataLevel(self):
        """ determines the level of data selected according to the table_view"""
        selType, siteNum, specimenNum = self.parent.getTreeSelectionType()

    def readDefaultNewSiteFields(self):
        """ returns a dictionary of column names and values from the 
        Defaults group under the All Records view."""
        # todo figure out the issue with parent addressing in the form class
        default_eventDate = self.parentClass.dateEdit_default_eventDate.date().toString("yyyy-MM-dd")
        default_recordedBy = self.parentClass.lineEdit_default_recordedBy.text()
        default_associatedCollectors = self.parentClass.lineEdit_default_associatedCollectors.text()
        
        defVals = {'eventDate':default_eventDate,
                   'recordedBy':default_recordedBy,
                   'associatedCollectors':default_associatedCollectors}
        return defVals

