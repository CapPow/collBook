# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/TestUI.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(972, 699)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.upperhorizontalLayout = QtWidgets.QHBoxLayout()
        self.upperhorizontalLayout.setObjectName("upperhorizontalLayout")
        self.pdf_preview = PDFViewer(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pdf_preview.sizePolicy().hasHeightForWidth())
        self.pdf_preview.setSizePolicy(sizePolicy)
        self.pdf_preview.setMinimumSize(QtCore.QSize(30, 30))
        self.pdf_preview.setText("")
        self.pdf_preview.setObjectName("pdf_preview")
        self.upperhorizontalLayout.addWidget(self.pdf_preview)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.specimenGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.specimenGroupBox.setObjectName("specimenGroupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.specimenGroupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.specimen_tabWidget = QtWidgets.QTabWidget(self.specimenGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.specimen_tabWidget.sizePolicy().hasHeightForWidth())
        self.specimen_tabWidget.setSizePolicy(sizePolicy)
        self.specimen_tabWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.specimen_tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.specimen_tabWidget.setObjectName("specimen_tabWidget")
        self.specimen_tabWidgetPage1 = QtWidgets.QWidget()
        self.specimen_tabWidgetPage1.setObjectName("specimen_tabWidgetPage1")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.specimen_tabWidgetPage1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.lineEdit_sciName = QtWidgets.QLineEdit(self.specimen_tabWidgetPage1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_sciName.sizePolicy().hasHeightForWidth())
        self.lineEdit_sciName.setSizePolicy(sizePolicy)
        self.lineEdit_sciName.setMinimumSize(QtCore.QSize(40, 0))
        self.lineEdit_sciName.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lineEdit_sciName.setObjectName("lineEdit_sciName")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_sciName)
        self.lineEdit_sciNameAuthority = QtWidgets.QLineEdit(self.specimen_tabWidgetPage1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_sciNameAuthority.sizePolicy().hasHeightForWidth())
        self.lineEdit_sciNameAuthority.setSizePolicy(sizePolicy)
        self.lineEdit_sciNameAuthority.setObjectName("lineEdit_sciNameAuthority")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_sciNameAuthority)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.specimen_tabWidgetPage1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
        self.plainTextEdit.setSizePolicy(sizePolicy)
        self.plainTextEdit.setMinimumSize(QtCore.QSize(0, 45))
        self.plainTextEdit.setMaximumSize(QtCore.QSize(16777215, 50))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.plainTextEdit)
        self.label_sciName = QtWidgets.QLabel(self.specimen_tabWidgetPage1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_sciName.sizePolicy().hasHeightForWidth())
        self.label_sciName.setSizePolicy(sizePolicy)
        self.label_sciName.setObjectName("label_sciName")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_sciName)
        self.label_sciNameAuthority = QtWidgets.QLabel(self.specimen_tabWidgetPage1)
        self.label_sciNameAuthority.setObjectName("label_sciNameAuthority")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_sciNameAuthority)
        self.label = QtWidgets.QLabel(self.specimen_tabWidgetPage1)
        self.label.setObjectName("label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label)
        self.verticalLayout_3.addLayout(self.formLayout)
        self.specimen_tabWidget.addTab(self.specimen_tabWidgetPage1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.specimen_tabWidget.addTab(self.tab_2, "")
        self.gridLayout_2.addWidget(self.specimen_tabWidget, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.specimenGroupBox)
        self.siteGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.siteGroupBox.setObjectName("siteGroupBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.siteGroupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.site_tabWidget = QtWidgets.QTabWidget(self.siteGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.site_tabWidget.sizePolicy().hasHeightForWidth())
        self.site_tabWidget.setSizePolicy(sizePolicy)
        self.site_tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.site_tabWidget.setObjectName("site_tabWidget")
        self.site_Data = QtWidgets.QWidget()
        self.site_Data.setObjectName("site_Data")
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(self.site_Data)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(0, 0, 445, 30))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.associatedTaxa_horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.associatedTaxa_horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.associatedTaxa_horizontalLayout.setObjectName("associatedTaxa_horizontalLayout")
        self.label_associatedTaxa = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_associatedTaxa.sizePolicy().hasHeightForWidth())
        self.label_associatedTaxa.setSizePolicy(sizePolicy)
        self.label_associatedTaxa.setObjectName("label_associatedTaxa")
        self.associatedTaxa_horizontalLayout.addWidget(self.label_associatedTaxa)
        self.lineEdit_associatedTaxa = QtWidgets.QLineEdit(self.horizontalLayoutWidget_3)
        self.lineEdit_associatedTaxa.setObjectName("lineEdit_associatedTaxa")
        self.associatedTaxa_horizontalLayout.addWidget(self.lineEdit_associatedTaxa)
        self.button_associatedTaxa = QtWidgets.QToolButton(self.horizontalLayoutWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_associatedTaxa.sizePolicy().hasHeightForWidth())
        self.button_associatedTaxa.setSizePolicy(sizePolicy)
        self.button_associatedTaxa.setMaximumSize(QtCore.QSize(70, 16777215))
        self.button_associatedTaxa.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/rc_/plus-square.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_associatedTaxa.setIcon(icon)
        self.button_associatedTaxa.setObjectName("button_associatedTaxa")
        self.associatedTaxa_horizontalLayout.addWidget(self.button_associatedTaxa)
        self.site_tabWidget.addTab(self.site_Data, "")
        self.site_tabWidgetPage1 = QtWidgets.QWidget()
        self.site_tabWidgetPage1.setObjectName("site_tabWidgetPage1")
        self.gridLayout = QtWidgets.QGridLayout(self.site_tabWidgetPage1)
        self.gridLayout.setObjectName("gridLayout")
        self.label_stateProvince = QtWidgets.QLabel(self.site_tabWidgetPage1)
        self.label_stateProvince.setObjectName("label_stateProvince")
        self.gridLayout.addWidget(self.label_stateProvince, 7, 0, 1, 1)
        self.label_recordedBy = QtWidgets.QLabel(self.site_tabWidgetPage1)
        self.label_recordedBy.setObjectName("label_recordedBy")
        self.gridLayout.addWidget(self.label_recordedBy, 2, 1, 1, 1)
        self.label_associatedCollectors = QtWidgets.QLabel(self.site_tabWidgetPage1)
        self.label_associatedCollectors.setWordWrap(True)
        self.label_associatedCollectors.setObjectName("label_associatedCollectors")
        self.gridLayout.addWidget(self.label_associatedCollectors, 2, 2, 1, 1)
        self.lineEdit_coordinateUncertaintyInMeters = QtWidgets.QLineEdit(self.site_tabWidgetPage1)
        self.lineEdit_coordinateUncertaintyInMeters.setObjectName("lineEdit_coordinateUncertaintyInMeters")
        self.gridLayout.addWidget(self.lineEdit_coordinateUncertaintyInMeters, 6, 2, 1, 1)
        self.label_municipality = QtWidgets.QLabel(self.site_tabWidgetPage1)
        self.label_municipality.setObjectName("label_municipality")
        self.gridLayout.addWidget(self.label_municipality, 7, 2, 1, 1)
        self.label_latitude = QtWidgets.QLabel(self.site_tabWidgetPage1)
        self.label_latitude.setObjectName("label_latitude")
        self.gridLayout.addWidget(self.label_latitude, 4, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.site_tabWidgetPage1)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 4, 1, 1, 1)
        self.lineEdit_associatedCollectors = QtWidgets.QLineEdit(self.site_tabWidgetPage1)
        self.lineEdit_associatedCollectors.setObjectName("lineEdit_associatedCollectors")
        self.gridLayout.addWidget(self.lineEdit_associatedCollectors, 3, 2, 1, 1)
        self.lineEdit_stateProvince = QtWidgets.QLineEdit(self.site_tabWidgetPage1)
        self.lineEdit_stateProvince.setObjectName("lineEdit_stateProvince")
        self.gridLayout.addWidget(self.lineEdit_stateProvince, 10, 0, 1, 1)
        self.lineEdit_recordedBy = QtWidgets.QLineEdit(self.site_tabWidgetPage1)
        self.lineEdit_recordedBy.setObjectName("lineEdit_recordedBy")
        self.gridLayout.addWidget(self.lineEdit_recordedBy, 3, 1, 1, 1)
        self.label_eventDate = QtWidgets.QLabel(self.site_tabWidgetPage1)
        self.label_eventDate.setWordWrap(True)
        self.label_eventDate.setObjectName("label_eventDate")
        self.gridLayout.addWidget(self.label_eventDate, 2, 0, 1, 1)
        self.dateEdit_eventDate = QtWidgets.QDateEdit(self.site_tabWidgetPage1)
        self.dateEdit_eventDate.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.dateEdit_eventDate.setAccelerated(False)
        self.dateEdit_eventDate.setCurrentSection(QtWidgets.QDateTimeEdit.MonthSection)
        self.dateEdit_eventDate.setCurrentSectionIndex(1)
        self.dateEdit_eventDate.setObjectName("dateEdit_eventDate")
        self.gridLayout.addWidget(self.dateEdit_eventDate, 3, 0, 1, 1)
        self.lineEdit_municipality = QtWidgets.QLineEdit(self.site_tabWidgetPage1)
        self.lineEdit_municipality.setObjectName("lineEdit_municipality")
        self.gridLayout.addWidget(self.lineEdit_municipality, 10, 2, 1, 1)
        self.lineEdit_county = QtWidgets.QLineEdit(self.site_tabWidgetPage1)
        self.lineEdit_county.setObjectName("lineEdit_county")
        self.gridLayout.addWidget(self.lineEdit_county, 10, 1, 1, 1)
        self.lineEdit_decimalLatitude = QtWidgets.QLineEdit(self.site_tabWidgetPage1)
        self.lineEdit_decimalLatitude.setObjectName("lineEdit_decimalLatitude")
        self.gridLayout.addWidget(self.lineEdit_decimalLatitude, 6, 0, 1, 1)
        self.lineEdit_decimalLongitude = QtWidgets.QLineEdit(self.site_tabWidgetPage1)
        self.lineEdit_decimalLongitude.setObjectName("lineEdit_decimalLongitude")
        self.gridLayout.addWidget(self.lineEdit_decimalLongitude, 6, 1, 1, 1)
        self.label_uncertainty = QtWidgets.QLabel(self.site_tabWidgetPage1)
        self.label_uncertainty.setObjectName("label_uncertainty")
        self.gridLayout.addWidget(self.label_uncertainty, 4, 2, 1, 1)
        self.label_county = QtWidgets.QLabel(self.site_tabWidgetPage1)
        self.label_county.setObjectName("label_county")
        self.gridLayout.addWidget(self.label_county, 7, 1, 1, 1)
        self.site_tabWidget.addTab(self.site_tabWidgetPage1, "")
        self.gridLayout_3.addWidget(self.site_tabWidget, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.siteGroupBox)
        self.upperhorizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.upperhorizontalLayout)
        self.lower_horizontalLayout = QtWidgets.QHBoxLayout()
        self.lower_horizontalLayout.setObjectName("lower_horizontalLayout")
        self.tree_widget = QtWidgets.QTreeWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tree_widget.sizePolicy().hasHeightForWidth())
        self.tree_widget.setSizePolicy(sizePolicy)
        self.tree_widget.setMinimumSize(QtCore.QSize(150, 0))
        self.tree_widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tree_widget.setSizeIncrement(QtCore.QSize(0, 0))
        self.tree_widget.setBaseSize(QtCore.QSize(150, 0))
        self.tree_widget.setMouseTracking(False)
        self.tree_widget.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.tree_widget.setFrameShape(QtWidgets.QFrame.Panel)
        self.tree_widget.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.tree_widget.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.SelectedClicked)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setExpandsOnDoubleClick(True)
        self.tree_widget.setObjectName("tree_widget")
        item_0 = QtWidgets.QTreeWidgetItem(self.tree_widget)
        self.lower_horizontalLayout.addWidget(self.tree_widget)
        self.table_view = QtWidgets.QTableView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.table_view.sizePolicy().hasHeightForWidth())
        self.table_view.setSizePolicy(sizePolicy)
        self.table_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.table_view.setEditTriggers(QtWidgets.QAbstractItemView.AnyKeyPressed|QtWidgets.QAbstractItemView.CurrentChanged|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.table_view.setAlternatingRowColors(False)
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_view.setIconSize(QtCore.QSize(100, 100))
        self.table_view.setGridStyle(QtCore.Qt.DashLine)
        self.table_view.setSortingEnabled(True)
        self.table_view.setObjectName("table_view")
        self.table_view.verticalHeader().setCascadingSectionResizes(False)
        self.table_view.verticalHeader().setSortIndicatorShown(False)
        self.lower_horizontalLayout.addWidget(self.table_view)
        self.verticalLayout.addLayout(self.lower_horizontalLayout)
        self.verticalLayout.setStretch(1, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 972, 22))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.left_toolBar = QtWidgets.QToolBar(MainWindow)
        self.left_toolBar.setObjectName("left_toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.left_toolBar)
        self.right_toolBar = QtWidgets.QToolBar(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.right_toolBar.sizePolicy().hasHeightForWidth())
        self.right_toolBar.setSizePolicy(sizePolicy)
        self.right_toolBar.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.right_toolBar.setObjectName("right_toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.right_toolBar)
        self.action_Open = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/rc_/file-text.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Open.setIcon(icon1)
        self.action_Open.setObjectName("action_Open")
        self.action_Exit = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/rc_/log-out.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Exit.setIcon(icon2)
        self.action_Exit.setObjectName("action_Exit")
        self.action_Verify_Taxonomy = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/rc_/check-circle.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Verify_Taxonomy.setIcon(icon3)
        self.action_Verify_Taxonomy.setObjectName("action_Verify_Taxonomy")
        self.action_Reverse_Geolocate = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/rc_/map-pin.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.action_Reverse_Geolocate.setIcon(icon4)
        self.action_Reverse_Geolocate.setObjectName("action_Reverse_Geolocate")
        self.action_Save_As = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/rc_/save.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Save_As.setIcon(icon5)
        self.action_Save_As.setObjectName("action_Save_As")
        self.action_New_Records = QtWidgets.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/rc_/file-plus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_New_Records.setIcon(icon6)
        self.action_New_Records.setObjectName("action_New_Records")
        self.action_undo = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/rc_/corner-down-left.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon7.addPixmap(QtGui.QPixmap(":/icons/corner-down-left.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.action_undo.setIcon(icon7)
        self.action_undo.setObjectName("action_undo")
        self.action_Redo = QtWidgets.QAction(MainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/rc_/corner-down-right.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon8.addPixmap(QtGui.QPixmap(":/icons/corner-down-left.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.action_Redo.setIcon(icon8)
        self.action_Redo.setObjectName("action_Redo")
        self.action_Settings = QtWidgets.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/rc_/settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Settings.setIcon(icon9)
        self.action_Settings.setObjectName("action_Settings")
        self.action_Export_Labels = QtWidgets.QAction(MainWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/rc_/tag.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Export_Labels.setIcon(icon10)
        self.action_Export_Labels.setObjectName("action_Export_Labels")
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addAction(self.action_New_Records)
        self.menu_File.addAction(self.action_Save_As)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Exit)
        self.menubar.addAction(self.menu_File.menuAction())
        self.left_toolBar.addAction(self.action_New_Records)
        self.left_toolBar.addAction(self.action_Open)
        self.left_toolBar.addAction(self.action_Save_As)
        self.left_toolBar.addSeparator()
        self.left_toolBar.addAction(self.action_undo)
        self.left_toolBar.addAction(self.action_Redo)
        self.left_toolBar.addSeparator()
        self.left_toolBar.addAction(self.action_Verify_Taxonomy)
        self.left_toolBar.addAction(self.action_Reverse_Geolocate)
        self.left_toolBar.addAction(self.action_Settings)
        self.left_toolBar.addAction(self.action_Export_Labels)
        self.right_toolBar.addSeparator()
        self.right_toolBar.addAction(self.action_Exit)

        self.retranslateUi(MainWindow)
        self.specimen_tabWidget.setCurrentIndex(0)
        self.site_tabWidget.setCurrentIndex(1)
        self.table_view.clicked['QModelIndex'].connect(MainWindow.updatePreview)
        self.tree_widget.currentItemChanged['QTreeWidgetItem*','QTreeWidgetItem*'].connect(MainWindow.updateTableView)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.table_view, self.tree_widget)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.specimenGroupBox.setTitle(_translate("MainWindow", "Specimen"))
        self.label_sciName.setText(_translate("MainWindow", "Scientific Name"))
        self.label_sciNameAuthority.setText(_translate("MainWindow", "Authority"))
        self.label.setText(_translate("MainWindow", "Locality"))
        self.specimen_tabWidget.setTabText(self.specimen_tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Page"))
        self.siteGroupBox.setTitle(_translate("MainWindow", "Site"))
        self.label_associatedTaxa.setText(_translate("MainWindow", "Associated Taxa"))
        self.site_tabWidget.setTabText(self.site_tabWidget.indexOf(self.site_Data), _translate("MainWindow", "Page"))
        self.label_stateProvince.setText(_translate("MainWindow", " State/Province"))
        self.label_recordedBy.setText(_translate("MainWindow", "Primary Collector"))
        self.label_associatedCollectors.setText(_translate("MainWindow", "Associated Collectors (comma seperated)"))
        self.label_municipality.setText(_translate("MainWindow", "Municipality"))
        self.label_latitude.setText(_translate("MainWindow", "Latitude (decimal)"))
        self.label_2.setText(_translate("MainWindow", "Longitude (decimal)"))
        self.label_eventDate.setText(_translate("MainWindow", "Date (of collection)"))
        self.dateEdit_eventDate.setDisplayFormat(_translate("MainWindow", "yyyy/MM/dd"))
        self.label_uncertainty.setText(_translate("MainWindow", "Uncertainty (m)"))
        self.label_county.setText(_translate("MainWindow", "County"))
        self.tree_widget.headerItem().setText(0, _translate("MainWindow", "Sites"))
        __sortingEnabled = self.tree_widget.isSortingEnabled()
        self.tree_widget.setSortingEnabled(False)
        self.tree_widget.topLevelItem(0).setText(0, _translate("MainWindow", "All Records"))
        self.tree_widget.setSortingEnabled(__sortingEnabled)
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.left_toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.right_toolBar.setWindowTitle(_translate("MainWindow", "toolBar_2"))
        self.action_Open.setText(_translate("MainWindow", "&Open"))
        self.action_Open.setToolTip(_translate("MainWindow", "Open a CSV file"))
        self.action_Exit.setText(_translate("MainWindow", "&Exit"))
        self.action_Verify_Taxonomy.setText(_translate("MainWindow", "&Verify Taxonomy"))
        self.action_Verify_Taxonomy.setToolTip(_translate("MainWindow", "align scientific names & retrieve authorities"))
        self.action_Reverse_Geolocate.setText(_translate("MainWindow", "&Reverse Geolocate"))
        self.action_Reverse_Geolocate.setToolTip(_translate("MainWindow", "Use GPS coordinates to prepend locality details"))
        self.action_Save_As.setText(_translate("MainWindow", "&Save As"))
        self.action_Save_As.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.action_New_Records.setText(_translate("MainWindow", "&New Records"))
        self.action_New_Records.setToolTip(_translate("MainWindow", "Generate a new, empty record list"))
        self.action_undo.setText(_translate("MainWindow", "&undo"))
        self.action_undo.setToolTip(_translate("MainWindow", "undo last major action"))
        self.action_Redo.setText(_translate("MainWindow", "&Redo"))
        self.action_Redo.setToolTip(_translate("MainWindow", "undo last major action"))
        self.action_Settings.setText(_translate("MainWindow", "&Settings"))
        self.action_Settings.setToolTip(_translate("MainWindow", "Settings and preferences"))
        self.action_Export_Labels.setText(_translate("MainWindow", "&Export_Labels"))

from ui.pdfviewer import PDFViewer
import Resources_rc
