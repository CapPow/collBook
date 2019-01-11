# found at: https://github.com/Beugeny/python_test/blob/d3e21dc075d9cef8dca323d281cbbdb4765233c6/Test1.py

import sys
import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QTreeWidgetItemIterator
from PyQt5.QtWidgets import QAbstractItemView

from reportlab.platypus.doctemplate import LayoutError

from ui.printlabels import LabelPDF
from ui.pandastablemodel import PandasTableModel
from ui.locality import locality

from PyQt5.QtCore import Qt

#import uiFunctions

# nice idea to use the maintained spyder.widgets for dataframe viewing
#from spyder.widgets.variableexplorer.dataframeeditor import DataFrameModel

import qdarkstyle
from ui.TestUI import Ui_MainWindow
from ui.settingsdialog import settingsWindow
        
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
        # generate an instance of the settingsWindow 
        self.settings = settingsWindow(self)
        # Linking functions to buttons in the UI
        w.action_Open.triggered.connect(m.open_CSV)
        w.action_New_Records.triggered.connect(m.new_Records)
        w.action_Exit.triggered.connect(lambda: sys.exit(app.exec_()))     
        w.action_Settings.triggered.connect(self.toggleSettings)    
        w.action_Reverse_Geolocate.triggered.connect(self.geoRef)
        m.dataChanged.connect(self.populateTreeWidget)
        # send the settings object along with the pdf constructor        
        p = LabelPDF(self.settings)
        #todo clean up the self definitions        
        self.w = w  # make the mainWindow accessible
        self.p = p  # make the pdfViewer accessible
        self.m = m  # make the PandasTableModel accessible
        self.pdf_preview = w.pdf_preview  # make the pdfViewer accessible
        self.table_view = w.table_view # make the table_view accessible
        self.tree_widget = w.tree_widget# make the tree_widget accessible
        self.populateTreeWidget()
        self.locality = locality(self)

    def toggleSettings(self):
        if self.settings.isHidden():
            self.settings.show()
        else:
            self.settings.hide()

    def geoRef(self):
        """ applies a function over each row among those selected by the
        treeSelectionType """
        
        selType, siteNum, specimenNum = self.getTreeSelectionType()
        rowsToProcess = self.m.getRowsToProcess(selType, siteNum, specimenNum)
        self.m.processViewableRecords(rowsToProcess, self.locality.genLocality)        
        

    def getTreeSelectionType(self):
        """ checks the tree_widget's type of selection """
        try:
            itemSelected = self.tree_widget.currentItem()
            text = itemSelected.text(0).split('(')[0].strip()
        except AttributeError:  # if not force "All Records"
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
        """ updates the table_view after tree_widget's selection change """
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
                topVisible = min(topVisible)
                self.table_view.selectRow(topVisible)
            except ValueError:
                self.table_view.clearSelection()
            self.updatePreview()

    def selectTreeWidgetItemByName(self, name):
        print(name)
        iterator = QTreeWidgetItemIterator(self.tree_widget, QTreeWidgetItemIterator.All)
        while iterator.value():
            item = iterator.value()
            if item.text(0) == name:
                #TODO currently it updates properly IF it has a site-specimen value not for site values
                self.tree_widget.setCurrentItem(item,1)
                break
            iterator +=1
        #self.updateTableView()

    def updatePreview(self):
        """ updates the pdf preview window after the vertical header is clicked"""
        #TODO modify this to be called from within the pdfviewer class
        tableSelection = self.w.table_view.selectionModel().selectedRows()
        if tableSelection:
            index = tableSelection[0].row()
            rowData = self.m.retrieveRowData(index)
            rowData = self.m.dataToDict(rowData)
            try:
                pdfBytes = self.p.genLabelPreview(rowData)  # retrieves the pdf in Bytes
            except LayoutError:
                self.pdf_preview.load_label_OversizeWarning()
                return
        else:
            pdfBytes = None
        self.pdf_preview.load_preview(pdfBytes)  # starts the loading display process        

    def populateTreeWidget(self):
        """ given a list of tuples structured as(siteNum, specimenNum),
        populates the TreeWidget with the records nested within the sites."""
        # first clear the tree    
        
        # store the current selection
        itemSelected = self.tree_widget.currentItem()
        try:
            text = itemSelected.text(0).split('(')[0].strip()
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