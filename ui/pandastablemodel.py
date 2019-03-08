#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 10:33:55 2019

@author: Caleb Powell

Based on work from github user Beugeny
https://github.com/Beugeny/python_test/blob/d3e21dc075d9cef8dca323d281cbbdb4765233c6/Test1.py
"""
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from pathlib import Path
from reportlab.platypus.doctemplate import LayoutError
from ui.importindexdialog import importDialog
import pandas as pd
import numpy as np

class PandasTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, editable = True, *args):
        super(PandasTableModel, self).__init__(parent)
        self.parent = parent
        self.datatable = None  # what the user is seeing & interacting with
        # custom undo method
        self.undoList = []  # holds the checkpoints
        self.redoList = []  # the current position in the checkpoint list
        self.updateUndoRedoButtons()  # set up initial undo / redo state

    def addToUndoList(self, description='undo the last major action'):
        """ to be called just before a change is made to the underlaying df """
        selection = self.parent.getTreeSelectionType()
        df = self.datatable   # save the details into a checkpoint
        checkPoint = (df.copy(deep=True), selection, description)
        self.undoList.append(checkPoint)
        self.redoList = []  # if we're adding to undoList, clear redoList
        self.updateUndoRedoButtons()
        if len(self.undoList) > 40:  # be sure not to grow too big
            self.undoList = self.undoList[40:]

    def redo(self):
        """ restores the underlaying df the most recent redoList point """
        origDF = self.datatable
        try:
            checkpoint = self.redoList.pop()
        except IndexError:
            checkpoint = (None,  (None, None, None),  'the last major action')
        df, sel, msg = checkpoint
        if isinstance(df, pd.DataFrame):
            self.datatable = df
            self.update(self.datatable)
            self.parent.updateTableView()
        self.undoList.append((origDF, sel, msg))
        self.updateUndoRedoButtons()
        self.parent.populateTreeWidget()
        self.parent.setTreeSelectionByType(*sel)  # return the selection

    def undo(self):
        """ restores the underlaying df to the most recent undoList point"""
        origDF = self.datatable
        try:
            checkpoint = self.undoList.pop()
        except IndexError:
            checkpoint = (None, (None, None, None), 'the last major action')
        df, sel, msg = checkpoint
        if isinstance(df, pd.DataFrame):
            self.datatable = df
            self.update(self.datatable)
            self.parent.updateTableView()
        self.redoList.append((origDF, sel, msg))
        self.updateUndoRedoButtons()
        self.parent.populateTreeWidget()
        self.parent.setTreeSelectionByType(*sel)  # return the selection

    def updateUndoRedoButtons(self):
        """ called if the self.undoIndex changes. Updates the hint text of the
            undo, & redo buttons to reflect the description appended in 
            addToUndoList"""
        if len(self.undoList) > 0 :
            self.parent.w.action_undo.setEnabled(True)
            msg = self.undoList[-1][-1]#.replace('redo: ', 'undo: ')
            msg = f'undo: {msg}'
        else:
            self.parent.w.action_undo.setEnabled(False)
            msg = 'undo the last major action'
        self.parent.w.action_undo.setToolTip(msg)

        if len(self.redoList) > 0 :
            self.parent.w.action_redo.setEnabled(True)
            msg = self.redoList[-1][-1]#.replace('undo', 'redo')
            msg = f'redo: {msg}'
        else:
            self.parent.w.action_redo.setEnabled(False)
            msg = 'redo the last major action'    
        self.parent.w.action_redo.setToolTip(msg)

    def update(self, dataIn):
        self.beginResetModel()
        self.datatable = dataIn
        self.endResetModel()
        # let display elements know about the change (ie: qTreeWidget)
        self.dataChanged.emit(QtCore.QModelIndex(),QtCore.QModelIndex() , (QtCore.Qt.DisplayRole, ))

    def addNewSite(self):
        """ adds a new, nearly blank site record to the dataTable """
        df = self.datatable
        try:
            newSiteNum = max(pd.to_numeric(df['siteNumber'], errors = 'coerce')) + 1
        except ValueError:
            newSiteNum = 1
        self.addToUndoList(f'added site {newSiteNum}')  # set checkpoint in undostack
        rowData = {'recordNumber':f'{newSiteNum}-#', 
                   'siteNumber':f'{newSiteNum}',
                   'specimenNumber':'#'}
        defVals = self.parent.form_view.readDefaultNewSiteFields()
        rowData.update(defVals)
        df = df.append(rowData,  ignore_index=True, sort=False)
        df.fillna('', inplace = True)
        self.update(df)
        self.parent.populateTreeWidget()
        # change tree_widget's selection to the to new site.
        self.parent.selectTreeWidgetItemByName(f'Site {newSiteNum}(0)')
    
    def addNewSpecimen(self):
        """ adds a new specimen record to selected site """
        df = self.datatable
        selType, siteNum, specimenNum = self.parent.getTreeSelectionType()
        if selType in ['site','specimen']:
            try:  # try to make the new row data
                spNums = df[(df['siteNumber'] == siteNum) &
                            (df['specimenNumber'] != '#')]['specimenNumber']
                newSpNum = max(pd.to_numeric(spNums, errors='coerce')) + 1
            except ValueError:
                newSpNum = 1
            newRowData = df[(df['siteNumber'] == siteNum) &
                            (df['specimenNumber'] == '#')].copy()
            newRowData['specimenNumber'] = f'{newSpNum}'
            catNum =  f'{siteNum}-{newSpNum}'
            self.addToUndoList(f'added specimen {catNum}')  # set checkpoint in undostack
            newRowData['recordNumber'] = catNum
            df = df.append(newRowData, ignore_index=True, sort=False)
            df = self.sortDF(df)
            df.fillna('', inplace=True)
            self.update(df)
            self.parent.populateTreeWidget()
            # change tree_widget's selection to the to new specimen.
            self.parent.selectTreeWidgetItemByName(catNum)

    def duplicateSpecimen(self):
        """ copies MOST fields from a specimen record into a new record in
        the same site number """
        df = self.datatable
        selType, siteNum, specimenNum = self.parent.getTreeSelectionType()
        if selType == 'specimen':
            self.addToUndoList(f'duplicated specimen {siteNum}-{specimenNum}')  # set checkpoint in undostack
            try:  # try to make the new row data
                spNums = df[(df['siteNumber'] == siteNum) &
                            (df['specimenNumber'] != '#')]['specimenNumber']
                newSpNum = max(pd.to_numeric(spNums, errors='coerce')) + 1
            except ValueError:
                newSpNum = 2
            newRowData = df[(df['siteNumber'] == siteNum) &
                            (df['specimenNumber'] == specimenNum)].copy()
            newRowData['specimenNumber'] = f'{newSpNum}'
            catNum =  f'{siteNum}-{newSpNum}'
            newRowData['recordNumber'] = catNum
            df = df.append(newRowData, ignore_index=True, sort=False)
            df = self.sortDF(df)
            df.fillna('', inplace=True)
            self.update(df)
            self.parent.populateTreeWidget()
            # change tree_widget's selection to the to new specimen.
            self.parent.selectTreeWidgetItemByName(catNum)
                
    def deleteSite(self):
        """ called from the delete site button """
        df = self.datatable
        selType, siteNum, specimenNum = self.parent.getTreeSelectionType()
        if selType == 'site':
            self.addToUndoList(f'removed site {siteNum}')  # set checkpoint in undostack
            newDF = df[df['siteNumber'] != siteNum].copy()
            newDF = self.sortDF(newDF)
            self.datatable = newDF
            self.update(self.datatable)
            self.parent.populateTreeWidget()
            # change tree_widget's selection to All Records.
            self.parent.w.checkBox_delSite.setCheckState(Qt.Unchecked)
            self.parent.selectTreeWidgetItemByName('All Records')

    def deleteSpecimen(self):
        """ called from the delete specimen button """
        df = self.datatable
        selType, siteNum, specimenNum = self.parent.getTreeSelectionType()
        if selType == 'specimen':
            self.addToUndoList(f'removed specimen {siteNum}-{specimenNum}')  # set checkpoint in undostack
            newDF = df[~((df['siteNumber'] == siteNum) & (df['specimenNumber'] == specimenNum))].copy()
            newDF = self.sortDF(newDF)
            self.datatable = newDF
            self.update(self.datatable)
            self.parent.populateTreeWidget()
            # change tree_widget's selection to All Records.
            self.parent.w.checkBox_deleteRecord.setCheckState(Qt.Unchecked)
            self.parent.selectTreeWidgetItemByName(f'Site ({siteNum})')
            self.parent.expandCurrentTreeWidgetItem() # re-expand the site selection

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.datatable.columns.values)
    
    def columnIndex(self, colName):
        """ given a column name, returns the index of it's location. Called
        by updateTableView to get the index of "specimenNumber" for sorting."""
        result = self.datatable.columns.get_loc(colName)
        return result
    
    def retrieveRowData(self, i):
        """ given a row index number returns the data as a series """
        df = self.datatable
        return df.loc[i]

    def getSelectedLabelDict(self, df):
        """Returns a list of dictionaries from given df
        organized as {column name: cell value}."""
        df = df.fillna('')
        if isinstance(df, pd.Series): # not sure if a series or df will be handed in
            data = [df.to_dict()]
        else:
            data = df.to_dict(orient='records')
        labelDicts = []
        for datum in data:
            #datum = {key: value.strip() for key, value in datum.items() if isinstance(value,str)} #dict comprehension!
            datum = {key: value for key, value in datum.items() if isinstance(value,str)} # strip command was preventing spaces from being entered
            #if datum.get('specimenNumber') not in ['#','!AddSITE']:   #keep out the site level records!
            labelDicts.append(datum)
        return labelDicts

    def geoRef(self):
        """ applies genLocality over each row among those selected.
        Combines api calls for records from the same site."""
        # Needs modified If editing site data at specimen level records is re-enabled.

        self.addToUndoList('geolocate process')  # set checkpoint in undostack
        selType, siteNum, specimenNum = self.parent.getTreeSelectionType()
        if selType == 'site':
            # hacky method to get only site level record (catalogNumber: "n-#")
            rowsToProcess = self.getRowsToProcess('specimen', siteNum, '#')
            sitesToUpdate = [siteNum]
        elif selType == 'allRec':
            records = self.getSiteSpecimens()
            # less hacky method to get every site level record
            rowsToProcess = [x for x,y in records if y == '#']
            sitesToUpdate = rowsToProcess
        else:
            rowsToProcess = self.getRowsToProcess(selType, siteNum, specimenNum)
            sitesToUpdate = []
        self.processViewableRecords(rowsToProcess, self.parent.locality.genLocality) 
        self.inheritGeoRefFields(sitesToUpdate) # send site data down stream.

    def inheritGeoRefFields(self, sitesToUpdate):
        """ passess all geoReference fields from sites to children records """
        df = self.datatable
        geoRefCols = ['country', 'stateProvince', 'county',
                      'municipality', 'path', 'locality',
                      'decimalLatitude', 'decimalLongitude',
                      'coordinateUncertaintyInMeters',
                      'minimumElevationInMeters']

        for col in geoRefCols:  # verify the column exists before adding to it.
            if col not in df:
                df[col] = ""

        for site in sitesToUpdate:
            #df.loc[df['Col1'].isnull(),['Col1','Col2', 'Col3']] = replace_with_this.values
            newVals = df.loc[(df['siteNumber'] == site) & (df['specimenNumber'] == '#')][geoRefCols]
            df.loc[(df['siteNumber']== site) & (df['specimenNumber'] != '#'), geoRefCols] = newVals.values.tolist()
            QApplication.processEvents()
            self.datatable.update(df)
            self.update(self.datatable)
            self.parent.updateTableView()

    def assignCatalogNumbers(self):
        """If appropriate assigns catalogNumbers over each visible row."""
        #TODO consider checking SERNEC for those Catalog Number's existance
        # IE: http://sernecportal.org/portal/collections/list.php?db=311&catnum=UCHT012345%20-%20UCHT0123555&othercatnum=1
        # Could webscrape a requests return from something like: http://sernecportal.org/portal/collections/list.php?db=311&catnum=UCHT999900%20-%20UCHT999991&othercatnum=1
        # the checkbox for enabling the "Assign catalog numbers" group box.
        assign = self.parent.settings.get('value_assignCatalogNumbers', False)
        if assign:
            rowsToProcess = self.getRowsToProcess(*self.parent.getTreeSelectionType())
            dfOrig = self.datatable.iloc[rowsToProcess, ]
            try:
                df = dfOrig.loc[(dfOrig['specimenNumber'].str.isdigit()) & 
                            (dfOrig['catalogNumber'] == '')].copy()
            except KeyError:  # address a no catalogNumber condition
                df = dfOrig.loc[dfOrig['specimenNumber'].str.isdigit()].copy()
                df['catalogNumber'] = ''
            if len(df) > 0:
                catStartingNum = int(self.parent.settings.get('value_catalogNumberStartingNum'))
                catDigits = int(self.parent.settings.get('value_catalogNumberDigits'))
                catPrefix = self.parent.settings.get('value_catalogNumberPrefix')
                newCatNums = []
                for i in range(len(df.index)):
                    newCatNum = f'{catPrefix}{str(catStartingNum).zfill(catDigits)}'
                    newCatNums.append(newCatNum)
                    catStartingNum += 1 # add 1 to the starting catNumber  
                answer = self.parent.userAsk(f'Assign catalog numbers: {newCatNums[0]} - {newCatNums[-1]} ?', 'Assigning Catalog Numbers')
                if answer is True:  # if the user agreed to assign the catalog numbers
                    df['catalogNumber'] = newCatNums
                    self.datatable.update(df)
                    self.update(self.datatable)
                    self.parent.updateTableView()
                    self.parent.settings.updateStartingCatalogNumber(catStartingNum)
                    # after adding catnums pull in results and check for uniqueness
                    # TODO Clean this function up! It is pretty awful looking..
                    df = self.datatable.iloc[rowsToProcess, ]
                    dfUnique = df.loc[(df['specimenNumber'].str.isdigit()) & 
                                          (df['catalogNumber'] != '')].copy()
                    if not dfUnique['catalogNumber'].is_unique:  # check for duplicated catalog numbers
                        dfNonUnique = dfUnique[dfUnique.duplicated(subset=['catalogNumber'],keep='first')].copy()  # keep the first one as "unique"
                        newCatNums = []
                        for i in range(len(dfNonUnique.index)):  # generate a range of additional new catNums to apply to non-uniques
                            newCatNum = f'{catPrefix}{str(catStartingNum).zfill(catDigits)}'
                            newCatNums.append(newCatNum)
                            catStartingNum += 1
                        answer = self.parent.userAsk(f'Duplicate catalog numbers found! Assign additional {newCatNums[0]} - {newCatNums[-1]} ? Selecting "NO" will keep the duplicate catalog numbers as they are.', 'Assigning Catalog Numbers')
                        if answer is True:  # if the user agreed to assign the catalog numbers
                            dfNonUnique['catalogNumber'] = newCatNums
                            self.datatable.update(dfNonUnique)
                            self.datatable.update(dfNonUnique)
                            self.update(self.datatable)
                            self.parent.updateTableView()
                            self.parent.settings.updateStartingCatalogNumber(catStartingNum)

    def verifyTaxButton(self):
        """ applies verifyTaxonomy over each visible row."""
        # refresh tax settings
        self.addToUndoList('verify taxonomy process')  # set checkpoint in undostack
        self.parent.tax.readTaxonomicSettings()
        rowsToProcess = self.getRowsToProcess(*self.parent.getTreeSelectionType())
        self.processViewableRecords(rowsToProcess, self.parent.tax.verifyTaxonomy)

    def verifyAllButton(self):
        """ applies verifyTaxonomy and geoRef over each visible row"""
        # TODO find logical point in workflow to clean associatedTaxa.
        selType, siteNum, specimenNum = self.parent.getTreeSelectionType()
        xButton = self.parent.statusBar.pushButton_Cancel
        xButton.setEnabled(True)  
        if selType in ['site', 'specimen']:
            sites = [siteNum]
        else:  # it is probably 'allRec'.
            sites = [x for x,y in self.getSiteSpecimens() if y == '#']
        for site in sites:  # enforce a site-by-site workflow
            QApplication.processEvents()
            if xButton.status:  # check for cancel button
                break
            self.parent.selectTreeWidgetItemByName(f'Site {site}')
            self.parent.updateTableView()
            self.parent.expandCurrentTreeWidgetItem()
            QApplication.processEvents()
            self.verifyTaxButton()
            if xButton.status:  # check for cancel button
                break
            self.geoRef()
            if xButton.status:  # check for cancel button
                break
            # check user policy for associatedTaxa dialog
            if self.parent.settings.get('value_associatedAlways', True):
                self.associatedTaxDialog()
            elif self.parent.settings.get('value_associatedOnly', False):
                records = self.getRowsToKeep('site', siteNum = site)
                if len(records) > 2:
                    self.associatedTaxDialog()
            elif self.parent.settings.get('value_associatedNever', False):
                # do nothing
                pass
            else:
                self.associatedTaxDialog()
            
            if xButton.status:  # check for cancel button
                break
            QApplication.processEvents()
        self.parent.testRunLabels()
        xButton.setEnabled(False)
        xButton.status = False
        self.parent.setTreeSelectionByType(selType, siteNum, specimenNum)  # return the selection
            
    def associatedTaxDialog(self):
        """ displays the associatedTaxa dialog and waits for user input """
        waitingForUser = QtCore.QEventLoop()
        self.parent.associatedTaxaWindow.associatedMainWin.button_save.clicked.connect(waitingForUser.quit)
        self.parent.associatedTaxaWindow.associatedMainWin.button_cancel.clicked.connect(waitingForUser.quit)
        self.parent.toggleAssociated() # call user input window and wait
        waitingForUser.exec_()

    def processViewableRecords(self, rowsToProcess, func):
        """ applies a function over each row among rowsToProcess (by index)"""
        #self.parent.statusBar.label_status
        xButton = self.parent.statusBar.pushButton_Cancel
        df = self.datatable.loc[rowsToProcess]
        totRows = len(df)
        pb = self.parent.statusBar.progressBar
        pb.setMinimum(0)
        pb.setMaximum(totRows)
        for c,i in enumerate(rowsToProcess):
            QApplication.processEvents()
            if xButton.status:  # check for cancel button
                break
            rowData = df.loc[i]
            df.loc[i] = func(rowData)
            pb.setValue(c + 1)
            #msg = (f'{c + 1} of {totRows}')
            df.update(rowData)
            self.datatable.update(df)
            self.update(self.datatable)
            self.parent.updateTableView()
        self.parent.form_view.fillFormFields()
        pb.setValue(0)


    def getRowsToProcess(self, selType, siteNum = None, specimenNum = None):
        """ defined for clarity, calls getRowsToKeep with the same args."""
        return self.getRowsToKeep(selType, siteNum, specimenNum)

    def getRowsToKeep(self, selType, siteNum = None, specimenNum = None):
        """ Returns list of row indices associated with inputs """
        df = self.datatable
        #df = df[~df['specimenNumber'].str.contains('#')]
        if selType == 'site':
            rowsToKeep = df[df['siteNumber'] == siteNum].index.values.tolist()
        elif selType == 'specimen':
            rowsToKeep = df[(df['siteNumber'] == siteNum) & (df['specimenNumber'] == specimenNum)].index.values.tolist()
        else:  # otherwise, keep everything (usually "allRec")
            rowsToKeep = df.index.values.tolist()
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
        """ Returns a list of tuples for each siteNumber specimenNumber combination
        called from mainWindow's populateTreeWidget"""
        df = self.datatable
        results = list(zip(df['siteNumber'], df['specimenNumber']))
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
            # this emission causes real time edits to appear on previewPDF window
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
            # check if input is an iNaturalist export
            try:
                # if so, parse those cols.
                if df['url'].str.lower().str.contains('inaturalist.org').any():
                    df = self.convertiNatFormat(df)
            except KeyError:
                # probably not an iNaturalist export.
                pass
            cols = df.columns
            # a list of cols which indicates the data may be from CollectR
            colectoRCols = ['Collector', 'Additional collectors',
                             'Number', 'Infracategory', 'Herbarium Acronym',
                             'Complete Herb. Name 1', 'Complete Herb. Name 2',
                             'Project']
            # check if input is a CollectoR export.
            if all(x in cols for x in colectoRCols):
                # if so, parse those cols.
                df = self.convertColectoRFormat(df)
                cols = df.columns
            # backwards compatability, following change in index field
            if ('otherCatalogNumbers' in cols & 'recordNumber' not in cols):
                df['recordNumber'] = df['otherCatalogNumbers']
                cols = df.columns
            # check if the indices need manually assigned (with user dialog)
            wasAssigned = False  # store if assignments were made.
            if not all(x in cols for x in ['siteNumber', 'specimenNumber']):
                if 'recordNumber' not in cols:
                    assignedDF, dialogStatus = self.getIndexAssignments(df)
                # if the accept button (titled 'Assign') was pressed, assign df
                    if dialogStatus == QDialog.Accepted:
                        df = assignedDF
                        cols = df.columns
                        wasAssigned = True
                    else:
                        return False
            if 'siteNumber' not in cols:  # if the siteNumber does not exist
                df = self.inferSiteSpecimenNumbers(df)  # attempt to infer them
                cols = df.columns
            if 'recordNumber' not in cols:
                df = df.apply(self.inferrecordNumber, axis=1)
                cols = df.columns
            if 'catalogNumber' not in cols:
                df['catalogNumber'] = ''
            #  be sure all cols exist which will later be assumed present.
            df = self.verifyRequiredColsExist(df)
            #  verify sites have a site record, where specimenNumber=='#'
            df = self.verifySiteRecordsExist(df)
            df.fillna('', inplace=True)
            df = self.sortDF(df)  # returns False given an error
            if df is False:
                if wasAssigned:  # if assignments were made, alter error text.
                    text = 'Cannot load records, check your index assignments.'
                else:
                    text = 'Cannot load records.'
                title = 'Error loading records.'
                self.parent.userNotice(text, title)
                return False
            # check if recordedBy is symbiota or DWC format.
            try:
                recordedBy = df['recordedBy']
                if '|' in recordedBy:
                    splitRecordedBy = recordedBy.split('|', 1)
                    if len(splitRecordedBy) == 2:
                        primaryCollector, associatedCollectors = splitRecordedBy
                        associatedCollectors = associatedCollectors.split('|')
                        associatedCollectors = [x.strip() for x in associatedCollectors if x != '']
                        #  rejoin as single, cleaned string.
                        associatedCollectors = ', '.join(associatedCollectors)
                    #if 'associatedCollectors' in cols:
                     # TODO check if associatedCollectors can be overwritten safely.   
            except KeyError:
                pass
            self.update(df)  # this function updates the visible dataframe
            self.parent.populateTreeWidget()
            self.parent.form_view.fillFormFields()
            return True

    def save_CSV(self, fileName=False, df=None):
        """ is triggered by the export records action"""
        if df is None:
            df = self.datatable.copy()
        else:
            df = df.copy()
        # convert empty strings to null values
        df.replace('', np.nan, inplace=True)
        df.dropna(axis=1, how='all', inplace=True)
        readyToSave=False
        if not fileName:
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                    None, "Save CSV", QtCore.QDir.homePath(), "CSV (*.csv)")
        if fileName:  # if a csv was selected, start loading the data.
            if Path(fileName).suffix == '':
                fileName = f'{fileName}.csv'
                readyToSave=True
                if Path(fileName).is_file():
                    readyToSave=False
                    message = f'File named: "{fileName}" already exist! OVERWRITE this file?'
                    title = 'Save As'
                    answer = self.parent.userAsk(message, title)
                    if answer:
                        readyToSave=True
            else:
                readyToSave = True
            if readyToSave:
                df.fillna('', inplace=True)  # convert nullvalues empty strings
                df.to_csv(fileName, encoding='utf-8', index=False)
                return True
            else:
                return False
                

    def export_CSV(self, fileName=None, df=None):
        """ is triggered by the export records action"""
        if df is None:
            df = self.datatable.copy()
        else:
            df = df.copy()
        # convert empty strings to null values
        df.replace('', np.nan, inplace=True)
        df.dropna(axis=1, how='all', inplace=True)
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                    None, "Save CSV", QtCore.QDir.homePath(), "CSV (*.csv)")
        if fileName:  # if a csv was selected, start loading the data.
            drop_col_Names = ['siteNumber', 'specimenNumber']
            keep_col_Names = [x for x in df.columns if x not in drop_col_Names]
            df = df[keep_col_Names]
            df.fillna('', inplace=True)  # convert nullvalues empty strings
            df.to_csv(fileName, encoding='utf-8', index=False)
            return True

    def verifyRequiredColsExist(self, df):
        """ given a dataFrame, verifies that the expected columns exist."""
        reqCols = [
            'scientificName',
            'scientificNameAuthorship',
            'taxonRemarks',
            'identifiedBy',
            'dateIdentified',
            'identificationReferences',
            'identificationRemarks',
            'collector',
            'associatedCollectors',
            'eventDate',
            'habitat',
            'substrate',
            'occurrenceRemarks',
            'associatedTaxa',
            'dynamicProperties',
            'reproductiveCondition',
            'cultivationStatus',
            'establishmentMeans',
            'lifeStage',
            'individualCount',
            'country',
            'stateProvince',
            'county',
            'municipality',
            'path',
            'locality',
            'decimalLatitude',
            'decimalLongitude',
            'coordinateUncertaintyInMeters',
            'minimumElevationInMeters',
            'labelProject']
        presentCols = df.columns
        for col in reqCols:
            #  if a required col is not present, add and fill it with empty str
            if col not in presentCols:
                df[col] = ''
        return df

    def verifySiteRecordsExist(self, df):
        """ iterates over each site number, and ensures there is a site level
        record present to hold the site data. """
        #  If data appears to have been made in collNotes, can skip iteration.
        siteNums = df['siteNumber'].unique().tolist()
        siteRecords = df.loc[df['specimenNumber'] == '#']
        if len(siteRecords) >= len(siteNums):
            return df
        # if the # of siteRecords < # of siteNumbers, there is an issue and
        # it is worth the time to iterate over the DF, and verify each site#
        newRows = []
        pb = self.parent.statusBar.progressBar
        pb.setMinimum(0)
        pb.setMaximum(len(siteNums))

        for c, siteNum in enumerate(siteNums):
            siteRecs = df.loc[df['siteNumber'] == siteNum].copy()
            siteRow = siteRecs.loc[siteRecs['specimenNumber'] == '#']
            # if there is a siteRow, move on to the next site.
            if len(siteRow) > 0:
                continue
            # otherwise, generate one.
            strCols = ['eventDate',
                       'country',
                       'stateProvince',
                       'county',
                       'municipality',
                       'path',
                       'locality',
                       'localitySecurity',
                       'collector',
                       'associatedCollectors',
                       'verbatimEventDate',
                       'habitat',
                       'associatedOccurrences',
                       'associatedTaxa',
                       'samplingEffort']
            # strip out site string cols which are not in source data
            # requird cols are verified as present later.
            strCols = [x for x in strCols if x in siteRecs.columns]

            numericCols = ['decimalLatitude',
                           'decimalLongitude',
                           'coordinateUncertaintyInMeters',
                           'minimumElevationInMeters']

            if len(siteRecs) > 0:
                # take the mode of the specimen values
                newRow = siteRecs[strCols]
                newRow = newRow.mode()[:1]
                newRow['specimenNumber'] = '#'
                newRow['siteNumber'] = siteNum
                # in the case of coordinate values, take the mean of the group
                # This could be problematic if they assigned distant sites.
                # But honestly, they'd have to assign them to the same site manually to ensure that.
                for numericCol in numericCols:
                    try:
                        newVals = siteRecs[numericCol].astype(float).mean().astype(str)
                    except ValueError:
                        # probably an empty value
                        continue
                    if str(newVals)[::-1].find('.') > 5:
                        newVals = '{:.5f}'.format(float(newVals))
                    newRow[numericCol] = newVals
                newRow = newRow
                pb.setValue(c + 1)
                QApplication.processEvents()
            # add results to the list of rows to be added
            newRow['specimenNumber'] = '#'
            newRow['siteNumber'] = siteNum
            newRows.append(newRow)
        # if we have any rows to be added to the df, do so
        if len(newRows) > 0:
            df = df.append(newRows, ignore_index=True, sort=False)
        
        pb.setValue(0)
        return df            

    def getIndexAssignments(self, df):
        """ calls the dialog defined in importindexdialog.py and retrieves or
        generates the user defined siteNumber & specimenNumber columns."""
        dialog = importDialog(self, df)
        result = dialog.exec_()
        resultDF = dialog.indexAssignments()
        # return the assignedDF and boolean if the dialog status was accepted.
        return (resultDF, result == QDialog.Accepted)

    def sortDF(self, df):
        """ accepts a dataframe and returns it sorted in an ideal manner. 
        Expects the dataframe to have siteNumber and specimenNumber columns """

        try:
            df['sortSpecimen'] = df['specimenNumber'].str.replace('#','0').astype(int)
            df['sortSite'] = df['siteNumber'].str.replace('','0').astype(int)
        except:
            return False
        df.sort_values(by=['sortSite', 'sortSpecimen'], inplace=True, ascending=True)
        df.drop(columns = ['sortSite', 'sortSpecimen'], inplace = True)
        df.reset_index(drop = True, inplace = True)
        return df

    def inferrecordNumber(self, rowData):
        """ assigns otherCatalogNumber based on siteNumber & specimenNumber """
        try:
            rowData['recordNumber'] = f"{rowData['siteNumber']}-{rowData['specimenNumber']}"
        except IndexError:
            pass
        return rowData

    def inferSiteSpecimenNumbers(self, df):
        """ attempts to infer a siteNumber and specimenNumber of an incoming df """
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
            df['siteNumber'] = df['recordNumber'].transform(lambda x: siteNumExtract(x))
            df['specimenNumber'] = df['recordNumber'].transform(lambda x: specimenNumExtract(x))
        except IndexError:
            # incase there are no recordNumber
            pass

        return df

    def convertiNatFormat(self, df):
        """converts iNaturalist formatted data into a compatable DWC format.
        This does not infer site numbers."""
        
        colNames = df.columns
        # private_latitude,private_longitude may be used in place if coordinates_obscured == 'true'
        if ('coordinates_obscured' in colNames & 
            df['coordinates_obscured'] == 'true'):
            # for key value in following dict. where keys are private coordinate columns
            for k, v in {
            'private_latitude': 'latitude',
            'private_longitude': 'longitude',
            'private_positional_accuracy': 'positional_accuracy'}.items():
                # essentially, if the private coordinate fields are filled, pull them into the non-private fields 
                # this allows those fields to be treated similarly in the future.
                if df[k] != '':
                    df[v] = df[k]
            # TODO add dialog, or consideration for "informationWithheld" given this condition
            # TODO add localitySecurity consideration for this condition
        # if it was indicated as cultivated in iNat, convert results ahead of renaming.
        if ('captive_cultivated' in colNames &
            df['captive_cultivated'] == 'true'):
            df['captive_cultivated'] = 'cultivated'

        colNameMap = {
                "observed_on": "eventDate",
                "url": "associatedMedia",
                "latitude": "decimalLatitude",
                "longitude": "decimalLongitude",
                "positional_accuracy": "coordinateUncertaintyInMeters",
                "scientific_name": "scientificName",
                "description": "occurrenceRemarks",
                "captive_cultivated": "establishmentMeans"
                }
        df.rename(colNameMap, axis='columns', inplace=True)

        return df

    def convertColectoRFormat(self, df):
        """ converts ColectoR formatted data into a compatable DWC format.
        This does not infer site numbers. For details on ColectoR see:
        Maya-Lastra, C.A. 2016, doi:10.3732/apps.1600035 """

        # create eventDate from existing cols        
        df['eventDate'] = ['-'.join([x,y,z]) for x, y, z in zip(df['Year'], df['Month'], df['Day'])]
        # strip non-numerics out of GPS accuracy value
        df['GPS Accuracy'] = df['GPS Accuracy'].str.replace('± ','').str.replace(' m','')        
        # join multiple terms into scientificName
        # get all terms into a list
        taxonTerms = df[['Genus','Species','Infracategory','InfraTaxa']].add(' ').fillna('').values.tolist()
        # replace empty spaces to NaN
        sciNames = pd.Series([''.join(x).strip(' ') for x in taxonTerms]).replace('^$', np.nan, regex=True)
        # replace NaN to ''
        sciNames = sciNames.where(sciNames.notnull(), '')
        df['scientificName'] = sciNames
        # join multiple terms into occurrenceRemarks
        # get all terms into a list
        notesTerms = df[['Description','Notes','Additional_notes']].add(' ').fillna('').values.tolist()
        # replace empty spaces to NaN
        occNotes = pd.Series([''.join(x).strip(' ') for x in notesTerms]).replace('^$', np.nan, regex=True)
        # replace NaN to ''
        occNotes = occNotes.where(occNotes.notnull(), '')
        df['occurrenceRemarks'] = occNotes
        # copy Number, so when choosing index names "Number" is still present.
        df['recordNumber'] = df['Number']
        # assign rename map over directly translatable cols
        colNameMap = {'Collector': 'recordedBy',
                      'Additional collectors	': 'associatedCollectors',
                      'Country': 'country',
                      'State': 'stateProvince',
                      'Locality': 'locality',
                      'Latitude': 'decimalLatitude',
                      'Longitude': 'decimalLongitude',
                      'GPS Accuracy': 'coordinateUncertaintyInMeters',
                      'Altitude': 'minimumElevationInMeters',
                      'Project': 'labelProject'}
        df.rename(colNameMap, axis='columns', inplace=True)

        return df

    def new_Records(self, skipDialog = False):
        # is triggered by the action_new_Records.
        """Clears all the data and makes a new table
        if skipDialog is True, it won't ask."""
        qm = QMessageBox
        if skipDialog:
            ret = QMessageBox.Yes
        else:
            ret = qm.question(self.parent, '', 'Load a blank data set? (any unsaved progress will be lost)', qm.Yes | qm.No)
        if ret == qm.Yes:
            if not skipDialog:
                self.addToUndoList(f'loaded new, blank site data')  # set checkpoint in undostack
            newDFDict = {
            'siteNumber':['1','1'],
            'specimenNumber':['#','1'],
            'recordNumber':['1-#','1-1'],
            'catalogNumber':['',''],
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
            'path':['',''],
            'locality':['',''],
            'localitySecurity':['',''],
            'decimalLatitude':['',''],
            'decimalLongitude':['',''],
            'coordinateUncertaintyInMeters':['',''],
            'verbatimCoordinates':['',''],
            'minimumElevationInMeters':['',''],
            'verbatimElevation':['',''],
            'duplicateQuantity':['',''],
            'labelProject':['','']}
    
            df = pd.DataFrame.from_dict(newDFDict)
            df.fillna('') # make any nans into empty strings.
            self.update(df)  # this function actually updates the visible dataframe
            self.parent.populateTreeWidget()
            self.parent.form_view.fillFormFields()
        return

