#!/usr/bin/env python
from reportlab.platypus import Image, Table, TableStyle, Flowable, SimpleDocTemplate, BaseDocTemplate, PageTemplate, PageBreak
from reportlab.platypus import Frame as platypusFrame   #NOTE SEE Special case import here to avoid namespace conflict with "Frame"
from reportlab.platypus.flowables import Spacer
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.graphics.barcode import code39 #Note, overriding a function from this import in barcode section
from reportlab.lib.units import inch, mm
from reportlab.lib import pagesizes

import os
import sys
import io

# TODO with the conversion to pyqt5, popplerqt5 should allow us to display & open 
# print dialogs for the pdfs without relying on system installed pdf viewer

import subprocess

from PyQt5.QtWidgets import QFileDialog

# This entire module needs clean up,
# dynamic spacing needs redesigned and simplified
# before size options are added.
class LabelPDF:
    
    def __init__(self, xPaperSize = 140, yPaperSize = 90, parent=None):
        """ xPaperSize, & yPaperSize are each assumed to be in mm """
        xPaperSize = xPaperSize * mm
        yPaperSize = yPaperSize * mm
        
        # Here is where preferences will be read into initalized
        # There are going to be lots of options for what goes on labels
        # additionally, there are some bundled font options with reportlab,
        # which could become a select from list or something

        relFont = 12
        xMarginProportion = 0
        yMarginProportion = 0   #Padding on tables are functionally the margins in our use. (We're claiming most of paper)
        xMargin = xMarginProportion * xPaperSize        #Margin set up (dynamically depending on paper sizes. Hopefully logical stuff).
        yMargin = xMarginProportion * yPaperSize
 
    """ Since this was ported, for now it is faster to just write helper 
    functions to call genPrintLabelsPDFs with appropriate args """
    
    def genLabelPreview(self, labelDataInput):
         # Get the value of the BytesIO buffer and write it to the response.
         pdfBytes = self.genPrintLabelPDFs(labelDataInput, returnBytes = True)
         return pdfBytes

    def genPrintLabelPDFs(self, labelDataInput, defaultFileName = None, returnBytes = False):
        """labelDataInput = list of dictionaries formatted as: {DWC Column:'field value'}
           defaultFileName = the filename to use as the default when saving the pdf file."""
        
        # 5.50in ~=140mm
        # 3.50in ~-89mm
        
#        
#        labelData = labelDataInput
#    #    xPaperSize = 5.50 * inch   #These values should be user preferences! (But it'll be a PITA to do)
#    #    yPaperSize = 3.50 * inch
#        yPaperSize = 5.50 * inch
#        xPaperSize = 3.50 * inch
#        customPageSize = (xPaperSize,yPaperSize)        #set up Paper size for labels, this should be user selectable in time.
#    
#        relFont = 12                                    #a font size which everything else relates to. Base normal text font size.
#    
#        xMarginProportion = 0
#        yMarginProportion = 0   #Padding on tables are functionally the margins in our use. (We're claiming most of paper)
#        xMargin = xMarginProportion * xPaperSize        #Margin set up (dynamically depending on paper sizes. Hopefully logical stuff).
#        yMargin = xMarginProportion * yPaperSize
    
        #Style sheets below (many lines.. for various styles)
        
    
        tableSty = [                                    #Default table style
                ('LEFTPADDING',(0,0),(-1,-1), 0),
                ('RIGHTPADDING',(0,0),(-1,-1), 0),
                ('TOPPADDING',(0,0),(-1,-1), 0),
                ('BOTTOMPADDING',(0,0),(-1,-1), 0)]
    
        #helper functions to keep the 'flowables' code more legible.
    
        def Para(textField1,styleKey,prefix = '',suffix = ''):
            if len(dfl(textField1)) > 0 :                #If the field has a value insert it, otherwise blank row
                return Paragraph(('<b>{}</b>'.format(prefix)) + dfl(textField1) + suffix,style = self.stylesheet(styleKey))
            else:
                return Paragraph('', style = self.stylesheet(styleKey))
    
        def verifiedByPara(textField1,styleKey):
            if len(dfl(textField1)) > 0 :                #If the field has a value insert it, otherwise blank row
                return Paragraph('<i>Verified by {}</i>'.format(dfl(textField1)),style = self.stylesheet(styleKey))
            else:
                return Paragraph('', style = self.stylesheet(styleKey))
    
        def sciName(textfield1,textfield2,styleKey,prefix = ''):
            if len(dfl(textfield1)) > 0 :
                return Paragraph(('<i>{}</i>'.format(dfl(textfield1))) + ' ' + dfl(textfield2),style = self.stylesheet(styleKey))
            else:
                return Paragraph('', style = self.stylesheet(styleKey))
    
        def collectedByPara(textfield1,textfield2,styleKey,prefix = ''):
            if len(dfl(textfield1)) > 0 :
                if len(dfl(textfield2)) > 0 :
                    return Paragraph(('<b>{}</b>'.format(prefix)) + dfl(textfield1) + ' with ' + dfl(textfield2), style = self.stylesheet(styleKey))
                else:
                    return Paragraph(('<b>{}</b>'.format(prefix)) + dfl(textfield1), style = self.stylesheet(styleKey))
            else:
                return Paragraph('', style = self.stylesheet(styleKey))
    
        def cultivationStatusChecker(textfield1, styleKey):
            if str(dfl(textfield1)) == 'cultivated':
                return Paragraph('<b>Cultivated specimen</b>', style = self.stylesheet(styleKey))
            else:
                return Paragraph('', style = self.stylesheet('default'))
            
        def gpsCoordStringer(textfield1,textfield2,textfield3,textfield4,styleKey):
            gpsString = []
            if len(dfl(textfield1)) > 0 :
                if (dfl(textfield1) and dfl(textfield2)):
                    # min([len(dfl(textfield1)),len(dfl(textfield2))]) testing length control.
                    gpsString.append('<b>GPS: </b>' + dfl(textfield1) + ', ' + dfl(textfield2))
                if dfl(textfield3):
                    gpsString.append(' ± ' + str(round(float(dfl(textfield3)),0)).split('.')[0] + 'm')
                if dfl(textfield4):
                    gpsString.append(', <b>Elevation: </b>' + dfl(textfield4) + 'm')
    
                return Paragraph(''.join(gpsString), style = self.stylesheet(styleKey))
    
        #############Logo Work#################################
        ##############################################################################
        #
        #logoPath = 'ucht.jpg'   # This should be determined by the user dialog open option.
        #
        #def getLogo(logoPath):
        #    if logoPath:
        #        return Image(logoPath, width = 40, height =30.6) #These values should be handled dynamically!
        ######Barcode work(Catalog Number)######
    
        def newHumanText(self):
            return self.stop and self.encoded[1:-1] or self.encoded
    
        def createBarCodes():   #Unsure of the benefits downsides of using extended vs standard?
            if len(dfl('catalogNumber')) > 0:
                barcodeValue = dfl('catalogNumber')
                code39._Code39Base._humanText = newHumanText  #Note, overriding the human text from this library to omit the stopcode ('+')
                barcode39Std = code39.Standard39(barcodeValue,barHeight=(yPaperSize * .10  ), barWidth=((xPaperSize * 0.28)/(len(barcodeValue)*13+35)), humanReadable=True, quiet = False, checksum=0)
                                                 #^^^Note width is dynamic, but I don't know the significe of *13+35 beyond making it work.
                return barcode39Std
            else:
                return ''
    
    
        elements = []      # a list to dump the flowables into for pdf generation
        for labelFieldsDict in labelData:
            def dfl(key):                       # dict lookup helper function
                value = labelFieldsDict.get(key,'') # return empty string if no result from lookup.
                return str(value)
    
        #Building list of flowable elements below
            if len(dfl('catalogNumber')) > 0:                   #If the catalog number is known, add the barcode. If not, don't.
                row0 = Table([[
                    Para('collectionName','collectionNameSTY'),
                    createBarCodes()
                              ]],
                colWidths = (xPaperSize * .67,xPaperSize * .29), rowHeights = None,
    
                style = [
                        ('VALIGN',(0,0),(0,-1),'TOP'),
                        ('ALIGN',(0,0),(0,0),'LEFT'),
                        ('ALIGN',(1,0),(1,0),'RIGHT'),
                         ])
            else:
                row0 = Para('collectionName','collectionNameSTY')
                    
    
            row1 = Table([
                [Para('samplingEffort','samplingEffortSTY')],
                [verifiedByPara('verifiedBy','verifiedBySTY')]],
                         colWidths = xPaperSize *.98, rowHeights = None,
                         style = [
                        ('BOTTOMPADDING',(0,0),(-1,-1), 2)]
                         )
    #bookmark
    #ScientificName Row Dynamic Formatting
        
            scientificNameElement = sciName('scientificName','scientificNameAuthorship','sciNameSTY')
            try:            #Test if Scienftific Name can Share a row with Event Date.
                scientificNameElement.wrap(1400, 1400) #Test wrap the string in a large environment to get it's desired ideal width.
                sciNameParaWidth = scientificNameElement.getActualLineWidths0()[0]
                sciHeight = scientificNameElement.height
            
            except (AttributeError, IndexError) as e:
                sciNameParaWidth = 0
    
            if sciNameParaWidth > xPaperSize *.96:  #If the string is so large as to not fit, even alone then shrink font and split lines into two rows.
                row2 = Table([[
                    Para('eventDate','dateSTY')],
                    [Spacer(width = xPaperSize *.98, height = sciHeight)], #Add spacer between rows for formatting.
                    [sciName('scientificName','scientificNameAuthorship','sciNameSTYSmall')]],
                        colWidths = xPaperSize *.98 , rowHeights = None, style = tableSty)
                    
            elif sciNameParaWidth > xPaperSize * -1:   #If the string is too big to share row with event date, split lines into rows.
                row2 = Table([[
                    Para('eventDate','dateSTY')],
                    [Spacer(width = xPaperSize *.98, height = sciHeight)],  #Add spacer between rows for formatting.
                    [sciName('scientificName','scientificNameAuthorship','sciNameSTY')]],
                        colWidths = xPaperSize *.98, rowHeights = None, style = tableSty)               
            else:
                row2 = Table([[
                    sciName('scientificName','scientificNameAuthorship','sciNameSTY'),
                    Para('eventDate','dateSTY')]],
                        colWidths = (xPaperSize * .80,xPaperSize * .18),
                        rowHeights = None, style = tableSty)
    
            row3 = Table([[
                    Para('locality','default')]],
                         rowHeights=None, style = tableSty)
    
            #Associated Taxa Dynamic Formatting
            if dfl('associatedTaxa') == '':         #If associated taxa is not used, give up the y space.
                associatedTaxaHeight = 0
                associatedTaxaStyle = 'defaultSTYSmall'   #This entire block is not functioning the way it was planned to.
            else:
                associatedTaxaHeight = .15 * yPaperSize          #Otherwise, devote some space, then test it's useage.
                associatedTaxaElement = Para('associatedTaxa','default','Associated taxa: ') #Test build for height
                try:
                    associatedTaxaParaHeight = associatedTaxaElement.wrap(xPaperSize *.98, 1)[1] #Test wrap the string in a large environment to get necessary height.
                except (AttributeError, IndexError) as e:
                    print('error ',e)
                    associatedTaxaParaHeight = 0
    
                if associatedTaxaParaHeight > associatedTaxaHeight:  #If the string is too large, reduce the font size.
                    associatedTaxaStyle = 'defaultSTYSmall'
                else:
                    associatedTaxaStyle = 'default'             #otherwise, use the normal height
            row4 = Table([[
                Para('associatedTaxa',associatedTaxaStyle,'Associated taxa: ')]],
                rowHeights=None,
                style = tableSty)
    #Note, associatedTaxa only reduces size if it is too large. At some extream point we'll need to consider trunication.
            
            if dfl('individualCount') != '':
                row5 = Table([[
                    Para('habitat','default','Habitat: '),
                    Para('individualCount','rightSTY', 'Approx. ≥ ',' on site.')]],
                    colWidths = (xPaperSize * .68,xPaperSize * .30), rowHeights = None,
                    style = [
                        ('VALIGN',(1,0),(1,0),'CENTER'),
                        ('ALIGN',(0,0),(0,0),'LEFT'),
                        ('ALIGN',(1,0),(1,0),'RIGHT'),
                        ('LEFTPADDING',(0,0),(-1,-1), 0),
                        ('RIGHTPADDING',(0,0),(-1,-1), 0),
                        ('TOPPADDING',(0,0),(-1,-1), 0),
                        ('BOTTOMPADDING',(0,0),(-1,-1), 0)])
            else:
                row5 = Table([[
                    Para('habitat','default','Habitat: ')]], style=tableSty)
    
            if dfl('establishmentMeans') == 'cultivated':  #If establishmentMeans status is not 'cultivated' (based on cultivated status in mobile app) then forfit the space in case Substrate field is long.
                row6 = Table([[
                Para('substrate','default','Substrate: '),
                cultivationStatusChecker('establishmentMeans','rightSTY')]],    
                colWidths = (xPaperSize * .68,xPaperSize * .30), rowHeights = None,
                style=tableSty)
                
            else:
                row6 = Table([[
                Para('substrate','default','Substrate: ')]],style=tableSty)
    
            row7 = [collectedByPara('recordedBy','associatedCollectors','default','Collected by: ')]
    
            row6_5 = Table([[
                Para('locationRemarks','default','Location Remarks: ')]],style=tableSty)
          #Note locationRemarks is in testing, may not stay!
    
            row6_7 = Table([[
                        Para('occurrenceRemarks','default','Occurence Remarks: ')]],style=tableSty)
                
            if dfl('identifiedBy') != '':
                row7_5 = Table([[
                        Para('identifiedBy','default','Determined by: ')]],style=tableSty)
            # TODO: Add all tableList (row) objects to a loop which checks for content and appends else returns None 
            # ...  Then Clean tableList for None objects
            
            tableList = [[row0],
                          [row1],
                          [row2],
                          [row3],
                          [row4],
                          [row5],
                          [row6],
                          [row6_5],
                          [row6_7],
                          [row7]]
    
            #Testing if GPS String can fit on one row with the field number. If not, split them into two rows.
            gpsStrElement = gpsCoordStringer('decimalLatitude', 'decimalLongitude', 'coordinateUncertaintyInMeters', 'minimumElevationInMeters','rightSTYSmall')
            try:
                gpsStrElement.wrap(xPaperSize * .98 , yPaperSize * .98)
                gpsParaWidth = gpsStrElement.getActualLineWidths0()[0]
            except AttributeError:
                gpsParaWidth = 0
                
            if gpsParaWidth > xPaperSize * .65:
                row8 = Table([[Para('otherCatalogNumbers','default','Field Number: ')]], style = tableSty)
                row9 = Table([[gpsStrElement]],style = tableSty)
                tableList.append([row8])
    
                if dfl('identifiedBy') != '':
                    tableList.append([row7_5])
    
                tableList.append([row9])
                
            else:
                row8 = Table([[
                Para('otherCatalogNumbers','default','Field Number: '),        
                gpsStrElement]],            
                colWidths = (xPaperSize * .33, xPaperSize * .65), rowHeights = None,style=tableSty)
                tableList.append([row8])
    
                if dfl('identifiedBy') != '':
                    tableList.append([row7_5])
    
            # append the determined by field
            
            
            docTableStyle = [                             #Cell alignment and padding settings (not text align within cells)
                    ('VALIGN',(0,3),(0,-1),'BOTTOM'),     #Rows 4-end align to bottom
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),     #All rows align to center
                    ('LEFTPADDING',(0,0),(-1,-1), 0),     #ALL Rows padding on left to none
                    ('RIGHTPADDING',(0,0),(-1,-1), 0),    #ALL Rows padding on right to none
                    ('TOPPADDING',(0,0),(-1,-1), 3),      #ALL Rows padding on top to none
                    ('BOTTOMPADDING',(0,0),(-1,-1), 0),   #ALL Rows padding on Bottom to none
                    ('BOTTOMPADDING',(0,0),(0,0), 3),     #ALL Rows padding on Bottom to none
                    ('TOPPADDING',(0,1),(0,1), 6),        #Row 2 top padding to 6
                    ('TOPPADDING',(0,2),(0,2), 6),        #Row 3 top padding to 6
                    ('BOTTOMPADDING',(0,2),(0,2), 6),     #Row 3 bottom padding to 6
                    #('NOSPLIT', (0,0),(-1,-1)),          #Makes Error if it won't fit. We should raise this error to user!
                                ]
            
            docTable = Table(tableList, style = docTableStyle ) #build the table to test it's height
    
            wid, hei = docTable.wrap(0, 0)      #Determines how much space is used by the table
            spaceRemaining = (yPaperSize - hei - 10) #Determine how much is left on the page
            spaceFiller = [Spacer(width = 0, height = (spaceRemaining/3))] #assign half the remaining space to a filler (to distrib into two places.
            tableList.insert(4,spaceFiller)     #build from bottom up because it is less confusing for the index values.
            tableList.insert(3,spaceFiller)
            tableList.insert(2,spaceFiller)
    
            docTable = Table(tableList, style = docTableStyle ) #build the final table
    
            #Add the flowables to the elements list.
            elements.append(docTable)
            elements.append(PageBreak())
        
        #Bookmark
        #Build the base document's parameters.
        
        if returnBytes:  # if we only want to make a preview save it to a stream
            byteStream = io.BytesIO()
            labelFileName = byteStream

        elif defaultFileName:
            labelFileName = QFileDialog.getSaveFileName(self, 'Save Label PDF', defaultFileName, 'PDF(*.pdf)')
        else:
            labelFileName = QFileDialog.getSaveFileName(self, 'Save Label PDF', os.getenv('HOME'), 'PDF(*.pdf)')
        #if labelFileName[0] == '':  # option to check if the user actually used the dialog
                
        doc = BaseDocTemplate(labelFileName,
         pagesize=customPageSize,
         pageTemplates=[],
         showBoundary=0,
         leftMargin=xMargin,
         rightMargin=xMargin,
         topMargin=yMargin,
         bottomMargin=yMargin,
         allowSplitting=1,           
         title=None,
         author=None,
         _pageBreakQuick=1,
         encrypt=None)
    
        #Function to build the pdf
    
        def build_pdf(flowables):
            doc.addPageTemplates(
                [
                    PageTemplate(
                        frames=[
                            platypusFrame(
                                doc.leftMargin,
                                doc.bottomMargin,
                                doc.width,
                                doc.height,
                                topPadding=0,
                                bottomPadding=0,
                                id=None
                            ),
                        ]
                    ),
                ]
            )
            doc.build(flowables)
        #Actually build the pdf
        build_pdf(elements)
        
        if returnBytes:  # If a preview is being generated just return the bytes
            # calling the byte stream "labelFileName" is a fast and dirty 
            # workaround to keep existing code functional
            pdfBytes = labelFileName.getvalue()  # save the stream to a variable
            buffer.close()  # close the buffer down
            return pdfBytes  # return the results
        
        #Open the file after it is built (maybe change/remove this later? Idealy, a preview or something
    
        def open_file(filename):
            if sys.platform == "win32":
                os.startfile(filename)
            else:
                opener ="open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, filename])
        open_file(labelFileName)


    def stylesheet(self, key):
        styles= {
            'default': ParagraphStyle(
                'default',
                fontName='Times-Roman',
                fontSize=relFont,
                leading=(relFont * 1.1) ,
                leftIndent=0,
                rightIndent=0,
                firstLineIndent=0,
                alignment=TA_LEFT,
                spaceBefore=0,
                spaceAfter=0,
                bulletFontName='Times-Roman',
                bulletFontSize=10,
                bulletIndent=0,
                backColor=None,
                wordWrap=(xPaperSize,yPaperSize),
                borderWidth= 0,
                borderPadding= 0,
                borderColor= None,
                borderRadius= None,
                allowWidows= 1,
                allowOrphans= 0,
                textTransform=None,  # options: 'uppercase' | 'lowercase' | None
                endDots=None,         
                splitLongWords=1,
            ),
        }
        styles['title'] = ParagraphStyle(
            'title',
            parent=styles['default'],
            fontName='Times-Bold',
            fontSize= relFont * 1.2,
            alignment=TA_CENTER,
        )
        styles['collectionNameSTY'] = ParagraphStyle(
            'collectionNameSTY',
            parent=styles['title'],
            fontName='Times',
            fontSize= relFont * .8,
            alignment=TA_CENTER,
        )
        styles['samplingEffortSTY'] = ParagraphStyle(
            'samplingEffortSTY',
            parent=styles['title'],
            fontName='Times-Bold',
            fontSize= relFont * 1.18,
            alignment=TA_CENTER,
        )
        styles['dateSTY'] = ParagraphStyle(
            'dateSTY',
            parent=styles['title'],
            fontName='Times',
            fontSize= relFont * 1.18,
            alignment=TA_RIGHT,
        )
        styles['authoritySTY'] = ParagraphStyle(
            'authoritySTY',
            parent=styles['default'],
            fontSize= relFont * 1.18,
            alignment=TA_LEFT
        )
        styles['sciNameSTY'] = ParagraphStyle(
            'sciNameSTY',
            parent=styles['default'],
            fontSize= relFont * 1.18,
            alignment=TA_LEFT,
            spaceAfter = 1
            
        )
        styles['sciNameSTYSmall'] = ParagraphStyle(
            'sciNameSTYSmall',
            parent=styles['default'],
            fontSize= relFont,
            alignment=TA_LEFT,
            spaceAfter = 1
            
        )
        styles['defaultSTYSmall'] = ParagraphStyle(
            'defaultSTYSmall',
            parent=styles['default'],
            fontSize= relFont * .80,
        )

        styles['verifiedBySTY'] = ParagraphStyle(
            'verifiedBySTY',
            parent=styles['default'],
            fontSize= relFont * .80,
            alignment=TA_CENTER,
            borderPadding=2,
        )
        styles['rightSTY'] = ParagraphStyle(
            'rightSTY',
            parent=styles['default'],
            alignment=TA_RIGHT,
            spaceAfter = 1,
        )
        styles['rightSTYSmall'] = ParagraphStyle(
            'rightSTY',
            parent=styles['default'],
            fontSize= relFont * .80,
            alignment=TA_RIGHT,
            spaceAfter = 1,
        )        
        styles['prefixLeftSTY'] = ParagraphStyle(
            'prefixLeftSTY',
            parent=styles['default'],
            alignment=TA_LEFT,
            spaceAfter = 1,
            fontName='Times-Bold'
        )
        styles['prefixRightSTY'] = ParagraphStyle(
            'prefixRightSTY',
            parent=styles['default'],
            alignment=TA_RIGHT,
            spaceAfter = 1,
            fontName='Times-Bold'
        )
        styles['countySTY'] = ParagraphStyle(
            'countySTY',
            parent=styles['default'],
            alignment=TA_CENTER,
            spaceAfter = 1,
            fontName='Times'
        )
        return styles.get(key)
