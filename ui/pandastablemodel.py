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
from reportlab.platypus.doctemplate import LayoutError


import pandas as pd

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
        if len(self.undoList) > 20:  # be sure not to grow too big
            self.undoList = self.undoList[20:]

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
            newSiteNum = max(pd.to_numeric(df['site#'], errors = 'coerce')) + 1
        except ValueError:
            newSiteNum = 1
        self.addToUndoList(f'added site {newSiteNum}')  # set checkpoint in undostack
        rowData = {'otherCatalogNumbers':f'{newSiteNum}-#', 
                   'site#':f'{newSiteNum}',
                   'specimen#':'#'}
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
        if selType == 'site':
            try:  # try to make the new row data
                spNums = df[(df['site#'] == siteNum) &
                            (df['specimen#'] != '#')]['specimen#']
                newSpNum = max(pd.to_numeric(spNums, errors='coerce')) + 1
            except ValueError:
                newSpNum = 1
            newRowData = df[(df['site#'] == siteNum) &
                            (df['specimen#'] == '#')].copy()
            newRowData['specimen#'] = f'{newSpNum}'
            catNum =  f'{siteNum}-{newSpNum}'
            self.addToUndoList(f'added specimen {catNum}')  # set checkpoint in undostack
            newRowData['otherCatalogNumbers'] = catNum
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
                spNums = df[(df['site#'] == siteNum) &
                            (df['specimen#'] != '#')]['specimen#']
                newSpNum = max(pd.to_numeric(spNums, errors='coerce')) + 1
            except ValueError:
                newSpNum = 2
            newRowData = df[(df['site#'] == siteNum) &
                            (df['specimen#'] == specimenNum)].copy()
            newRowData['specimen#'] = f'{newSpNum}'
            catNum =  f'{siteNum}-{newSpNum}'
            newRowData['otherCatalogNumbers'] = catNum
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
            newDF = df[df['site#'] != siteNum].copy()
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
            newDF = df[~((df['site#'] == siteNum) & (df['specimen#'] == specimenNum))].copy()
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
        by updateTableView to get the index of "specimen#" for sorting."""
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
            #if datum.get('specimen#') not in ['#','!AddSITE']:   #keep out the site level records!
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
#                if len(associatedTaxaItems) > 10:   #if it is too large, trunicate it at 15, and append "..." to indicate trunication.
#                    record['associatedTaxa'] = ', '.join(associatedTaxaItems[:10])+' ...'   
        return records

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
        for site in sitesToUpdate:
            #df.loc[df['Col1'].isnull(),['Col1','Col2', 'Col3']] = replace_with_this.values
            newVals = df.loc[(df['site#'] == site) & (df['specimen#'] == '#')][geoRefCols]
            df.loc[(df['site#']== site) & (df['specimen#'] != '#'), geoRefCols] = newVals.values.tolist()
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
            df = dfOrig.loc[(dfOrig['specimen#'].str.isdigit()) & 
                        (dfOrig['catalogNumber'] == '')].copy()
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
                    dfUnique = df.loc[(df['specimen#'].str.isdigit()) & 
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
        self.parent.tax.onFirstRow = True
        self.parent.tax.readTaxonomicSettings()
        rowsToProcess = self.getRowsToProcess(*self.parent.getTreeSelectionType())
        self.processViewableRecords(rowsToProcess, self.parent.tax.verifyTaxonomy)

    def verifyAllButton(self):
        """ applies verifyTaxonomy and geoRef over each visible row"""
        # TODO find logical point in workflow to clean associatedTaxa.
        self.geoRef()
        self.verifyTaxButton()
        self.parent.testRunLabels()
            
    def processViewableRecords(self, rowsToProcess, func):
        """ applies a function over each row among rowsToProcess (by index)"""
        #self.parent.statusBar.label_status
        xButton = self.parent.statusBar.pushButton_Cancel
        xButton.setEnabled(True)
        df = self.datatable.loc[rowsToProcess]
        totRows = len(df)
        pb = self.parent.statusBar.progressBar
        pb.setMinimum(0)
        pb.setMaximum(totRows)
        for c,i in enumerate(rowsToProcess):
            QApplication.processEvents()
            if xButton.status:  # check for cancel button
                break
            rowData = df.loc[[i]]
            rowData.apply(func,1)
            pb.setValue(c + 1)
            #msg = (f'{c + 1} of {totRows}')
            df.update(rowData)
            self.datatable.update(df)
            self.update(self.datatable)
            self.parent.updateTableView()
        #self.parent.statusBar().removeWidget(self.progressBar)
        xButton.setEnabled(False)
        xButton.status = False
        self.parent.form_view.fillFormFields()
        pb.setValue(0)


    def getRowsToProcess(self, selType, siteNum = None, specimenNum = None):
        """ defined for clarity, calls getRowsToKeep with the same args."""
        return self.getRowsToKeep(selType, siteNum, specimenNum)

    def getRowsToKeep(self, selType, siteNum = None, specimenNum = None):
        """ Returns list of row indices associated with inputs """
        df = self.datatable
        #df = df[~df['specimen#'].str.contains('#')]
        if selType == 'site':
            rowsToKeep = df[df['site#'] == siteNum].index.values.tolist()
        elif selType == 'specimen':
            rowsToKeep = df[(df['site#'] == siteNum) & (df['specimen#'] == specimenNum)].index.values.tolist()
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
            if ~df.columns.isin(['site#']).any():  # if the site# does not exist:
                df = self.inferSiteSpecimenNumbers(df)  # attempt to infer them
            df = self.sortDF(df)
            df.fillna('') # make any nans into empty strings.
            self.update(df)  # this function actually updates the visible dataframe 
            self.parent.populateTreeWidget()
            self.parent.form_view.fillFormFields()
            return True

    def save_CSV(self, fileName = None, df = None):
        # is triggered by the action_Save:
        if df is None:
            df = self.datatable
        else:
            df = df.copy()
        if fileName is None:
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save CSV",
                                                                QtCore.QDir.homePath(), "CSV (*.csv)")
        if fileName:  # if a csv was selected, start loading the data.
            drop_col_Names = ['site#', 'specimen#']
            keep_col_Names = [x for x in df.columns if x not in drop_col_Names]
            df = df[keep_col_Names]
            df.fillna('') # make any nans into empty strings.
            df.to_csv(fileName, encoding = 'utf-8', index = False)
            return True

    def sortDF(self, df):
        """ accepts a dataframe and returns it sorted in an ideal manner. 
        Expects the dataframe to have site# and specimen# columns """

        df['sortSpecimen'] = df['specimen#'].str.replace('#','0').astype(int)
        df['sortSite'] = df['site#'].str.replace('','0').astype(int)
        df.sort_values(by=['sortSite', 'sortSpecimen'], inplace=True, ascending=True)
        df.drop(columns = ['sortSite', 'sortSpecimen'], inplace = True)
        df.reset_index(drop = True, inplace = True)
        return df

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
            ret = qm.question(self.parent, '', 'Load a blank data set? (any unsaved progress will be lost)', qm.Yes | qm.No)
        if ret == qm.Yes:
            if not skipDialog:
                self.addToUndoList(f'loaded new, blank site data')  # set checkpoint in undostack
            newDFDict = {
            'site#':['1','1'],
            'specimen#':['#','1'],
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
            df['-'] = '-' # add in the little "-" seperator.
            df.fillna('') # make any nans into empty strings.
            self.update(df)  # this function actually updates the visible dataframe
            self.parent.populateTreeWidget()
            self.parent.form_view.fillFormFields()
        return

