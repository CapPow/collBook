# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/importindexdialogUI.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_importIndexDialog(object):
    def setupUi(self, importIndexDialog, inat):
        importIndexDialog.setObjectName("importIndexDialog")
        importIndexDialog.resize(411, 396)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        importIndexDialog.setFont(font)
        self.gridLayout = QtWidgets.QGridLayout(importIndexDialog)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(importIndexDialog)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.value_Use_Existing_Site_Numbers = QtWidgets.QRadioButton(self.groupBox)
        self.value_Use_Existing_Site_Numbers.setObjectName("value_Use_Existing_Site_Numbers")
        self.horizontalLayout_2.addWidget(self.value_Use_Existing_Site_Numbers)
        self.value_Existing_Site_Numbers = QtWidgets.QComboBox(self.groupBox)
        self.value_Existing_Site_Numbers.setEnabled(False)
        self.value_Existing_Site_Numbers.setObjectName("value_Existing_Site_Numbers")
        self.horizontalLayout_2.addWidget(self.value_Existing_Site_Numbers)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.SpanningRole, self.horizontalLayout_2)
        self.value_Gen_Site_Numbers = QtWidgets.QRadioButton(self.groupBox)
        if inat:
            self.value_Gen_Site_Numbers.setChecked(False)
        else:
            self.value_Gen_Site_Numbers.setChecked(True)
        self.value_Gen_Site_Numbers.setObjectName("value_Gen_Site_Numbers")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.value_Gen_Site_Numbers)
        self.value_Use_One_Site = QtWidgets.QRadioButton(self.groupBox)
        if inat:
            self.value_Use_One_Site.setChecked(True)
        else:
            self.value_Use_One_Site.setChecked(False)
        self.value_Use_One_Site.setObjectName("value_Use_One_Site")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.value_Use_One_Site)
        self.gridLayout.addWidget(self.groupBox, 6, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.pushButton_Cancel = QtWidgets.QPushButton(importIndexDialog)
        self.pushButton_Cancel.setObjectName("pushButton_Cancel")
        self.horizontalLayout_3.addWidget(self.pushButton_Cancel)
        self.pushButton_Assign = QtWidgets.QPushButton(importIndexDialog)
        self.pushButton_Assign.setObjectName("pushButton_Assign")
        self.horizontalLayout_3.addWidget(self.pushButton_Assign)
        self.gridLayout.addLayout(self.horizontalLayout_3, 7, 0, 1, 1)
        self.label = QtWidgets.QLabel(importIndexDialog)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(importIndexDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(importIndexDialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName("formLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.value_Use_Existing_Specimen_Numbers = QtWidgets.QRadioButton(self.groupBox_2)
        self.value_Use_Existing_Specimen_Numbers.setObjectName("value_Use_Existing_Specimen_Numbers")
        self.horizontalLayout.addWidget(self.value_Use_Existing_Specimen_Numbers)
        self.value_Existing_Specimen_Numbers = QtWidgets.QComboBox(self.groupBox_2)
        self.value_Existing_Specimen_Numbers.setEnabled(False)
        self.value_Existing_Specimen_Numbers.setObjectName("value_Existing_Specimen_Numbers")
        self.horizontalLayout.addWidget(self.value_Existing_Specimen_Numbers)
        self.formLayout_2.setLayout(0, QtWidgets.QFormLayout.SpanningRole, self.horizontalLayout)
        self.value_Gen_Specimen_Numbers = QtWidgets.QRadioButton(self.groupBox_2)
        self.value_Gen_Specimen_Numbers.setChecked(True)
        self.value_Gen_Specimen_Numbers.setObjectName("value_Gen_Specimen_Numbers")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.value_Gen_Specimen_Numbers)
        self.gridLayout.addWidget(self.groupBox_2, 5, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 4, 0, 1, 1)

        self.retranslateUi(importIndexDialog, inat)
        self.value_Use_Existing_Site_Numbers.toggled['bool'].connect(self.value_Existing_Site_Numbers.setEnabled)
        self.value_Use_Existing_Specimen_Numbers.toggled['bool'].connect(self.value_Existing_Specimen_Numbers.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(importIndexDialog)

    def retranslateUi(self, importIndexDialog, inat):
        _translate = QtCore.QCoreApplication.translate
        importIndexDialog.setWindowTitle(_translate("importIndexDialog", "Form"))
        self.groupBox.setTitle(_translate("importIndexDialog", "Site Number"))
        self.value_Use_Existing_Site_Numbers.setText(_translate("importIndexDialog", "Pick from existing columns"))
        self.value_Gen_Site_Numbers.setText(_translate("importIndexDialog", "Generate unique site numbers"))
        self.value_Use_One_Site.setText(_translate("importIndexDialog", "Treat all imported records as one site (recommended for iNaturalist-like files)"))
        self.pushButton_Cancel.setText(_translate("importIndexDialog", "Cancel"))
        self.pushButton_Assign.setText(_translate("importIndexDialog", "Assign"))
        if inat:
            self.label.setText(_translate("importIndexDialog", "Importing iNaturalist file."))
        else:
            self.label.setText(_translate("importIndexDialog",
                                          "Could not locate indexing fields (ie: siteNumber, specimenNumber, or otherCatalogNumbers)."))
        self.label_2.setText(_translate("importIndexDialog", "Select how to assign index fields."))
        self.groupBox_2.setTitle(_translate("importIndexDialog", "Specimen Numbers"))
        self.value_Use_Existing_Specimen_Numbers.setText(_translate("importIndexDialog", "Pick from existing columns"))
        self.value_Gen_Specimen_Numbers.setText(_translate("importIndexDialog", "Generate unique specimen numbers"))

