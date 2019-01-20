#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 18:27:51 2019

@author: Caleb Powell
"""

class progressBar(gui.QStatusBar):
    """a progres bar which sits in the status bar"""


    def __init__(self, parent = None):
        super(progressBar, self).__init__()
        self.initUI()

    def initUI(self):
        # Pre Params:
        self.setMinimumSize(800, 600)

        # File Menus & Status Bar:
        self.statusBar().showMessage('Ready')
        self.progressBar = gui.QProgressBar()


        self.statusBar().addPermanentWidget(self.progressBar)

        # This is simply to show the bar
        self.progressBar.setGeometry(30, 40, 200, 25)
        self.progressBar.setValue(50)