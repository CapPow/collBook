#!/usr/bin/env python3

# How to view PDF in a Qt5 widget.
# Poppler has almost no documentation and Python-Qt5 isn't much better,
# so maybe this will help someone.
# Copyright 2018 by Akkana Peck: share and enjoy under the GPLv2 or later.

# Uses popplerqt5: https://pypi.org/project/python-poppler-qt5/
# or Debian package python3-poppler-qt5

# Poppler is theoretically available from gi (instead of popplerqt5),
# but I haven't found any way to get that Poppler to work with Qt5
# because it can only draw to a Cairo context.
# import gi
# gi.require_version('Poppler', '0.18')
# from gi.repository import Poppler

import sys
import traceback

from PyQt5.QtWidgets import QWidget, QApplication, QShortcut, \
     QLabel, QScrollArea, QSizePolicy, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSize
from popplerqt5 import Poppler
import Resources_rc


# Poppler gives page sizes in points, so 72 DPI.
# If you want to use a DPI other than 72, you have to convert.
POINTS_PER_INCH = 72

""" the QLabel object from qt Designer UI files
which to link this class to is called: pdf_preview """


class PDFViewer(QLabel):

    '''
    A widget showing one page of a PDF.
    If you want to show multiple pages of the same PDF,
    make sure you share the document (let the first PDFViewer
    create the document, then pass thatPDFViewer.document to any
    subsequent widgets you create) or use a ScrolledPDFViewer.
    '''

    def __init__(self, parent, pdfData= None, 
                 document=None, pageno=1, dpi=72,load_cb=None):
        '''
           load_cb: will be called when the document is loaded.
        '''
        #dpi - 72
        super(PDFViewer, self).__init__()        

        screenSize = (parent.parent().geometry())
        screenX = screenSize.width()
        self.xMax = screenX * 0.5
        screenY = screenSize.height()
        self.yMax = screenY * 0.75
        self.filename = pdfData
        self.load_cb = load_cb
        self.value_X = 140
        self.value_Y = 90
        if not document:
            self.document = None
            self.load_preview(pdfData)
        else:
            self.document = document
        self.page = None
        self.dpi = dpi

    def initViewer(self, parent):
        #print(parent.objectName())
        self.parent = parent
        self.settings = self.parent.settings
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # at 25.4mm per inch, need to adjust values since they're in mm.
        self.value_X = int(self.settings.get('value_X', 140)) * (self.dpi / 25.4)
        self.value_X = min(self.value_X, self.xMax)  # be sure it does not exceed the max
        self.value_Y = int(self.settings.get('value_Y', 90)) * (self.dpi / 25.4)
        self.value_Y = min(self.value_Y, self.yMax)  # be sure it does not exceed the max
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
            self.document = Poppler.Document.loadFromData(pdfBytes) #  Try loading from bytes
            self.document.setRenderHint(Poppler.Document.TextAntialiasing)
            pdfPage = self.document.page(0)
            img = pdfPage.renderToImage() #  See if it needs rendered to an image
            img = img.scaled(self.value_X, self.value_Y, Qt.KeepAspectRatio)
            #img = img.scaled(self.pagesize, Qt.KeepAspectRatio)
        except (AttributeError, TypeError):
            img = QImage(':/rc_/label_Preview.png')
            img = img.scaled(self.value_X, self.value_Y, Qt.KeepAspectRatio)
            #img = img.scaled(self.pagesize, Qt.KeepAspectRatio)
        self.setPixmap(QPixmap.fromImage(img))


class PDFScrolledWidget(QScrollArea):   # inherit from QScrollArea?

    '''
    Show all pages of a PDF, with scrollbars.
    '''

    def __init__(self, filename, dpi=72, parent=None):
        super(PDFScrolledWidget, self).__init__(parent)

        self.loaded = False

        self.vscrollbar = None

        self.setWidgetResizable(True)

        # Try to eliminate the guesswork in sizing the window to content:
        self.setFrameShape(self.NoFrame)

        # I would like to set both scrollbars to AsNeeded:
        # but if the vertical scrollbar is AsNeeded, the content
        # gets loaded initially, then the QScrollArea decides it
        # needs a vertical scrollbar, adds it and resizes the content
        # inside, so everything gets scaled by 0.98.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Create a widget inside the scroller for the VBox layout to use:
        self.scroll_content = QWidget()
        self.setWidget(self.scroll_content)

        # A VBox to lay out all the pages vertically:
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Create the widget for the first page of the PDF,
        # which will also create the Poppler document we'll use
        # to render the other pages.
        self.pages = [ PDFViewer(filename, document=None, pageno=1, dpi=dpi,
                                 load_cb = self.load_cb) ]
        self.pages[0].setContentsMargins(0, 0, 0, 0)
        self.pages[0].setFrameShape(self.NoFrame)

        # Add page 1 to the vertical layout:
        self.scroll_layout.addWidget(self.pages[0])


    def load_cb(self):
        page1 = self.pages[0]

        width = page1.width()
        height = page1.height()
        if self.vscrollbar:
            sbw = self.vscrollbar.width()
            width += sbw
            height += sbw

        for p in range(2, page1.document.numPages()):
            pagew = PDFViewer(page1.filename, document=page1.document,
                              pageno=p, dpi=page1.dpi)
            pagew.setContentsMargins(0, 0, 0, 0)

            # pagew.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            self.scroll_layout.addWidget(pagew)
            self.pages.append(pagew)

        self.scroll_layout.addStretch(1)

        # Now there's a size. Set the initial page size to be big enough
        # to show one page, including room for scrollbars, at 72 DPI.
        self.resizeToFitContent()

        # Don't set the loaded flag until after the first set of resizes,
        # so resizeEvent() won't zoom.
        self.loaded = True

    def resizeToFitContent(self):
        '''Resize to be wide enough not to show a horizontal scrollbar,
           and just a little taller than the first page of PDF content.
        '''
        if not self.vscrollbar:
            self.vscrollbar = self.verticalScrollBar()
        if self.vscrollbar:
            vscrollbarwidth = self.vscrollbar.width()
        else:
            vscrollbarwidth = 14

        # Getting the size of a widget is tricky.
        # self.widget().width(), for some reason, gives the width minus 12
        # pixels, while self.widget().sizeHint().width() gives the
        # correct size.
        # So that means, apparently, if you want the margins of a widget
        # you can get them by subtracting width() and height() from sizeHint().
        # print("widget width is", self.widget().width(),
        #       ", sizehint", self.widget().sizeHint().width())
        width = self.widget().sizeHint().width() + vscrollbarwidth
        height = self.pages[0].pagesize.height() + vscrollbarwidth

        self.resize(width, height)

    def resizeEvent(self, event):
        '''On resizes after the initial resize,
           re-render the PDF to fit the new width.
        '''
        oldWidth = event.oldSize().width()
        newWidth = event.size().width()

        if oldWidth > 0 and self.loaded:
            self.zoom(newWidth / oldWidth)

        super(PDFScrolledWidget, self).resizeEvent(event)

    def zoom(self, frac=1.25):
        '''Zoom the page by the indicated fraction.
        '''
        for page in self.pages:
            # Resize according to width, ignoring height.
            page.dpi *= frac
            page.render()

    def unzoom(self, frac=.8):
        '''Zoom the page by the indicated fraction.
           Same as unzoom but with a default that zooms out instead of in.
        '''
        self.zoom(frac)


#if __name__ == '__main__':
#    #
#    # PyQt is super crashy. Any little error, like an extra argument in a slot,
#    # causes it to kill Python with a core dump.
#    # Setting sys.excepthook works around this , and execution continues.
#    #
#    def excepthook(excType=None, excValue=None, tracebackobj=None, *,
#                   message=None, version_tag=None, parent=None):
#        # print("exception! excValue='%s'" % excValue)
#        # logging.critical(''.join(traceback.format_tb(tracebackobj)))
#        # logging.critical('{0}: {1}'.format(excType, excValue))
#        traceback.print_exception(excType, excValue, tracebackobj)
#
#    sys.excepthook = excepthook
#
#    app = QApplication(sys.argv)
#
#    # It's helpful to know screen size, to choose appropriate DPI.
#    # It's currently ignored but will eventually be used.
#    desktops = QApplication.desktop()
#    geometry = desktops.screenGeometry(desktops.screenNumber())
#    # print("screen geometry is", geometry.width(), geometry.height())
#
#    w = PDFScrolledWidget(sys.argv[1])
#    # w = PDFViewer(sys.argv[1])
#
#    QShortcut("Ctrl+Q", w, activated=w.close)
#
#    w.show()
#
#    sys.exit(app.exec_())
