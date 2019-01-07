# found at: https://github.com/Beugeny/python_test/blob/d3e21dc075d9cef8dca323d281cbbdb4765233c6/Test1.py

import sys
import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem

from ui.printlabels import LabelPDF
from ui.pandastablemodel import PandasTableModel


#import uiFunctions

# nice idea to use the maintained spyder.widgets for dataframe viewing
#from spyder.widgets.variableexplorer.dataframeeditor import DataFrameModel

import qdarkstyle
from ui.TestUI import Ui_MainWindow

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
        # Linking functions to buttons in the UI
        # functions which are being connected are (**NOT**) found in 'uiFunctions.py'
        w.action_Open.triggered.connect(m.open_CSV)
        w.action_New_Records.triggered.connect(m.new_Records)
        w.action_Exit.triggered.connect(lambda: sys.exit(app.exec_()))
        
        m.dataChanged.connect(self.populateTreeWidget)

        p = LabelPDF()  # construct the label maker
        
        self.w = w  # make the mainWindow accessible
        self.p = p  # make the pdfViewer accessible
        self.m = m  # make the PandasTableModel accessible
        self.pdf_preview = w.pdf_preview  # make the pdfViewer accessible
        self.tree_widget = w.tree_widget # make the treeWidget accessible
        self.table_view = w.table_view # make the table_view accessible
        self.tree_widget = w.tree_widget# make the tree_widget accessible
        
        self.populateTreeWidget()

    def updateTableView(self):
        """ updates the table_view after tree_widget's selection change """
        # first reset the view
        rowNums = range(self.m.rowCount())
        for row in rowNums:
            self.table_view.showRow(row)
        # then see if there is a selected row
        try:  # if so, pull it's text
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
        rowsToHide = self.m.getRowsToHide(selType, siteNum, specimenNum)
        for row in rowsToHide:
            self.table_view.hideRow(row)

#TODO Fix the selection of the top row
#        if selType != 'allRec':
#            topVisible = [x for x in rowNums if x not in rowsToHide]
#            topVisible.remove(0)
#            topVisible = min(topVisible)
#            self.table_view.selectRow(topVisible)
#            self.updatePreview()

    def updatePreview(self):
        """ updates the pdf preview window after the vertical header is clicked"""
        #self.parent some way to get the dataframe data
    
        # note the up then back down addressing here:
            # up to parentof this object, then back down to table_view
        tableSelection = self.w.table_view.selectionModel().selectedRows()
        if tableSelection:
            index = tableSelection[0].row()
            rowData = self.m.retrieveRowData(index)
            rowData = self.m.dataToDict(rowData)
            pdfBytes = self.p.genLabelPreview(rowData)  # retrieves the pdf in Bytes
            self.pdf_preview.load_preview(pdfBytes)  # starts the loading display process        
        

    def populateTreeWidget(self):
        """ given a list of tuples structured as(siteNum, specimenNum),
        populates the TreeWidget with the records nested within the sites."""
        # first clear the tree        
        self.tree_widget.clear()
        fieldNumbers = self.m.getSiteSpecimens()
        siteNumbers = list(set([x[0] for x in fieldNumbers]))
        siteNumbers.sort(key = int)
        #QTreeWidgetItem(["String AA", "String BB", "String CC"])
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

    
app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
w = MyWindow()
w.show()

sys.exit(app.exec_())