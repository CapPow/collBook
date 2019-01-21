import sys
from io import StringIO
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QTreeWidgetItemIterator, QItemDelegate, QCompleter
from reportlab.platypus.doctemplate import LayoutError
from ui.printlabels import LabelPDF
from ui.pandastablemodel import PandasTableModel
from ui.locality import locality
from PyQt5.QtCore import QFile, Qt
import qdarkstyle
from ui.TestUI import Ui_MainWindow
from ui.settingsdialog import settingsWindow
from ui.taxonomy import taxonomicVerification
from ui.associatedtaxa import associatedTaxaMainWindow

from ui.progressbar import progressBar

class editorDelegate(QItemDelegate):
    """solution to the table_view editor clearing pre-existing cell values
    ref: https://stackoverflow.com/questions/39387842/not-displaying-old-value-when-editing-cell-in-a-qtablewidget"""
    def setEditorData(self, editor, index):
        editor.setAutoFillBackground(True)
        editor.setText(str(index.data()))


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.w = Ui_MainWindow()
        self.showMaximized()
        self.w.setupUi(self)
        self.status_bar = self.statusBar()
        self.statusBar = progressBar(self.status_bar)
        self.statusBar.initProgressBar(self.status_bar)
        self.progress_bar = self.statusBar.progressBar
        self.m = PandasTableModel(self)
        self.tree_widget = self.w.tree_widget  # The nav tree widget.
        self.site_tree_widget = self.w.treeWidget_sitesToApply  # site selection tree widget in "all records view"
        self.settings = settingsWindow(self)  # settingsWindow
        self.associatedTaxaWindow = associatedTaxaMainWindow(self)  # associatedTaxaWindow
        self.lineEdit_sciName = self.w.lineEdit_sciName
        self.form_view = self.w.formView
        self.table_view = self.w.table_view
        self.table_view.setItemDelegate(editorDelegate(self.table_view))  # use flipped proxy delegate
        self.form_view.init_ui(self, self.w)
        self.tax = taxonomicVerification(self.settings)  # taxonomic verifier
        self.p = LabelPDF(self.settings)
        self.pdf_preview = self.w.pdf_preview
        self.pdf_preview.initViewer(self)
        self.m.new_Records(True)
        self.table_view.setModel(self.m)
        self.locality = locality(self)
        self.w.action_Open.triggered.connect(self.m.open_CSV)
        self.w.action_Save_As.triggered.connect(self.m.save_CSV)
        self.w.action_New_Records.triggered.connect(self.m.new_Records)
        self.w.action_Exit.triggered.connect(lambda: sys.exit(app.exec_()))
        self.w.action_Settings.triggered.connect(self.toggleSettings)
        self.w.button_associatedTaxa.clicked.connect(self.toggleAssociated)
        self.w.action_Reverse_Geolocate.triggered.connect(self.m.geoRef)
        self.w.toolButton_reverseGeolocate.clicked.connect(self.m.geoRef)
        self.w.action_Verify_Taxonomy.triggered.connect(self.m.verifyTaxButton)
        self.w.toolButton_verifyTaxonomy.clicked.connect(self.m.verifyTaxButton)
        self.w.action_Verify_All.triggered.connect(self.m.verifyAllButton)
        self.w.action_Export_Labels.triggered.connect(self.exportLabels)
        self.w.pushButton_newSite.clicked.connect(self.m.addNewSite)
        self.w.pushButton_newSpecimen.clicked.connect(self.m.addNewSpecimen)
        self.w.pushButton_duplicateSpecimen.clicked.connect(self.m.duplicateSpecimen)
        self.w.pushButton_deleteSite.clicked.connect(self.m.deleteSite)
        self.w.pushButton_deleteRecord.clicked.connect(self.m.deleteSpecimen)
        self.w.toolButton_sitesToApply_SelectNone.clicked.connect(self.clearSitesToApply)
        self.w.toolButton_sitesToApply_SelectAll.clicked.connect(self.selectAllSitesToApply)
        #self.w.actionTestFunction.triggered.connect(self.timeitTest)  # a test function button for debugging or time testing
                # update the preview window as dataframe changes
        self.m.dataChanged.connect(self.updatePreview)
        self.updateAutoComplete()
        
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

    def getTreeSelectionType(self):
        """ checks the tree_widget's type of selection """
        # TODO alter selType to become a custom attribute of mainWindow, setting it upon changes. This should reduce checks with this function
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
        # TODO rename this, as it does more than upates tableview. Basically alters scope of user's view
        selType, siteNum, specimenNum = self.getTreeSelectionType()
        rowsToHide = self.m.getRowsToHide(selType, siteNum, specimenNum)
        rowNums = range(self.m.rowCount())
        for row in rowNums:
            if row not in rowsToHide:
                self.table_view.showRow(row)
            else:
                self.table_view.hideRow(row)

        if selType != 'allRec':
            topVisible = [x for x in rowNums if x not in rowsToHide]
            try:
                #TODO make consideration for avoiding this if the last action was an edit.
                topVisible = min(topVisible)
                self.table_view.selectRow(topVisible)
            except ValueError:
                self.table_view.clearSelection()
        self.updatePreview()

        if selType == 'site':
            self.statusBar.label_status.setText("  Site View  ")
            self.form_view.setCurrentIndex(1) #swap to site tab
        elif selType == 'specimen':
            self.statusBar.label_status.setText("Specimen View")
            self.form_view.setCurrentIndex(2) #swap to specimen tab
        else: #  probably all records
            self.statusBar.label_status.setText(" All Records  ")
            self.form_view.setCurrentIndex(0) #all records
        self.form_view.fillFormFields()

    def selectTreeWidgetItemByIndex(self, i):
        """ helper function called when form_view's tab index is clicked Is 
        intended to change the user's view to all records when the all records
        tab is clicked """
        if i == 0:
            self.selectTreeWidgetItemByName('All Records')

    def selectTreeWidgetItemByName(self, name):
        """ selects an item on the nav tree_widget. Permits site selection without
        the parenthetical (n) value. ie: 'Site 5' would find 'Site 5 (12)' """
        iterator = QTreeWidgetItemIterator(self.tree_widget, QTreeWidgetItemIterator.All)
        if name[:5] == 'Site ':  # handle changing record counts at set site#s
            name = name.split('(')[0].strip()
        while iterator.value():
            item = iterator.value()
            if name in item.text(0):
                self.tree_widget.setCurrentItem(item,1)
                break
            iterator +=1
    def expandCurrentTreeWidgetItem(self):
        """ expands the currently selected tree_widget item """
        itemSelected = self.tree_widget.currentItem()
        selectionIndex = self.tree_widget.indexFromItem(itemSelected)
        self.tree_widget.expand(selectionIndex)

    def timeitTest(self):
        """ debugging / improving space for testing various functions or their timings """

        from datetime import datetime
        a = datetime.now()
        iterCount = 10000
        for i in range(iterCount):
            listComp = [x for x in range(0, self.m.rowCount()) if not self.table_view.isRowHidden(x)]
        b = datetime.now()
        listCompTime = b - a
        listCompTime = int((listCompTime.total_seconds() / iterCount) * 1000000) # microseconds
        print(f'listComp = {listCompTime} (µs)')
        a = datetime.now()
        for i in range(iterCount):
            treeSel = self.m.getRowsToProcess(*self.getTreeSelectionType())
        b = datetime.now()
        treeSelTime = b - a
        treeSelTime = int((treeSelTime.total_seconds() / iterCount) * 1000000) # microseconds
        print(f'treeSel = {treeSelTime} (µs)')

    def getVisibleRows(self):
        """ returns a list of indicies which are visible """
        visibleRows = [x for x in range(0, self.m.rowCount()) if not self.table_view.isRowHidden(x)]
        return visibleRows
    
    def getVisibleRowData(self):
        """ queries the table_view for selected rows 
        and returns associated rowData """
        rowsVisible = self.getVisibleRows()
        if rowsVisible:
            rowData = self.m.retrieveRowData(rowsVisible)
            rowData = self.m.dataToDict(rowData)
        else:
            rowData = None
        return rowData


    def exportLabels(self):
        """ bundles records up and passes them to printlabels.genPrintLabelPDFs() """
        try:
            rowsToProcess = self.m.getRowsToProcess(*self.getTreeSelectionType())
            outDF = self.m.datatable.iloc[rowsToProcess, ]
            outDict = self.m.dataToDict(outDF)
            self.p.genPrintLabelPDFs(outDict)
        except LayoutError:
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("""The content of one or more of your labels is too large for the label dimentions. Alter your settings, and try again.""")
            msg.setWindowTitle('Label Export Error')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def updatePreview(self):
        """ updates the pdf preview window """
        #TODO modify this to be called from within the pdfviewer class
        rowData = self.getVisibleRowData()
        selType, siteNum, specimenNum = self.getTreeSelectionType()
        if (isinstance(rowData, list)) & (selType != 'allRec'):
            if (selType == 'site') & (len(rowData) > 1):
                rowData = [rowData[1]]  # only want first row, but other functions expect a list
            else:
                rowData = [rowData[0]]
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
       
    def getSelectSitesToApply(self):
        """ queries the site_tree_widget to determine which are checked """
        fieldNumbers = self.m.getSiteSpecimens()
        siteNumbers = list(set([x[0] for x in fieldNumbers]))
        if self.w.radioButton_applyAllRecords.isChecked():
            return siteNumbers
        else:
            siteNumbers = []
            iterator = QTreeWidgetItemIterator(self.site_tree_widget, QTreeWidgetItemIterator.Checked)
            while iterator.value():
                siteText = iterator.value().text(0)
                siteNum = siteText.split()[-1]
                siteNumbers.append(siteNum)
                iterator += 1
            return siteNumbers
        
    def selectAllSitesToApply(self):
        """ checks all objects in site_tree_widget, may be useful if the user
        wants to select all but a few in the list"""
        iterator = QTreeWidgetItemIterator(self.site_tree_widget, QTreeWidgetItemIterator.NotChecked)
        while iterator.value():
            obj = iterator.value()
            obj.setCheckState(0, Qt.Checked)
            iterator += 1

    def clearSitesToApply(self):
        """ unchecks all objects in site_tree_widget """
        iterator = QTreeWidgetItemIterator(self.site_tree_widget, QTreeWidgetItemIterator.Checked)
        while iterator.value():
            obj = iterator.value()
            obj.setCheckState(0, Qt.Unchecked)
            iterator += 1

    def populateTreeWidget(self):
        """ populates the navigation TreeWidget with the records nested 
        within sites. Also populates site_tree_widget with site numbers"""
        # store the current selection(s)
        itemSelected = self.tree_widget.currentItem()
        sites_Selected = self.getSelectSitesToApply()
        sites_Selected = [f'Site {x}' for x in sites_Selected]
        try:
            text = itemSelected.text(0)
        except AttributeError:
            text = 'All Records'
        self.tree_widget.clear()
        self.site_tree_widget.clear()
        fieldNumbers = self.m.getSiteSpecimens()
        siteNumbers = list(set([x[0] for x in fieldNumbers]))
        try:
            siteNumbers.sort(key = int)
        except ValueError:
            pass
        # build a hierarchical structure of QTreeWidgetItem(s) to fill the tree with
        self.tree_widget.addTopLevelItem(QTreeWidgetItem(["All Records"]))
        for siteNum in siteNumbers:
            site_tree_text = f'Site {siteNum}'
            site_tree_item = QTreeWidgetItem([site_tree_text])
            if site_tree_text in sites_Selected:
                site_tree_item.setCheckState(0, Qt.Checked)  # update site_tree_widget
            else:
                site_tree_item.setCheckState(0, Qt.Unchecked)  # update site_tree_widget
            self.site_tree_widget.addTopLevelItems([site_tree_item]) # fill in site_tree_widget
            
            # now start on the navigation "tree_widget" object.            
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