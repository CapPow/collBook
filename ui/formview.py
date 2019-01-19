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
        
    def init_ui(self, parentInstance, parentClass):
        #  TODO understand what the root of the parent mix up is here.
        # Setting it like this and modifying at the end of the formFields is a workaround
        # Without workaround, cannot simultaniously address designer objects form UI file
        # and instance relationships, such as functons I've defined in parent file
        self.parent = parentClass

    # set up a map for the fields and objects
    # structured as { columnName : ( read Function, save_Function, object )}
        self.formFields = {
                'eventDate': (self.read_QDateEdit, self.save_QDateEdit, self.parent.dateEdit_eventDate),
                'reproductiveCondition': (self.read_QComboBox, self.save_QComboBox, self.parent.comboBox_reproductiveCondition),
                'individualCount': (self.read_QSpinBox, self.save_QSpinBox,  self.parent.spinBox_individualCount),
                'establishmentMeans': (self.read_establishmentMeans, self.save_establishmentMeans, self.parent.checkBox_establishmentMeans),  # special objectType
                'locality': (self.read_QPlainTextEdit, self.save_QPlainTextEdit, self.parent.plainTextEdit_locality),
                'recordedBy': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_recordedBy),
                'associatedCollectors': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_associatedTaxa),
                'associatedTaxa': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_associatedTaxa),
                'habitat': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_habitat),
                'locationNotes': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_locationNotes),
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
                'otherCatalogNumbers': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_otherCatalogNumbers),
                'scientificName': (self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_sciName),  # breaks naming convention
                'scientificNameAuthorship':(self.read_QLineEdit, self.save_QLineEdit, self.parent.lineEdit_sciNameAuthority),  # breaks naming convention
                }
        self.connectFields()
        
        self.parent = parentInstance

    def connectFields(self):
        """ connect formview fields to save functions 
        with 'data changed' signals. """
        for colName, val in  self.formFields.items():
            _, saveFunc, qtObject = val  # break out the value tuple
            qtObject.colName = colName  # assign each object it's associated column name
            
            if isinstance(qtObject, QtWidgets.QDateEdit):
                qtObject.dateChanged.connect(self.save_QDateEdit)
            elif isinstance(qtObject, QtWidgets.QComboBox):
                qtObject.currentTextChanged.connect(self.save_QComboBox)
            elif isinstance(qtObject, QtWidgets.QLineEdit):
                qtObject.textChanged.connect(self.save_QLineEdit)
            elif isinstance(qtObject, QtWidgets.QCheckBox):
                qtObject.toggled.connect(self.save_establishmentMeans) #  Note, if any other checkboxes are added this will be problematic
            elif isinstance(qtObject, QtWidgets.QSpinBox):
                qtObject.valueChanged.connect(self.save_QSpinBox)
            elif isinstance(qtObject, QtWidgets.QPlainTextEdit):
                qtObject.textChanged.connect(self.save_QPlainTextEdit)
            
    
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

    def saveChanges(self, colName, value):
        pdModel = self.parent.m  # link to the PandasTableModel
        visibleRows = self.parent.getVisibleRows()  # get what is currently within the user's scope
        df = pdModel.datatable.loc[visibleRows, ]
        df[colName] = value
        pdModel.datatable.update(df)
        pdModel.update(pdModel.datatable)
    
    def read_QLineEdit(self, obj, value):
        obj.setText(value)

    def save_QLineEdit(self, value):
        sender = self.sender()
        colName = sender.colName
        self.saveChanges(colName, value)

    def read_QDateEdit(self, obj, value):
        obj.setDate(QDate.fromString(value, "yyyy-MM-dd"))

    def save_QDateEdit(self, obj):
        sender = self.sender()#.objectName()
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

    def read_QPlainTextEdit(self, obj, value):
        obj.setPlainText(value)

    def save_QPlainTextEdit(self):
        sender = self.sender()
        colName = sender.colName
        value = sender.toPlainText()
        self.saveChanges(colName, value)

    def determineDataLevel(self):
        """ determines the level of data selected according to the table_view"""
        selType, siteNum, specimenNum = self.parent.getTreeSelectionType()


    def siteFieldChanged(self, fieldName):
        """ saves changes to site level data """


    def specimenFieldChanged(self, fieldName):
        """ saves changes to specimen level data"""

