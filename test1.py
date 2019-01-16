# found at: https://github.com/Beugeny/python_test/blob/d3e21dc075d9cef8dca323d281cbbdb4765233c6/Test1.py

import sys
import os
from io import StringIO
import pandas as pd

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QTreeWidgetItemIterator, QItemDelegate, QCompleter
from PyQt5.QtWidgets import QAbstractItemView

from reportlab.platypus.doctemplate import LayoutError

from ui.printlabels import LabelPDF
from ui.pandastablemodel import PandasTableModel
from ui.locality import locality

from PyQt5.QtCore import Qt, QFile

#import uiFunctions

# nice idea to use the maintained spyder.widgets for dataframe viewing
#from spyder.widgets.variableexplorer.dataframeeditor import DataFrameModel

import qdarkstyle
from ui.TestUI import Ui_MainWindow
from ui.settingsdialog import settingsWindow
from ui.taxonomy import taxonomicVerification
from ui.associatedtaxa import associatedTaxaMainWindow
from ui.formview import formView
        

class editorDelegate(QItemDelegate):
    """solution to the table_view editor clearing pre-existing cell values
    ref: https://stackoverflow.com/questions/39387842/not-displaying-old-value-when-editing-cell-in-a-qtablewidget"""
    def setEditorData(self,editor,index):
        editor.setAutoFillBackground(True)
        editor.setText(str(index.data()))

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        w = Ui_MainWindow()
        w.setupUi(self)
        
        m = PandasTableModel()
        #default empty
        #m.update(pd.DataFrame())
        #default blank sheet
        m.new_Records(True)
        # apply the custom model class to the existing QTableView object
        w.table_view.setModel(m)
        delegate = editorDelegate
        w.table_view.setItemDelegate(delegate(w.table_view)) # use flipped proxy delegate
        # generate an instance of the settingsWindow 
        settings = settingsWindow(self)
        self.settings = settings
       # generate an instance of the associatedTaxaWindow
        associatedTaxaWindow = associatedTaxaMainWindow(self)
        self.associatedTaxaWindow = associatedTaxaWindow
        
        lineEdit_sciName = w.lineEdit_sciName
        self.lineEdit_sciName = lineEdit_sciName
        self.updateAutoComplete()
        
        form_view = w.form_view_tabWidget
        form_view.init_ui(w)
        
        # generate an instance of the taxonomic verifier
        self.tax = taxonomicVerification(self.settings)
        # Linking functions to buttons in the UI
        w.action_Open.triggered.connect(m.open_CSV)
        w.action_Save_As.triggered.connect(m.save_CSV)
        w.action_New_Records.triggered.connect(m.new_Records)
        w.action_Exit.triggered.connect(lambda: sys.exit(app.exec_()))     
        w.action_Settings.triggered.connect(self.toggleSettings)  
        w.button_associatedTaxa.clicked.connect(self.toggleAssociated)
        w.action_Reverse_Geolocate.triggered.connect(self.geoRef)
        w.action_Verify_Taxonomy.triggered.connect(self.verifyTaxButton)
        w.action_Export_Labels.triggered.connect(self.exportLabels)
        
        
        m.dataChanged.connect(self.populateTreeWidget)
        
        p = LabelPDF(self.settings)
        #todo clean up the self definitions        
        self.w = w  # make the mainWindow accessible
        self.p = p  # make the label Maker accessible
        self.m = m  # make the PandasTableModel accessible
        self.pdf_preview = w.pdf_preview  # make the pdfViewer accessible
        self.table_view = w.table_view # make the table_view accessible
        self.tree_widget = w.tree_widget# make the tree_widget accessible
        self.populateTreeWidget()
        self.form_view = form_view #make self.form_view_tabWidget accessible
        self.locality = locality(self)

    def toggleSettings(self):
        if self.settings.isHidden():
            self.settings.show()
        else:
            self.settings.hide()
    
    def toggleAssociated(self):
        if self.associatedTaxaWindow.isHidden():
            self.associatedTaxaWindow.show()
            self.associatedTaxaWindow.populateAssociatedTaxa()
        else:
            self.associatedTaxaWindow.associatedList.clear()
            self.associatedTaxaWindow.hide()

    def geoRef(self):
        """ applies genLocality over each row among those selected."""
        selType, siteNum, specimenNum = self.getTreeSelectionType()
        rowsToProcess = self.m.getRowsToProcess(selType, siteNum, specimenNum)
        self.m.processViewableRecords(rowsToProcess, self.locality.genLocality)        
        
    def verifyTaxButton(self):
        """ applies verifyTaxonomy over each row among those selected."""
        # refresh tax settings
        self.tax.onFirstRow = True
        self.tax.readTaxonomicSettings()
        selType, siteNum, specimenNum = self.getTreeSelectionType()
        rowsToProcess = self.m.getRowsToProcess(selType, siteNum, specimenNum)
        self.m.processViewableRecords(rowsToProcess, self.tax.verifyTaxonomy)

    def exportLabels(self):
        """ bundles records up and passes them to printlabels.genPrintLabelPDFs() """
        selType, siteNum, specimenNum = self.getTreeSelectionType()
        rowsToProcess = self.m.getRowsToProcess(selType, siteNum, specimenNum)
        outDF = self.m.datatable.iloc[rowsToProcess, ]
        outDict = self.m.dataToDict(outDF)
        self.p.genPrintLabelPDFs(outDict)
                
        
    def getTreeSelectionType(self):
        """ checks the tree_widget's type of selection """
        try:
            itemSelected = self.tree_widget.currentItem()
            text = itemSelected.text(0).split('(')[0].strip()
        except AttributeError as e:  # if not force "All Records"
            text = "All Records"
        siteNum = None
        specimenNum = None
        if text == "All Records":
            selType = 'allRec'
        elif "Site" in text:
            selType = 'site'
            siteNum = text.replace('Site ','').strip()
        elif "-" in text:
            selType = 'specimen'
            siteNum, specimenNum = text.split('-')
            
        return selType, siteNum, specimenNum
       
    def updateTableView(self):
        """ updates the table_view, and form_view's current tab
        called after tree_widget's selection change """
        # first reset the view
        rowNums = range(self.m.rowCount())
        for row in rowNums:
            self.table_view.showRow(row)
        # then get the tree's selection type
        selType, siteNum, specimenNum = self.getTreeSelectionType()
        rowsToHide = self.m.getRowsToHide(selType, siteNum, specimenNum)
        for row in rowsToHide:
            self.table_view.hideRow(row)
        specimenColumnIndex = self.m.columnIndex('specimen#')
        #TODO fix this sort, currently uses alphanumeric (ie: 100, 2, 30). Should be numeric Ascending
        self.table_view.sortByColumn(specimenColumnIndex, Qt.AscendingOrder)
        if selType != 'allRec':
            topVisible = [x for x in rowNums if x not in rowsToHide]
            try:
                #TODO make consideration for avoiding this if the last action was an edit.
                topVisible = min(topVisible)
                self.table_view.selectRow(topVisible)
            except ValueError:
                self.table_view.clearSelection()
            self.updatePreview()
        
        #print( self.w.form_view_tabWidget.currentIndex())
        if selType == 'site':
            self.w.form_view_tabWidget.setTabEnabled(0, False) #disable all records
            self.w.form_view_tabWidget.setTabEnabled(1, True) #enable site data
            self.w.form_view_tabWidget.setTabEnabled(2, False) #disable specimen data
            self.w.form_view_tabWidget.setCurrentIndex(1) #swap to site tab
        elif selType == 'specimen':
            self.w.form_view_tabWidget.setTabEnabled(0, False) #disable all records
            self.w.form_view_tabWidget.setTabEnabled(1, True) #enable site data
            if not self.w.form_view_tabWidget.isTabEnabled(2): # if specimen tab is not enabled
                self.w.form_view_tabWidget.setTabEnabled(2, True) #enable specimen tab
                self.w.form_view_tabWidget.setCurrentIndex(2) #swap to specimen tab
            #if self.w.form_view_tabWidget.currentIndex() == 0:
                
        else: #  all records
            self.w.form_view_tabWidget.setTabEnabled(0, True) #all records
            self.w.form_view_tabWidget.setTabEnabled(1, False) #site data
            self.w.form_view_tabWidget.setTabEnabled(2, False) #specimen data
            self.w.form_view_tabWidget.setCurrentIndex(0) #all records

    def selectTreeWidgetItemByIndex(self, i):
        """ helper function called when form_view's tab index is clicked Is 
        intended to change the user's view to all records when the all records
        tab is clicked """
        if i == 0:
            self.selectTreeWidgetItemByName('All Records')

    def selectTreeWidgetItemByName(self, name):
        iterator = QTreeWidgetItemIterator(self.tree_widget, QTreeWidgetItemIterator.All)
        while iterator.value():
            item = iterator.value()
            if item.text(0) == name:
                self.tree_widget.setCurrentItem(item,1)
                break
            iterator +=1
        #self.updateTableView()
        
    def updatePreview(self):
        """ updates the pdf preview window and the form_view """
        #TODO modify this to be called from within the pdfviewer class
        tableSelection = self.w.table_view.selectionModel().selectedRows()
        if tableSelection:
            index = tableSelection[0].row()
            rowData = self.m.retrieveRowData(index)
            rowData = self.m.dataToDict(rowData)

            # push data into form_view
            self.form_view.fillFormFields(rowData)
            
            try:
                pdfBytes = self.p.genLabelPreview(rowData)  # retrieves the pdf in Bytes
            except LayoutError:
                self.pdf_preview.load_label_OversizeWarning()
                return
        else:
            pdfBytes = None
        self.pdf_preview.load_preview(pdfBytes)  # starts the loading display process        

    def updateAutoComplete(self):
        """ updates the Completer's reference text based on the kingdom """

        value_Kingdom = self.settings.get('value_Kingdom', 'Plantae')
        if value_Kingdom == 'Plantae':
            nameCol = 'complete_name'
        if value_Kingdom == 'Fungi':
            nameCol = 'Taxon_name'
        stream = QFile(f':/rc_/{value_Kingdom}_Reference.csv')
        if stream.open(QFile.ReadOnly):
            df = StringIO(str(stream.readAll(), 'utf-8'))
            stream.close()
        wordList = pd.read_csv(df, encoding = 'utf-8', dtype = 'str')
        wordList = sorted(wordList[nameCol].tolist())      
        
        completer = QCompleter(wordList, self.lineEdit_sciName)
        self.lineEdit_sciName.setCompleter(completer)

        completerAssociated = QCompleter(wordList, self.associatedTaxaWindow.lineEdit_newAssociatedTaxa)
        self.associatedTaxaWindow.associatedMainWin.lineEdit_newAssociatedTaxa.setCompleter(completerAssociated)
       
    def populateTreeWidget(self):
        """ given a list of tuples structured as(siteNum, specimenNum),
        populates the TreeWidget with the records nested within the sites."""

        # store the current selection
        itemSelected = self.tree_widget.currentItem()
        try:
            text = itemSelected.text(0)
        except AttributeError:
            text = 'All Records'
        self.tree_widget.clear()
        fieldNumbers = self.m.getSiteSpecimens()
        siteNumbers = list(set([x[0] for x in fieldNumbers]))
        try:
            siteNumbers.sort(key = int)
        except ValueError:
            pass
        # build a hierarchical structure of QTreeWidgetItem(s) to fill the tree with
        self.tree_widget.addTopLevelItem(QTreeWidgetItem(["All Records"]))
        for siteNum in siteNumbers:
            specimenNumbers = list(set([y for x, y in fieldNumbers if x == siteNum and y != '#']))
            specimenNumbers.sort(key = int)
            site = QTreeWidgetItem([f'Site {siteNum} ({len(specimenNumbers)})'])
            siteChildren = []
            for i in specimenNumbers:
                # where i is a specimen number for a site
                label = [f'{siteNum}-{i}']
                child = QTreeWidgetItem(label)
                siteChildren.append(child)
            site.addChildren(siteChildren)
            # add the list of sites (with children) to the master list
            self.tree_widget.addTopLevelItems([site])
        # return to the selection (if it exists)
        self.selectTreeWidgetItemByName(text)

    
app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
w = MyWindow()
w.show()

sys.exit(app.exec_())