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
from fitz.utils import getColor

class PDFViewer(QLabel):

    '''
    A widget displaying the pdf as a pixmap.
    '''

    def __init__(self, parent, pdfData=None,
                 document=None, pageno=1):
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
        else:
            self.document = document
        self.page = None
        self.parent = parent.parent()

    def initViewer(self, parent):
        self.settings = self.parent.settings
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        screenSize = (parent.geometry())
        screenX = screenSize.width()
        self.xMax = screenX * 0.5
        screenY = screenSize.height()
        self.yMax = screenY * 0.75
        # at 25.4mm per inch, need to adjust values since they're in mm.
        self.value_X = int(self.settings.get('value_X', 140))
        self.value_Y = int(self.settings.get('value_Y', 90))
        self.settings.setMaxZoom()
        # appears to be a 10% resize error somewhere between these values, the 1.1 corrects this

    def load_preview(self, pdfBytes, errorType=False):

        if errorType:
            if errorType == 'oversize':
                errorText = ["Label contents do not fit!", "Adjust label settings, or content."]
            elif errorType == 'preview':
                errorText = ["Label Preview Window"]
            pdfBytes = self.parent.p.genErrorLabel(errorText)
            self.document = fitz.open(stream=pdfBytes, filetype='pdf')
            pdfPage = self.document[0]
        try:
            self.document = fitz.open(stream=pdfBytes, filetype='pdf')  # Try loading from bytes
            pdfPage = self.document[0]
        except IndexError:
            errorText = ["Label Preview Window"]
            pdfBytes = self.parent.p.genErrorLabel(errorText)
            self.document = fitz.open(stream=pdfBytes, filetype='pdf')
            pdfPage = self.document[0]
        zoom = int(self.settings.get('value_zoomLevel', 100)) / 100
        mat = fitz.Matrix(zoom, zoom)  # the scaling / transformations
        pix = pdfPage.getPixmap(alpha=False, matrix=mat)
        fmt = QImage.Format_RGB888
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        #x,y = self.getZoom(labXY=True)
        self.setPixmap(QPixmap.fromImage(img))
