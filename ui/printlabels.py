#!/usr/bin/env python
from reportlab.platypus import Table, BaseDocTemplate, SimpleDocTemplate, PageTemplate, PageBreak
from reportlab.platypus import Frame as platypusFrame   #NOTE SEE Special case import here to avoid namespace conflict with "Frame"
from reportlab.platypus.flowables import Spacer, KeepInFrame
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.doctemplate import LayoutError
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from PIL import Image, ImageFilter
import math
import os
import sys
import io

# TODO with the conversion to pyqt5, pymupdf should allow us to display & open 
# print dialogs for the pdfs without relying on system installed pdf viewer

# TODO investigate stringWidth function to simplify the width checking options.
# see: https://stackoverflow.com/questions/27732213/how-to-add-bold-and-normal-text-in-one-line-using-drawstring-method-in-reportlab

import subprocess

from PyQt5.QtWidgets import QFileDialog

# This entire module needs clean up,
# dynamic spacing needs redesigned and simplified
# before size options are added.

class LabelPDF():

    def __init__(self, settings):
        """ xPaperSize, & self.yPaperSize are each assumed to be in mm """
        self.settings = settings
        self.useLogo = self.settings.get('value_inc_Logo',False)
        self.logoPath = self.settings.get('value_LogoPath', '')
        self.opacity = 0
        self.logo = False
        if self.useLogo:
            self.initLogoCanvas()

    def initLogoCanvas(self):
        """ initalizes the logo and stores it in memory to be applied to each
        label (and label preview). """
        # save variables to avoid looking them up for every preview.
        self.useLogo = self.settings.get('value_inc_Logo',False)
        if self.useLogo:
            self.logoPath = self.settings.get('value_LogoPath', '')
            if self.logoPath != '':
                self.opacity = int(self.settings.get('value_LogoOpacity', 30)) / 100
                self.useLogo = self.settings.get('value_LogoPath',False)
                # start to set up the logo
                logoPath = self.settings.get('value_LogoPath')
                logoScaling = int(self.settings.get('value_LogoScaling', 100)) / 100
                logoMargin = int(self.settings.get('value_LogoMargin', 2))
                try:
                    im = Image.open(logoPath)

                except:  # if the path provided seems broken, clear the setting
                    self.logoPath = ''
                    self.settings.setValue('value_LogoPath','')
                    self.settings.settingsWindow.value_LogoPath.setText('')
                    return
                logoDPIx, logoDPIy = im.info['dpi']  # get DPI of input logo image
                label_X = int(self.settings.get('value_X'))  # get mm size of labels
                label_X = int(label_X * mm)
                label_Y = int(self.settings.get('value_Y'))
                label_Y = int(label_Y * mm)
                # resize the image to fit within the label dimentions
                # then expand the image to the proper ratio filling alpha values in.
                maxsize = (int(label_X * logoScaling), int(label_Y * logoScaling))
                im.thumbnail(maxsize, Image.ANTIALIAS)       
                im = im.filter(ImageFilter.SHARPEN) # sharpen to clean up scaling losses
                logoWidth, logoHeight = im.size  # get size of image
                # align image on the backdrop.
                logoAlignment = self.settings.get('value_LogoAlignment')
                if logoAlignment == 'Upper Left':
                    x1 = logoMargin
                    y1 = logoMargin
                elif logoAlignment == 'Upper Center':
                    x1 = int(math.floor((label_X - logoWidth) / 2))
                    y1 = logoMargin
                elif logoAlignment == 'Upper Right':
                    x1 = int(label_X - logoWidth) -logoMargin
                    y1 = logoMargin
                elif logoAlignment == 'Center Left':
                    x1 = 2
                    y1 = int(math.floor((label_Y - logoHeight) / 2))
                elif logoAlignment == 'Center Right':
                    x1 = int(label_X - logoWidth) -logoMargin
                    y1 = int(math.floor((label_Y - logoHeight) / 2))
                elif logoAlignment == 'Lower Left':
                    x1 = logoMargin
                    y1 = int(label_Y - logoHeight) - logoMargin
                elif logoAlignment == 'Lower Center':
                    x1 = int(math.floor((label_X - logoWidth) / 2))
                    y1 = int(label_Y - logoHeight) - logoMargin
                elif logoAlignment == 'Lower Right':
                    x1 = int(label_X - logoWidth) -logoMargin
                    y1 = int(label_Y - logoHeight) - logoMargin
                else:  # it is probably 'center'     
                    x1 = int(math.floor((label_X - logoWidth) / 2))
                    y1 = int(math.floor((label_Y - logoHeight) / 2))       
    
                mode = im.mode
                if len(mode) == 1:  # L, 1
                    new_background = (255)
                if len(mode) == 3:  # RGB
                    new_background = (255, 255, 255)
                if len(mode) == 4:  # RGBA, CMYK
                    new_background = (255, 255, 255, 255)
                resizedLogo = Image.new(mode, (label_X, label_Y), new_background)
                resizedLogo.paste(im, (x1, y1, x1 + logoWidth, y1 + logoHeight))
                logoData = io.BytesIO()
                #im.save('imlocalSave.png',quality=100)
                resizedLogo.save(logoData, format='PNG', quality=95, optimize = True)
                resizedLogo.seek(0)
                logo = ImageReader(logoData)     
    
                self.logo = logo

    def labelSetup(self, c, doc):
        """ Applies a logo to the pdf's background """
        if isinstance(self.logo, ImageReader) and self.useLogo :
            c.saveState()
            c._setFillAlpha(self.opacity)
            c.drawImage(self.logo, 0, 0)#, width=logoWidth, height=logoHeight, preserveAspectRatio = True, anchor = logoAlignment)
            c.restoreState()  

    def genLabelPreview(self, labelDataInput):
         # Get the value of the BytesIO buffer and write it to the response.
         pdfBytes = self.genPrintLabelPDFs(labelDataInput, returnBytes = True)
         return pdfBytes

    def genPrintLabelPDFs(self, labelDataInput, defaultFileName = None, returnBytes = False):
        """labelDataInput = list of dictionaries formatted as: {DWC Column:'field value'}
           defaultFileName = the filename to use as the default when saving the pdf file.
           returnBytes = If the result should be a bytes object (used for label previews).
           Otherwise, produces (and attempts to open) a pdf file."""

        # strip out the site number rows
        try:
            labelDataInput = [x for x in labelDataInput if x.get('specimenNumber') != "#"]
        except AttributeError:
            labelDataInput = [x for x in labelDataInput if "#" not in x.get('recordNumber').split('-')[-1]]
        if len(labelDataInput) < 1:  # exit early if nothing is left
            return None

        # decent default values 140, 90
        self.xPaperSize = int(self.settings.get('value_X', 140)) * mm
        self.yPaperSize = int(self.settings.get('value_Y', 90)) * mm
        self.relFont = int(self.settings.get('value_RelFont', 12))
         # TODO explore adding font options which are already bundled with reportlab
        self.fontName = self.settings.get('value_fontName', 'Helvetica')
         
        self.allowSplitting = 0
        self.xMarginProportion = 0
        self.yMarginProportion = 0   #Padding on tables are functionally the margins in our use. (We're claiming most of paper)
        self.xMargin = self.xMarginProportion * self.xPaperSize        #Margin set up (dynamically depending on paper sizes.
        self.yMargin = self.xMarginProportion * self.yPaperSize
        self.customPageSize = (self.xPaperSize, self.yPaperSize)
        
        # check some of the optional label settings, & make adjustments.
        additionalData = {}
        if self.settings.get('value_inc_VerifiedBy'):
            additionalData['verifiedBy'] = self.settings.get('value_VerifiedBy')
        else:
            additionalData['verifiedBy'] = ''
        if self.settings.get('value_inc_CollectionName'):
            additionalData['collectionName'] = self.settings.get('value_CollectionName')
        else:
            additionalData['collectionName'] = ''
        # setting these now, to avoid redundant .get calls.
        incAssociated = self.settings.get('value_inc_Associated')
        italicizeAssociated = self.settings.get('value_italicize_Associated')
        maxAssociated = int(self.settings.get('value_max_Associated'))
        tripName = self.settings.get('value_inc_TripName', False)
        for rowData in labelDataInput:
            if incAssociated:
                associatedTaxa = rowData['associatedTaxa']
                associatedTaxaItems = associatedTaxa.split(', ')
                if len(associatedTaxaItems) > maxAssociated: #if it is too large, trunicate it, and append "..." to indicate trunication.
                    associatedTaxa =  ', '.join(associatedTaxaItems[:maxAssociated])+' ...'
                if italicizeAssociated:
                    associatedTaxa = f"<i>{associatedTaxa}</i>"
                rowData['associatedTaxa'] = associatedTaxa
            else:
                rowData['associatedTaxa'] = ''
            if not tripName:
                # label project is already handed in, nullify it if user opted against it on label.
                rowData['Label Project'] = ''
            for key, value in additionalData.items():
                rowData[key] = value

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
            # break out the textValues
            textContent1 = dfl(textfield1)
            textContent2 = dfl(textfield2)
            
            if textContent1 != '': #  if textContent has content
                if ('|' in textfield1) & (textfield2 == ''): #  if it has a |
                    splitCollectors = textContent1.split('|',1) # split on |
                    #  if it is a list & it has 2 elements, assign them 
                    if len(splitCollectors) == 2:
                        textContent1, textContent2 = splitCollectors
            elif textContent2 != '':
                # if there is no primariy collector, but there are associated collector(s)
                if ('|' in textfield2):
                    splitCollectors = textContent2.split('|',1) # split on |
                    if len(splitCollectors) == 2:
                        textContent1, textContent2 = splitCollectors
            # condition of remaining collectors in textContent2 delimited by |
            if '|' in textContent2:
                #  split on | delimiter
                splitCollectors = textContent2.split('|')
                #  strip out trailing/leading spaces and empty strings.
                splitCollectors = [x.strip() for x in splitCollectors if x != '']
                #  rejoin as single, cleaned string.
                splitCollectors = ', '.join(splitCollectors)
                        
            if (isinstance(textContent1, str) & (textContent1 != '') & (textContent2 != '')):
                return Paragraph(('<b>{}</b>'.format(prefix)) + textContent1 + ' with ' + textContent2, style = self.stylesheet(styleKey))
            elif (isinstance(textContent1, str) & (textContent1 != '')):
                return Paragraph(('<b>{}</b>'.format(prefix)) + textContent1, style = self.stylesheet(styleKey))
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

        def newHumanText(self):
            return self.stop and self.encoded[1:-1] or self.encoded
    
        def createBarCodes():   #Unsure of the benefits downsides of using extended vs standard?
            if len(dfl('catalogNumber')) > 0:
                barcodeValue = dfl('catalogNumber')
            else:
                barcodeValue =  self.settings.dummyCatNumber
            if barcodeValue:
                barcode128  = code128.Code128(barcodeValue,barHeight=(self.yPaperSize * .10  ), barWidth=((self.xPaperSize * 0.28)/(len(barcodeValue)*13+35)), humanReadable=True, quiet = False, checksum=0)
                                    #^^^Note width is dynamic, but I don't know the significe of *13+35 beyond making it work.
                return barcode128  
            else:
                return ''
        elements = []      # a list to dump the flowables into for pdf generation
        for labelFieldsDict in labelDataInput:
            def dfl(key):                       # dict lookup helper function
                value = labelFieldsDict.get(key,'') # return empty string if no result from lookup.
                return str(value)

        #Building list of flowable elements below
            if (len(dfl('catalogNumber')) > 0) | (self.settings.dummyCatNumber != False):
                row0 = Table([[
                    Para('collectionName','collectionNameSTY'),
                    createBarCodes()
                              ]],
                colWidths = (self.xPaperSize * .67,self.xPaperSize * .29), rowHeights = None,
    
                style = [
                        ('VALIGN',(0,0),(0,-1),'TOP'),
                        ('ALIGN',(0,0),(0,0),'LEFT'),
                        ('ALIGN',(1,0),(1,0),'RIGHT'),
                         ])
            else:
                row0 = Table([
                        [Para('collectionName','collectionNameSTY')],
                        [Para('family', 'familyNameSTY')]])
                    
    
            row1 = Table([
                [Para('Label Project','labelProjectSTY')],
                [verifiedByPara('verifiedBy','verifiedBySTY')]],
                         colWidths = self.xPaperSize *.98, rowHeights = None,
                         style = [
                        ('BOTTOMPADDING',(0,0),(-1,-1), 2)]
                         )
            #ScientificName Row Dynamic Formatting
            scientificNameElement = sciName('scientificName','scientificNameAuthorship','sciNameSTY')
            try:            #Test if Scienftific Name can Share a row with Event Date.
                scientificNameElement.wrap(1400, 1400) #Test wrap the string in a large environment to get it's desired ideal width.
                sciNameParaWidth = scientificNameElement.getActualLineWidths0()[0]
                sciHeight = scientificNameElement.height
            
            except (AttributeError, IndexError) as e:
                sciNameParaWidth = 0
                sciHeight = 0
    
            if sciNameParaWidth > self.xPaperSize *.96:  #If the string is so large as to not fit, even alone then shrink font and split lines into two rows.
                row2 = Table([[
                    Para('eventDate','dateSTY')],
                    [Spacer(width = self.xPaperSize *.98, height = sciHeight)], #Add spacer between rows for formatting.
                    [sciName('scientificName','scientificNameAuthorship','sciNameSTYSmall')]],
                        colWidths = self.xPaperSize *.98 , rowHeights = None, style = tableSty)
                    
            elif sciNameParaWidth > self.xPaperSize * -1:   #If the string is too big to share row with event date, split lines into rows.
                row2 = Table([[
                    Para('eventDate','dateSTY')],
                    [Spacer(width = self.xPaperSize *.98, height = sciHeight)],  #Add spacer between rows for formatting.
                    [sciName('scientificName','scientificNameAuthorship','sciNameSTY')]],
                        colWidths = self.xPaperSize *.98, rowHeights = None, style = tableSty)               
            else:
                row2 = Table([[
                    sciName('scientificName','scientificNameAuthorship','sciNameSTY'),
                    Para('eventDate','dateSTY')]],
                        colWidths = (self.xPaperSize * .80,self.xPaperSize * .18),
                        rowHeights = None, style = tableSty)
    
            row3 = Table([[
                    Para('locality','default')]],
                         rowHeights=None, style = tableSty)
    
            #Associated Taxa Dynamic Formatting
            if dfl('associatedTaxa') == '':         #If associated taxa is not used, give up the y space.
                associatedTaxaHeight = 0
                associatedTaxaStyle = 'defaultSTYSmall'   #This entire block is not functioning the way it was planned to.
            else:
                associatedTaxaHeight = .15 * self.yPaperSize          #Otherwise, devote some space, then test it's useage.
                associatedTaxaElement = Para('associatedTaxa','default','Associated taxa: ') #Test build for height
                try:
                    associatedTaxaParaHeight = associatedTaxaElement.wrap(self.xPaperSize *.98, 1)[1] #Test wrap the string in a large environment to get necessary height.
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
                    colWidths = (self.xPaperSize * .68,self.xPaperSize * .30), rowHeights = None,
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
                colWidths = (self.xPaperSize * .68,self.xPaperSize * .30), rowHeights = None,
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
                gpsStrElement.wrap(self.xPaperSize * .98 , self.yPaperSize * .98)
                try:
                    gpsParaWidth = gpsStrElement.getActualLineWidths0()[0]
                except IndexError:
                    gpsParaWidth = 0
            except AttributeError:
                gpsParaWidth = 0
                
            if gpsParaWidth > self.xPaperSize * .65:
                row8 = Table([[Para('recordNumber','default','Field Number: ')]], style = tableSty)
                row9 = Table([[gpsStrElement]],style = tableSty)
                tableList.append([row8])
    
                if dfl('identifiedBy') != '':
                    tableList.append([row7_5])
    
                tableList.append([row9])
                
            else:
                row8 = Table([[
                Para('recordNumber','default','Field Number: '),        
                gpsStrElement]],            
                colWidths = (self.xPaperSize * .33, self.xPaperSize * .65), rowHeights = None,style=tableSty)
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
            spaceRemaining = (self.yPaperSize - hei - 10) #Determine how much is left on the page
            spaceFiller = [Spacer(width = 0, height = (spaceRemaining/3))] #assign half the remaining space to a filler (to distrib into two places.
            tableList.insert(4,spaceFiller)     #build from bottom up because it is less confusing for the index values.
            tableList.insert(3,spaceFiller)
            tableList.insert(2,spaceFiller)
    
            docTable = Table(tableList, style = docTableStyle ) #build the final table
    
            #Add the flowables to the elements list.
            elements.append(docTable)
            elements.append(PageBreak())

        #Build the base document's parameters.
        
        if returnBytes:  # if we only want to make a preview save it to a stream
            byteStream = io.BytesIO()
            labelFileName = byteStream

        elif defaultFileName:
            labelFileName = defaultFileName
            #labelFileName, _ = QFileDialog.getSaveFileName(None, 'Save Label PDF', defaultFileName, 'PDF(*.pdf)')
        else:
            labelFileName, _ = QFileDialog.getSaveFileName(None, 'Save Label PDF', os.getenv('HOME'), 'PDF(*.pdf)')

        if not labelFileName:  # If the user canceled the dialog
            return
        # TODO fill in title and author based on select form_view or settings info                
        doc = BaseDocTemplate(labelFileName,
                              pagesize=self.customPageSize,
                              pageTemplates=[],
                              showBoundary=0,
                              leftMargin=self.xMargin,
                              rightMargin=self.xMargin,
                              topMargin=self.yMargin,
                              bottomMargin=self.yMargin,
                              allowSplitting= self.allowSplitting,           
                              title=None,
                              author=None,
                              _pageBreakQuick=1,
                              encrypt=None)
    
        #Function to build the pdf
    
        def build_pdf(flowables):
            """ actually loads the flowables into the document """

            doc.addPageTemplates(
                [
                    PageTemplate(
                        onPage = self.labelSetup,
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
            try:
                doc.build(flowables)
            except LayoutError:
                raise LayoutError
        
        try:
            build_pdf(elements)
        except LayoutError:
            # if there is a layout error, raise it
            raise LayoutError
        
        if returnBytes:  # If a preview is being generated just return the bytes
            # calling the byte stream "labelFileName" is a fast and dirty 
            # workaround to keep existing code functional
            pdfBytes = labelFileName.getvalue()  # save the stream to a variable
            labelFileName.close()  # close the buffer down
            return pdfBytes  # return the results
        
        #Open the file after it is built (maybe change/remove this later? Idealy, a preview or something
    
        def open_file(filename):
            if sys.platform == "win32":
                os.startfile(filename)
            else:
                opener ="open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, filename])
        open_file(labelFileName)


    def genErrorLabel(self, errorMSG, relFont=None):
        """ Generates a PDF with the errorMSG clearly printed. Used as a
        simple solution to displaying errors inside the pdfviewer which
        can be easily, correctly, scaled and manipulated by the viewer."""

        labelFileName = io.BytesIO()
        self.xPaperSize = int(self.settings.get('value_X', 140)) * mm
        self.yPaperSize = int(self.settings.get('value_Y', 90)) * mm
        self.customPageSize = (self.xPaperSize, self.yPaperSize)
        self.relFont = int(self.settings.get('value_RelFont', 12))
        self.fontName = self.settings.get('value_fontName', 'Helvetica')
        style = ParagraphStyle(
                name = 'test',
                fontName= f'{self.fontName}-Bold',
                fontSize= self.relFont * 1.5,
                textColor='Grey',
                alignment=TA_CENTER)
        
        fontSize = style.fontSize
        pageStrW = max([stringWidth(x, style.fontName, fontSize) for x in errorMSG])
        availWidth = self.xPaperSize *.9
        # because the label size can be user set, and best to avoid altering it
        # for error windows, dynamically determine fontsize that fits.
        while availWidth < pageStrW and fontSize > 1:
            fontSize = fontSize * .9
            pageStrW = max([stringWidth(x, style.fontName, fontSize) for x in errorMSG])

        doc =  SimpleDocTemplate(labelFileName, 
                            pagesize= self.customPageSize,
                            showBoundary=0,
                            leftMargin=1,
                            rightMargin=1,
                            topMargin=1,
                            bottomMargin=1,
                            allowSplitting= False,           
                            title=None,
                            author=None,
                            _pageBreakQuick=1,
                            encrypt=None)
        style.fontSize = fontSize
        content = [Paragraph(x, style) for x in errorMSG]
        #  determine the length of a vert spacer to roughly center the errorMSG  
        pageStrH = max([x.wrap(self.xPaperSize *.9, 100000)[1] for x in content])
        spacerHeight = self.yPaperSize * .40 - pageStrH
        flowables = []
        flowables.append(Spacer(0, spacerHeight))
        flowables.extend(content)
        doc.build(flowables)

        pdfBytes = labelFileName.getvalue()  # save the stream to a variable
        labelFileName.close()  # close the buffer down
        return pdfBytes

    def stylesheet(self, key):
        usrFont = self.fontName
        styles= {
            'default': ParagraphStyle(
                'default',
                fontName= f'{usrFont}',
                fontSize=self.relFont,
                leading=(self.relFont * 1.1) ,
                leftIndent=0,
                rightIndent=0,
                firstLineIndent=0,
                alignment=TA_LEFT,
                spaceBefore=0,
                spaceAfter=0,
                bulletFontName=f'{usrFont}',
                bulletFontSize=10,
                bulletIndent=0,
                backColor=None,
                wordWrap=(self.xPaperSize,self.yPaperSize),
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
            fontName= f'{usrFont}-Bold',
            fontSize= self.relFont * 1.2,
            alignment=TA_CENTER,
        )
        styles['collectionNameSTY'] = ParagraphStyle(
            'collectionNameSTY',
            parent=styles['title'],
            fontName=f'{usrFont}-Bold',
            fontSize= self.relFont,
            alignment=TA_CENTER,
        )
        styles['familyNameSTY'] = ParagraphStyle(
            'familyNameSTY',
            parent=styles['title'],
            fontName=f'{usrFont}',
            fontSize= self.relFont,
            alignment=TA_CENTER,
            textTransform='uppercase'
        )
        styles['labelProjectSTY'] = ParagraphStyle(
            'labelProjectSTY',
            parent=styles['title'],
            fontName=f'{usrFont}-Bold',
            fontSize= self.relFont * 1.18,
            alignment=TA_CENTER,
        )
        styles['dateSTY'] = ParagraphStyle(
            'dateSTY',
            parent=styles['title'],
            fontName= f'{usrFont}',
            fontSize= self.relFont * 1.18,
            alignment=TA_RIGHT,
        )
        styles['authoritySTY'] = ParagraphStyle(
            'authoritySTY',
            parent=styles['default'],
            fontSize= self.relFont * 1.18,
            alignment=TA_LEFT
        )
        styles['sciNameSTY'] = ParagraphStyle(
            'sciNameSTY',
            parent=styles['default'],
            fontSize= self.relFont * 1.18,
            alignment=TA_LEFT,
            spaceAfter = 1
            
        )
        styles['sciNameSTYSmall'] = ParagraphStyle(
            'sciNameSTYSmall',
            parent=styles['default'],
            fontSize= self.relFont,
            alignment=TA_LEFT,
            spaceAfter = 1
            
        )
        styles['defaultSTYSmall'] = ParagraphStyle(
            'defaultSTYSmall',
            parent=styles['default'],
            fontSize= self.relFont * .80,
        )

        styles['verifiedBySTY'] = ParagraphStyle(
            'verifiedBySTY',
            parent=styles['default'],
            fontSize= self.relFont * .80,
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
            fontSize= self.relFont * .80,
            alignment=TA_RIGHT,
            spaceAfter = 1,
        )        
        styles['prefixLeftSTY'] = ParagraphStyle(
            'prefixLeftSTY',
            parent=styles['default'],
            alignment=TA_LEFT,
            spaceAfter = 1,
            fontName=f'{usrFont}-Bold'
        )
        styles['prefixRightSTY'] = ParagraphStyle(
            'prefixRightSTY',
            parent=styles['default'],
            alignment=TA_RIGHT,
            spaceAfter = 1,
            fontName=f'{usrFont}-Bold',
        )
        styles['countySTY'] = ParagraphStyle(
            'countySTY',
            parent=styles['default'],
            alignment=TA_CENTER,
            spaceAfter = 1,
            fontName=f'{usrFont}'
        )
        styles['errorMSG'] = ParagraphStyle(
            'title',
            parent=styles['default'],
            fontName=f'{usrFont}-Bold',
            fontSize= self.relFont * 1.5,
            textColor='Grey',
            alignment=TA_CENTER

        )
        return styles.get(key)
