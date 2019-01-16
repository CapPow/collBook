#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 10:33:55 2019

@author: Caleb Powell

"""
#from PyQt5 import Qt
#from PyQt5 import QtCore
#from PyQt5.QtCore import QAbstractTableModel
#from PyQt5.QtCore import QDir
#from PyQt5.QtCore import QStringListModel
#from PyQt5.QtCore import QVariant
#from PyQt5.QtGui import QColor
#from PyQt5.QtGui import QIcon
#from PyQt5.QtWidgets import QFileSystemModel

import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QListWidgetItem
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication

from ui.associatedtaxaUI import Ui_associatedTaxaMainWindow

class associatedTaxaMainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.init_ui(parent)

        #TODO add a consideration for if the config file has never been created... fill in default values
        # can use the get() argument for alt values and just code it into the populateSettings() function
           
    def init_ui(self, parent):
        self.parent = parent # this is the master window
        associatedMainWin = Ui_associatedTaxaMainWindow()
        associatedMainWin.setupUi(self)
        
        # make the entry object addressable
        self.lineEdit_newAssociatedTaxa = associatedMainWin.lineEdit_newAssociatedTaxa
        # make the main window easily addressable
        self.associatedMainWin = associatedMainWin
        
        associatedList = associatedMainWin.listWidget_associatedTaxa
        self.associatedList = associatedList


    def saveAssociatedTaxa(self):
        """ Populates the mainwindow's lineEdit_associatedTaxa with the 
        checked taxa in associatedList and hides the associatedTaxaMainWindow"""
        #  collect the list, and dump them into the proper field(s)

        checkedTaxa = []
        for index in range(self.associatedList.count()):
            if self.associatedList.item(index).checkState() == Qt.Checked:
                checkedTaxa.append(self.associatedList.item(index).text())
        checkedTaxa = sorted(set(checkedTaxa), key=str.lower)
        currentSciName = self.parent.w.lineEdit_sciName.text()
        try:
            checkedTaxa.remove(currentSciName)
        except ValueError:
            pass
        joinedTaxa = ', '.join(checkedTaxa)
        self.parent.w.lineEdit_associatedTaxa.setText(joinedTaxa)
        self.hide()
        
    def populateAssociatedTaxa(self):
        """ populates the items in the associatedLists """
        
        self.associatedList.clear()
        # determine what is currently selected
        selType, siteNum, specimenNum = self.parent.getTreeSelectionType()
        existingAssociatedTaxa = self.parent.w.lineEdit_associatedTaxa.text().split(', ')
        if selType == 'specimen':  # see what is already there 
            selType = 'site'  # be sure we always gather atleast site-wide taxa
        rowsToConsider = self.parent.m.getRowsToKeep(selType, siteNum, None)
        # generate a  list of all taxa from the selections
        taxaList = []
        
        for row in rowsToConsider:
            rowData = self.parent.m.retrieveRowData(row)
            associatedNames =  rowData['associatedTaxa'].split(',')
            associatedNames.append(rowData['scientificName'])
            associatedNames = [x.strip() for x in associatedNames if x != '']
            taxaList.extend(associatedNames)
        taxaList = list(set(taxaList))
        QItems = []
        for taxon in taxaList:
                item = QListWidgetItem(taxon, self.associatedList)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.associatedList.addItem(item)
        self.associatedList.sortItems(Qt.AscendingOrder)
        #  if it is a specimen, check existing associated records         
        
        if None not in existingAssociatedTaxa:
            self.checkItems(existingAssociatedTaxa)            

    def checkItems(self, itemStrList):
        """ accepts a list of strings, and iterates over the associatedList,
        ensuring they are checked """
        for text in itemStrList:
            if text not in ['', None]:
                try:
                    item = self.associatedList.findItems(text, Qt.MatchRegExp)[0]
                    item.setCheckState(Qt.Checked)
                except IndexError:
                    item = QListWidgetItem(text, self.associatedList)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Checked)
                    self.associatedList.addItem(item)
        
    
    def addAssociatedTaxa(self):
        """ adds item from the lineEdit_newAssociatedTaxa to the associatedList """
        entryBar = self.associatedMainWin.lineEdit_newAssociatedTaxa
        text = entryBar.text()
        item = QListWidgetItem(text, self.associatedList)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked)
        self.associatedList.addItem(item)
        self.associatedList.sortItems(Qt.AscendingOrder)
        item = self.associatedList.findItems(text, Qt.MatchRegExp)[0]
        item.setSelected(True)     
        self.associatedList.scrollToItem(item)
        entryBar.clear()

    def selectNone(self):
        for i in range(self.associatedList.count()):
            item = self.associatedList.item(i)
            item.setCheckState(Qt.Unchecked)

    def selectAll(self):
        for i in range(self.associatedList.count()):
            item = self.associatedList.item(i)
            item.setCheckState(Qt.Checked)


        
