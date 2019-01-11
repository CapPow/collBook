#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 11 10:33:55 2019

@authors: Caleb Powell, Jacob Motley

"""
import pandas as pd
import re
import Resources_rc
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QFile



class taxonomicVerification():
    def __init__(self, settings, editable = True, *args):
        super(taxonomicVerification, self).__init__()
        
        self.settings = settings       
        # precompile regex cleaning string to save time.
        self.strNormRegex = re.compile('[^a-z ]')
        
    def readTaxonomicSettings(self):
        """ Fetches the most up-to-date taxonomy relevant settings"""
        #which service to utalize to make alignments
        self.TaxAlignSource = self.settings.get('value_TaxAlignSource')
        # how to handle name reccomendations
        self.NameChangePolicy = self.settings.get('value_NameChangePolicy')
        # how to handle authority reccomendations
        self.AuthChangePolicy = self.settings.get('value_AuthChangePolicy')
        #if self.NameChangePolicy == 'ITIS (local)':
        if self.TaxAlignSource == 'ITIS (local)':       
            from io import StringIO
            stream = QFile(':/rc_/itis_Taxonomy_Reference.csv')
            if stream.open(QFile.ReadOnly):
                df = StringIO(str(stream.readAll(), 'utf-8'))
                stream.close()
            self.itis_Taxonomy_Reference = pd.read_csv(df, encoding = 'utf-8', dtype = 'str')

    
    def verifyTaxonomy(self, rowData):
        """general method to align taxonomy and retrieve authority.
        accepts a df row argument, treats it as a dictionary and makes
        refinements. Returning a the modified argument."""
        
        rowNum = f"{rowData['site#']}-{rowData['specimen#']}"     
        scientificName = rowData['scientificName']
        scientificNameAuthorship = rowData['scientificNameAuthorship']
        inputSciName = scientificName
        querySciName = self.normalizeStrInput(scientificName)
        
        if self.TaxAlignSource == 'Catalog of Life (web API)':
            result = getCOL(querySciName)
        elif self.TaxAlignSource == 'ITIS (local)':
            result = self.getITISLocal(querySciName)
        elif self.TaxAlignSource == 'ITIS (web API)':
            result = getITISWeb(querySciName)
        elif self.TaxAlignSource == 'Taxonomic Name Resolution Service (web API)':
            result = getTNRS(querySciName)
        else:
            result = (None, None)
            
        resultSciName, resultAuthor = result
        
        # determine how to handle resulting data
        if resultSciName not in [scientificName, None]:
            if self.NameChangePolicy == 'Accept all suggestions':
                rowData['scientificName'] = resultSciName
            elif self.NameChangePolicy == 'Always ask':
                 message = f'Change {scientificName} to {resultSciName} at record {rowNum}?'
                 answer = self.userAsk(message)
                 if answer:
                     rowData['scientificName'] = resultSciName
                     rowData['scientificNameAuthorship'] = resultAuthor
        return rowData
#                else:
#                    return currentRowArg
#            elif self.nameChangePolicy == 'Fill blanks':
            
            
 #       if resultAuthor != scientificNameAuthorship:
 #           if self.value_AuthChangePolicy == 'Accept all suggestions'
 #           elif self.value_AuthChangePolicy == 'Always ask'

        
    def normalizeStrInput(self, inputStr):
        """ returns a normalized a scientificName based on string input.
        is used to prepare queries """
        # Strip non-alpha characters
        # Strip additional whitespace from ends
        toCleanString = inputStr.lower()
        toCleanString = self.strNormRegex.sub('', toCleanString).strip()
        wordList = toCleanString.split()
        if len(wordList) > 2:
            omitList = ['var', 'ssp', 'subsp', 'x', 'f']
            toCleanString = ' '.join([x for x in wordList if x not in omitList])
        outputStr = toCleanString
        
        return outputStr

# still work to do here
    def getITISLocal(self, inputStr):
        """ uses local itis reference csv to attempt alignments """
        df = self.itis_Taxonomy_Reference
        result = (None, None)
        try:
            tsn_accepted = df[df['normalized_name'] == inputStr]['tsn_accepted'].mode()[0]
        except IndexError:
            return result
        acceptedRow = df[df['tsn'] == tsn_accepted]
        if len(acceptedRow) > 0:
            acceptedName = acceptedRow['complete_name'].mode()[0]
            acceptedAuthor = acceptedRow['taxon_author_id'].mode()[0]
            result = (acceptedName, acceptedAuthor)

        
        return result
    
    def retrieveIPTJSON(url, retryCount = 0):
        if retryCount > 3:
            print( print(f'JSON errors, gave up on: {url}'))
            return {}
        try:
            result = json.loads(requests.get(url=url).content).get('items')[0]
        except:
            retryCount += 1
            sleepTime = 30 * retryCount
            print(f'JSON errors, sleeping for {sleepTime} seconds.')
            time.sleep(sleepTime)
            result = retrieveIPTJSON(url, retryCount = retryCount)
        return result   
    
#    def iPlantNameSearch(givenScientificName):
#        queryWordList = givenScientificName.split()
#        # dump any indications of infraspecific taxa
#        omitList = ['var.','ssp.','x']
#        query = ' '.join([x for x in queryWordList if x not in omitList])
#        queryText = query.replace(' ','%20')
#        url = 'http://www.catalogueoflife.org/annual-checklist/2017/webservice?name={}&format=json&response=full'.format(queryText)
#        
#        data = requests.get(url=url)
#        data = json.loads(data.text)
#        
#        print(data.keys)
#        nameStatus = data.get('results')[0].get('name_status')
#        if 'accepted name' not in nameStatus: # if it is not accepted it'll be organized differently...
#            acceptedName = data.get('results')[0].get('accepted_name').get('name')
#            query = acceptedName
#            queryText = query.replace(' ','%20')
#            url = 'http://www.catalogueoflife.org/annual-checklist/2017/webservice?name={}&format=json&response=full'.format(acceptedName)
#            data = requests.get(url=url)
#            data = json.loads(data.text)
#        else:
#            acceptedName = data.get('results')[0].get('name')
#        
#        print(acceptedName)
#    
    def tnrsNameAlign(sciNameString, retScore = False):
        """expects a string which represents a scientific name.
        Returns an iplant aligned name, author, iPlant confidence score.
        This is helpful to clean up simple typos.
        The returned score should be used to decide if it is an acceptable name"""
        # start tnrs api search out with a sleep, to slow repeated requests.
        time.sleep(1)
        queryName = sciNameString.replace(' ','%20')
        url = f'http://tnrs.iplantc.org/tnrsm-svc/matchNames?retrieve=best&names={queryName}'
        result = retrieveIPTJSON(url)
        sciName = result.get('acceptedName', None)
        sciAuthor = result.get('acceptedAuthor', None)
        try:
            score = float(result.get('scientificScore', 0)) # the confidence in the return
        except ValueError:
            score = 0
        result = sciName
        # if it scored poorly, or was not resolved to species
        # don't pass the results on.
        if (score < 0.7) or (len(sciName.split()) < 2): 
            result = None
        if retScore:
            result = (sciName, score, sciAuthor)
        return result
    
        return acceptedName
        
    def colNameSearch(givenScientificName):
        ''' Checks a given scientific Name for acceptance and authority, using
            Catalog of Life's API. Expects a string, with a standardized name '''
    
        identification = str(givenScientificName).split()
        if givenScientificName != '':
            identQuery = [identification[0]]
        # If there is no sci-name in row
        else:
            return 'empty_string'
        if len(identification) > 1:
            identQuery.append(identification[1])
            if len(identification) > 2:
                identQuery.append(identification[-1])
        try:
            CoLQuery = ET.parse(urllib.request.urlopen('http://webservice.catalogueoflife.org/col/webservice?name={}&response=terse'.format('+'.join(identQuery)), timeout=30)).getroot()
        # help(socket.timeout)
        except OSError:
            try:
                # This try attempt tries to load a catalog by specififying the current year
                # We may want to ask the user first, or consider removing this.
                # This tries  the current year then attempts a year prior before giving up.
                print('useing the alternative CoL URL')
                CoLQuery = ET.parse(urllib.request.urlopen('http://webservice.catalogueoflife.org/annual-checklist/{}/webservice?name={}&response=terse'.format(datetime.datetime.now().year,'+'.join(identQuery)), timeout=30)).getroot()
            # help(socket.timeout)
            except OSError:
                try:
                    CoLQuery = ET.parse(urllib.request.urlopen('http://webservice.catalogueoflife.org/annual-checklist/{}/webservice?name={}&response=terse'.format(datetime.datetime.now().year -1 ,'+'.join(identQuery)), timeout=30)).getroot()
                except HTTPError:
                    return 'http_Error'
        #<status>accepted name|ambiguous synonym|misapplied name|privisionally acceptedname|synomym</status>  List of potential name status
    
        #Check if CoL returned an Error
        if len(CoLQuery.get('error_message')) > 0:
            return ('ERROR', str(CoLQuery.get('error_message')))
        #if not an error, then pull all the results
        for result in CoLQuery.findall('result'):
        #start checking the results for the first instance of an accepted name.
            nameStatus = result.find('name_status').text
            if nameStatus == 'accepted name':
                name = result.find('name').text
                try: #Try to locate an instance in which the name is italicized (because CoL returns an HTML name with authority)
                    authorityName = result.find('name_html').find('i').tail
                except AttributeError:
                    try:
                        # Try another method to find the HTML name with authority
                        authorityName = html.unescape(result.find('name_html').text)
                        authorityName = authorityName.split('</i> ')[1]
                    except IndexError:
                        # Give up looking for authority
                        authorityName = ''
                    #cleaning the author name up.
                authorityName = re.sub(r'\d+','',str(authorityName))
                authorityName = authorityName.strip().rstrip(',')
                return (name,authorityName)
            elif 'synonym' in nameStatus:
                return colNameSearch(result.find('accepted_name/name').text)

    def genScientificName(self, currentRowArg):
        """Generate scientific name calls Catalog of Life to get
        most up-to-date scientific name for the specimen in question."""
        
        # retrieve a user pref for which database to use for taxonomy.
        # ie: iPlant should probably be first because of the % score feature.
        
        #self.prefs.get('')
        
        currentRow = currentRowArg
        sciNameColumn = self.findColumnIndex('scientificName')
        authorColumn = self.findColumnIndex('scientificNameAuthorship')
        sciNameAtRow = self.model.getValueAt(currentRow, sciNameColumn)
        sciNameList = sciNameAtRow.split(' ')
        sciNameToQuery = sciNameAtRow
        sciAuthorAtRow = str(self.model.getValueAt(currentRow, authorColumn))
        sciNameSuffix = ''
        if sciNameAtRow != '':
            exclusionWordList = ['sp.','sp','spp','spp.','ssp','ssp.','var','var.']
            #this intends to exclude only those instances where the final word is one from the exclusion list.
            if sciNameList[-1].lower() in exclusionWordList:    #If an excluded word is in scientific name then modify.
                sciNameToQuery = sciNameList
                sciNameSuffix = str(' ' + sciNameToQuery[-1])       #store excluded word incase the user only has genus and wants Sp or the like included.
                sciNameToQuery.pop()
                if len(sciNameToQuery) < 1:                     #If the name has more than 1 word after excluded word was removed then forget the excluded word.
                    return sciNameAtRow
                sciNameToQuery = ' '.join(sciNameToQuery)
            #elif ((len(sciNameList) == 4) & (sciNameList[2].lower() in exclusionWordList)): # handle infraspecific abbreviations by trusting user input.
            elif len(sciNameList) == 4:
                if sciNameList[2].lower() in exclusionWordList: # handle infraspecific abbreviations by trusting user input.
                    infraSpecificAbbreviation = sciNameList[2]
                    sciNameList.remove(infraSpecificAbbreviation)
                    sciNameToQuery = ' '.join(sciNameList)
            results = colNameSearch(sciNameToQuery)
            if isinstance(results, tuple):
                if results[0] == 'ERROR':
                    messagebox.showinfo('Name ERROR at row {}'.format(currentRow+1), 'Name Verification Error at row {}:\nWhen asked about "{}",\nCatalog of Life responded with: "{}."\nName unverified! (probably a typo)'.format(currentRow+1,sciNameAtRow,results[1]))
                    return sciNameAtRow
    
                sciName = str(results[0])
                auth = str(results[1])
                try:
                    if isinstance(infraSpecificAbbreviation, str):
                        sciName = sciName.split()
                        if len(sciName) > 2:
                            sciName.insert(-1, infraSpecificAbbreviation)
                        sciName = ' '.join(sciName)
                except NameError:
                    pass # if we fail to check infraSpecificAbbreviation, it must not exist. Probably a nicer way to do this.
    
                if sciNameAtRow != sciName:   #If scientific name needs updating, ask. Don't ask about new authority in this case.
                    if messagebox.askyesno('Scientific name at row {}'.format(currentRow+1), 'Would you like to change {} to {} and update the authority?'.format(sciNameAtRow,sciName)):
                        return (sciName, auth)
                    else:
                        return (sciNameAtRow + sciNameSuffix, sciAuthorAtRow) #if user declines the change return the old stuff.
    
                elif sciAuthorAtRow == '':  #if author is empty, update it without asking.
                    return (sciNameAtRow + sciNameSuffix, auth)
                elif sciAuthorAtRow != auth:  #If only Author needs updating, ask and keep origional scientific name (we've covered if it is wrong already)
                    if messagebox.askyesno('Authority at row {}'.format(currentRow+1), 'Would you like to update the authorship for {} from {} to {}?'.format(sciNameAtRow,sciAuthorAtRow,auth)):
                        return (sciNameAtRow + sciNameSuffix, auth)
                    else:
                        return (sciNameAtRow + sciNameSuffix, sciAuthorAtRow) #if user declines the change return the old stuff.
                else:
                    return (sciNameAtRow + sciNameSuffix, sciAuthorAtRow)
                    
            elif isinstance(results, str):
         #       if results == 'not_accepted_or_syn':
         #           messagebox.showinfo("Scientific Name Error", "No scientific name update!")
         #           return currentSciName
                if results == 'empty_string':
                    #messagebox.showinfo("Scientific name error", "Row " + str(currentRow+1) + " has no scientific name.") # 2 dialog boxes is sort of rude.
                    if messagebox.askyesno('MISSING Name at row {}'.format(currentRow+1), "Would you like to halt record processing to add a Scientific Name to row {}?".format(currentRow+1)):
                        self.setSelectedRow(currentRow)
                        self.setSelectedCol(sciNameColumn)
                        return "user_set_sciname"
                elif results == 'http_Error':
                     messagebox.showinfo('Name ERROR at row {}'.format(currentRow+1, "Catalog of Life, the webservice might be down. Try again later, if this issue persists please contact us: plantdigitizationprojectutc@gmail.com"))
        else: # Can this ever catch anything?
            if messagebox.askyesno('MISSING Name at row {}'.format(currentRow+1), "Would you like to halt record processing to add a Scientific Name to row {}?".format(currentRow+1)):
                self.setSelectedRow(currentRow)
                self.setSelectedCol(sciNameColumn)
                return "user_set_sciname"
            return sciNameAtRow
    def userNotice(self, text):
        msg = QMessageBox()
        msg.setIcon(MessageBox.Warning)
        msg.setText(text)
        #msg.setInformativeText("This is additional information")
        msg.setWindowTitle('Taxanomic alignment')
        #msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def userAsk(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(text)
        msg.setWindowTitle('Taxanomic alignment')
        msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        reply = msg.exec_()
        if reply == QMessageBox.Yes:
            return True
        elif reply == QMessageBox.No:
            return False
        else:
            return "cancel"
        
        #    def cleanSciName(self, sciNameStr):
#        """partial snipit to remove autonymns"""
#        
#        sciNameStr = str(sciNameStr).lower()
#        sciNameStr = strNormRegex.sub('', sciNameStr)  # strip out non-alpha characters
#        wordList = sciNameStr.split()
#        if len(wordList) == 3:
#        # check for autonym & reduce redunant infraspecific term.
#            if queryWordList[1] == queryWordList[2]:
#                del queryWordList[2]