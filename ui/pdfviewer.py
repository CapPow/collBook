#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 20:19:40 2019

#Based on guidance from qpdfview.py by Akkana Peck (akkana@shallowsky.com),
#available at: https://github.com/akkana

@author: Caleb Powell
"""
from PyQt5.QtWidgets import QWidget, QApplication, QShortcut, \
     QLabel, QScrollArea, QSizePolicy, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSize
import Resources_rc

import fitz

class PDFViewer(QLabel):

    '''
    A widget displaying the pdf as a pixmap.
    '''

    def __init__(self, parent, pdfData= None, 
                 document=None, pageno=1, dpi=72):

        #dpi - 72
        super(PDFViewer, self).__init__()        

        screenSize = (parent.parent().geometry())
        screenX = screenSize.width()
        self.xMax = screenX * 0.5
        screenY = screenSize.height()
        self.yMax = screenY * 0.75
        self.filename = pdfData
        self.value_X = 140
        self.value_Y = 90
        if not document:
            self.document = None
            self.load_preview(pdfData)
        else:
            self.document = document
        self.page = None
        self.dpi = dpi

        #self.value_Zoom = 1  # prepping for a future zoom feature on labels

    def initViewer(self, parent):
        self.parent = parent
        self.settings = self.parent.settings
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # at 25.4mm per inch, need to adjust values since they're in mm.
        self.value_X = int(self.settings.get('value_X', 140)) * (self.dpi / 25.4)
        #self.value_X = min(self.value_X, self.xMax)  # be sure it does not exceed the max
        self.value_Y = int(self.settings.get('value_Y', 90)) * (self.dpi / 25.4)
        #self.value_Y = min(self.value_Y, self.yMax)  # be sure it does not exceed the max
        # appears to be a 10% resize error somewhere between these values, the 1.1 corrects this
        self.pagesize = QSize(self.value_X, self.value_Y) * 1.1

    def sizeHint(self):
        return self.pagesize

    def load_label_OversizeWarning(self):
        img = QImage(':/rc_/label_OversizeWarning.png')
        img = img.scaled(self.value_X, self.value_Y, Qt.KeepAspectRatio)
        self.document = None
        self.setPixmap(QPixmap.fromImage(img))

    def load_preview(self, pdfBytes):
        try:
            self.document = fitz.open(stream = pdfBytes, filetype = 'pdf')  # Try loading from bytes
            pdfPage = self.document[0]
            value_Zoom = int(self.settings.get('value_zoomLevel', 100)) / 100
            mat = fitz.Matrix(value_Zoom, value_Zoom)  # the scaling / transformations
            pix = pdfPage.getPixmap(alpha = False, matrix = mat)
            fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            zoomX = min(self.xMax, self.value_X * value_Zoom)
            zoomY = min(self.yMax, self.value_Y * value_Zoom)
            img = img.scaled(zoomX, zoomY, Qt.KeepAspectRatio)
        except (IndexError) as e:
            img = QImage(':/rc_/label_Preview.png')
            img = img.scaled(self.value_X, self.value_Y, Qt.KeepAspectRatio)
        self.setPixmap(QPixmap.fromImage(img))
