#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 10:33:55 2019

@author: Caleb Powell

Based on work from github user Beugeny
https://github.com/Beugeny/python_test/blob/d3e21dc075d9cef8dca323d281cbbdb4765233c6/Test1.py
"""
#from PyQt5 import Qt
#from PyQt5.QtCore import QAbstractTableModel
#from PyQt5.QtCore import QDir
#from PyQt5.QtCore import QStringListModel
#from PyQt5.QtCore import QVariant
#from PyQt5.QtGui import QColor
#from PyQt5.QtGui import QIcon
#from PyQt5.QtWidgets import QFileSystemModel

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox

#from ui.locality import genLocalityNoAPI, genLocality
import pandas as pd

# NOTE see set_data function for the method to notify the table of changes
# to the data
# ie: self.dataChanged.emit(index, index, (QtCore.Qt.DisplayRole, ))

# NOTE for code snippits see:
# https://github.com/SanPen/GridCal/blob/master/UnderDevelopment/GridCal/Gui/GuiFunctions.py

class PandasTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, editable = True, *args):
        super(PandasTableModel, self).__init__(parent)
        
        self.datatable = None  # what the user is seeing & interacting with
        
        # custom undo implimentation, essentially storing copies of dataframes 
        # stored as a list of tuples (df, "description of change")
        # undoing or redoing simply restores the list according to the index
        self.undoStack = []  # holds the checkpoints
        self.undoIndex = 0  # the current position in the checkpoint list
        self.undoActive = False  # is an undo available?
        self.redoActive = False  # is a redo available?

    def processViewableRecords(self, rowsToProcess, func):
        """ applies a function over each row among those selected by the
        treeSelectionType """
        df = self.datatable.iloc[rowsToProcess, ]
        try:
            df.apply(func, 1)
        except Exception as e:
            print(e)
        self.datatable.update(df)
        self.update(self.datatable)
    
    def add_to_undo_stack(self, description = 'the last major action'):
        """ to be called just before a change is made to the underlaying df """
        undoStack = self.undoStack  # establish a shorthand
        undoIndex = self.undoIndex
        undoIndex = 0 # if a change was made, reset the index
        if undoIndex >= 20:  # be sure not to grow too big
            undoStack = undoStack[:20]
        df = self.datatable   # save the details into a checkpoint
        checkPoint = (df.copy(deep=True), description)
        undoIndex.insert(0, checkPoint)  # insert it at the top of the list

    def undo(self):
        """ restores the underlaying df to a previous checkpoint """
        if undoIndex == 0:
            add_to_undo_stack(self, "")
            self.undoIndex += 1

        if (self.undoActive & self.undoIndex <= len(self.undoStack) - 1):
            self.undoIndex += 1

    def update(self, dataIn):
        self.beginResetModel()
        self.datatable = dataIn
        self.endResetModel()
        # let display elements know about the change (ie: qTreeWidget)
        self.dataChanged.emit(QtCore.QModelIndex(),QtCore.QModelIndex() , (QtCore.Qt.DisplayRole, ))

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.columns.values)
    
    def columnIndex(self, colName):
        """ given a column name, returns the index of it's location. Called
        by updateTableView to get the index of "specimen#" for sorting."""
        result = self.datatable.columns.get_loc(colName)
        return result
    
    def retrieveRowData(self, i):
        """ given a row index number returns the data as a series """
        df = self.datatable
        return df.iloc[i]
    
    def getSelectedLabelDict(self, df):
        """Returns a list of dictionaries from given df
        organized as {column name: cell value}."""
        df = df.fillna('')
        if isinstance(df, pd.Series): # not sure if a series or df will be handed in
            data = [df.to_dict()]
        else:
            data = df.to_dict(orient='dict')
        labelDicts = []
        for datum in data:
            datum = {key: value.strip() for key, value in datum.items() if isinstance(value,str)} #dict comprehension!
            if datum.get('specimen#') not in ['#','!AddSITE']:   #keep out the site level records!
                labelDicts.append(datum)
        return labelDicts

    def dataToDict(self, df):
        """ given a df (or series) bundles the data as a dictionary
        Initially written for label pdf generation, may also be useful for
        field population"""
        records = self.getSelectedLabelDict(df)  #function returns a list of dicts (one for each record to print)
        if len(records) > 0:
            for record in records:   
                # TODO needs to be updated for "verified by" considerations
                # currently just has it commented out
                #if CatNumberBar.stuCollCheckBoxVar.get() == 1: # for each dict, if it is student collection
                #    record['verifiedBy'] = CatNumberBar.stuCollVerifyByVar.get() #then add the verified by name to the dict.
                associatedTaxaItems = record.get('associatedTaxa').split(', ') #for each dict, verify that the associatedTaxa string does not consist of >15 items.
                if len(associatedTaxaItems) > 10:   #if it is too large, trunicate it at 15, and append "..." to indicate trunication.
                    record['associatedTaxa'] = ', '.join(associatedTaxaItems[:10])+' ...'   
        return records
    
    def getRowsToProcess(self, selType, siteNum = None, specimenNum = None):
        """ defined for clarity, calls getRowsToKeep with the same args."""
        return self.getRowsToKeep(selType, siteNum, specimenNum)

    def getRowsToKeep(self, selType, siteNum = None, specimenNum = None):
        """ Returns list of row indices associated with inputs """
        df = self.datatable
        allRows = df.index.values.tolist()
        df = df[~df['specimen#'].str.contains('#')]
        if selType == 'allRec':
            rowsToKeep = allRows
        elif selType == 'site':
            rowsToKeep = df[df['site#'] == siteNum].index.values.tolist()
        elif selType == 'specimen':
            rowsToKeep = df[(df['site#'] == siteNum) & (df['specimen#'] == specimenNum)].index.values.tolist()
        return rowsToKeep
    
    def getRowsToHide(self, selType, siteNum = None, specimenNum = None):
        """ Returns list of row indicies NOT associated with input options
        called from mainWindow's updateTableView() following 
        tree_widget selection changes."""
        df = self.datatable
        allRows = df.index.values.tolist()
        rowsToKeep = self.getRowsToKeep(selType, siteNum, specimenNum)
        rowsToHide = [x for x in allRows if x not in rowsToKeep]
        return rowsToHide
    
    def getSiteSpecimens(self):
        """ Returns a list of tuples for each site# specimen# combination
        called from mainWindow's populateTreeWidget"""
        df = self.datatable
        results = list(zip(df['site#'], df['specimen#']))
        return results


    def data(self, index, role=QtCore.Qt.DisplayRole):  # TODO figure out what this def is doing and when it is called
        if role == QtCore.Qt.DisplayRole:
            i = index.row()
            j = index.column()
            return '{0}'.format(self.datatable.iloc[i, j])
        elif role == QtCore.Qt.ToolTipRole:
            i = index.row()
            j = index.column()
            return 'Index={0}-{1}'.format(i, j)
        else:
            return QtCore.QVariant()

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsEnabled

    def setData(self, index, value, role=None):
        if index.isValid() and role == QtCore.Qt.EditRole:
            i = index.row()
            j = index.column()
            self.datatable.iloc[i, j] = value
            self.dataChanged.emit(index, index, (QtCore.Qt.DisplayRole, ))
            return True
        return False

    def headerData(self, p_int, Qt_Orientation, role=None):
        if role == QtCore.Qt.DisplayRole:
            if Qt_Orientation == QtCore.Qt.Horizontal:
                return self.datatable.columns.values[p_int]
            else:
                return self.datatable.index[p_int]
        return QtCore.QVariant()

    def open_CSV(self, fileName = None):
        # is triggered by the action_Open.
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Open CSV",
                                                            QtCore.QDir.homePath(), "CSV (*.csv)")
        if fileName:  # if a csv was selected, start loading the data.
            df = pd.read_csv(fileName, encoding = 'utf-8',keep_default_na=False, dtype=str)
            df = df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1) # drop any "unnamed" cols
            if ~df.columns.isin(['site#']).any():  # if the site# does not exist:
                df = self.inferSiteSpecimenNumbers(df)  # attempt to infer them
            sort_col_Names = ['site#', 'specimen#']
            df.fillna('') # make any nans into empty strings.
            df.sort_values(by=sort_col_Names, inplace=True, ascending=True)
            self.update(df)  # this function actually updates the visible dataframe
            return True

    def inferSiteSpecimenNumbers(self, df):
        """ attempts to infer a site# and specimen# of an incoming df """

        def specimenNumExtract(catNum):
            try:
                result = catNum.split('-')[1]
                if result.isdigit():
                    return result
                else:
                    return '#'
            except (ValueError, IndexError, AttributeError) as e:
                return '#'

        def siteNumExtract(catNum):
            try:
                result = catNum.split('-')[0]
                if result.isdigit():
                    return result
                else:
                    return ''
            except (ValueError, IndexError, AttributeError) as e:
                return ''
        try:
            df['site#'] = df['otherCatalogNumbers'].transform(lambda x: siteNumExtract(x))
            df['specimen#'] = df['otherCatalogNumbers'].transform(lambda x: specimenNumExtract(x))
        except IndexError:
            pass

        return df

    def new_Records(self, skipDialog = False):
        # is triggered by the action_new_Records.
        """Clears all the data and makes a new table
        if skipDialog is True, it won't ask."""
        qm = QMessageBox
        if skipDialog:
            ret = QMessageBox.Yes
        else:    
            ret = qm.question(self.parent(),'', 'Load a blank data set? (any unsaved progress will be lost)', qm.Yes | qm.No)
        if ret == qm.Yes:
            newDFDict = {
            'site#':['0','1'],
            'specimen#':['0','1'],
            'otherCatalogNumbers':['1-#','1-1'],
            'family':['',''],
            'scientificName':['',''],
            'genus':['',''],
            'scientificNameAuthorship':['',''],
            'taxonRemarks':['',''],
            'identifiedBy':['',''],
            'dateIdentified':['',''],
            'identificationReferences':['',''],
            'identificationRemarks':['',''],
            'collector':['',''],
            'collectorNumber':['',''],
            'associatedCollectors':['',''],
            'eventDate':['',''],
            'verbatimEventDate':['',''],
            'habitat':['',''],
            'substrate':['',''],
            'occurrenceRemarks':['',''],
            'informationWithheld':['',''],
            'associatedOccurrences':['',''],
            'dataGeneralizations':['',''],
            'associatedTaxa':['',''],
            'dynamicProperties':['',''],
            'description':['',''],
            'reproductiveCondition':['',''],
            'cultivationStatus':['',''],
            'establishmentMeans':['',''],
            'lifeStage':['',''],
            'sex':['',''],
            'individualCount':['',''],
            'country':['',''],
            'stateProvince':['',''],
            'county':['',''],
            'municipality':['',''],
            'locality':['',''],
            'localitySecurity':['',''],
            'decimalLatitude':['',''],
            'decimalLongitude':['',''],
            'geodeticDatum':['',''],
            'coordinateUncertaintyInMeters':['',''],
            'verbatimCoordinates':['',''],
            'minimumElevationInMeters':['',''],
            'maximumElevationInMeters':['',''],
            'verbatimElevation':['',''],
            'duplicateQuantity':['',''],
            'labelProject':['','']}
    
            df = pd.DataFrame.from_dict(newDFDict)
            df['-'] = '-' # add in the little "-" seperator.
            df.fillna('') # make any nans into empty strings.
            self.update(df)  # this function actually updates the visible dataframe
        return

