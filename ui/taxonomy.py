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

import datetime
import time
import requests
import json



class taxonomicVerification():
    def __init__(self, settings, parent, editable = True, *args):
        super(taxonomicVerification, self).__init__()
        self.parent = parent
        self.settings = settings       
        # precompile regex cleaning string to save time.
        self.strNormRegex = re.compile('[^a-z ]')
    
    def readTaxonomicSettings(self):
        """ Fetches the most up-to-date taxonomy relevant settings"""
        # TODO check if this is redundant, shouldn't the settings window "Save and exit" button establish these changes?
        # meaning, whenever this was called the function could just go straight to the settings module and use it?
        # additionally, this may be reloading the local alignments excessively
        # The function is called in pandastablemodel (at least)
        #which service to utalize to make alignments
        self.TaxAlignSource = self.settings.get('value_TaxAlignSource')
        # how to handle name reccomendations
        self.NameChangePolicy = self.settings.get('value_NameChangePolicy')
        # how to handle authority reccomendations
        self.AuthChangePolicy = self.settings.get('value_AuthChangePolicy')
        # tnrs score threshold
        self.value_TNRS_Threshold = self.settings.get('value_TNRS_Threshold')
        # which kingdom we're interested in
        current_value_Kingdom = self.settings.get('value_Kingdom')
        try:  # see if it's necessary to reload the local_Reference
            if self.value_Kingdom != current_value_Kingdom:
                raise AttributeError # force exception and boolean into same outcome
        except AttributeError:  # load the local reference
            self.value_Kingdom = current_value_Kingdom
            if '(local)' in self.TaxAlignSource:       
                from io import StringIO
                stream = QFile(f':/rc_/{self.value_Kingdom}_Reference.csv')
                if stream.open(QFile.ReadOnly):
                    df = StringIO(str(stream.readAll(), 'utf-8'))
                    stream.close()
                self.local_Reference = pd.read_csv(df, encoding = 'utf-8', dtype = 'str')

    def retrieveAlignment(self, querySciName, retrieveAuth=False):
        """ parses the settings for the proper alignment policy. 
        Returns tuple of aligned name and aligned authority.
        Can optionally be used to retrieve the authority of a potentially 
        unaccepted taxon. """
        if self.TaxAlignSource == 'Catalog of Life (web API)':
            result = self.getCOLWeb(querySciName, retrieveAuth)
        elif self.TaxAlignSource == 'ITIS (local)':
            result = self.getITISLocal(querySciName, retrieveAuth)
        elif self.TaxAlignSource == 'ITIS (web API)':
            result = self.getITISWeb(querySciName, retrieveAuth)
        elif self.TaxAlignSource == 'Taxonomic Name Resolution Service (web API)':
            result = self.getTNRS(querySciName, retrieveAuth)
        elif self.TaxAlignSource == 'MycoBank (local)':
            result = self.getMycoBankLocal(querySciName, retrieveAuth)
        elif self.TaxAlignSource == 'MycoBank (web API)':
            result = self.getMycoBankWeb(querySciName, retrieveAuth)
        else:
            result = (None, None)

        if retrieveAuth:
            result = result[-1]
        return result

    def verifyTaxonomy(self, rowData):
        """general method to align taxonomy and retrieve authority.
        accepts a df row argument, treats it as a dictionary and makes
        refinements. Returning a the modified argument."""

        if rowData['scientificName'] in ['', None]:
            return rowData
        rowNum = f"{rowData['siteNumber']}-{rowData['specimenNumber']}"
        scientificName = rowData['scientificName']
        scientificNameAuthorship = rowData['scientificNameAuthorship'].strip()
        querySciName = self.normalizeStrInput(scientificName)
        result = self.retrieveAlignment(querySciName)
        resultSciName, resultAuthor = result
        # Decide how to handle resulting data
        keptResult = False  # flag to det if the alignment result was kept
        changeAuth = False  # flag to determine if the authority needs altered.
        if result[0] is None:  # if no scientificName was returned
            message = f'No {self.value_Kingdom} results for "{scientificName}" (# {rowNum}) found using {self.TaxAlignSource}.\n This may be a typo, would you like to reenter the name?'
            reply = self.parent.userSciNameInput(f'{rowNum}: Taxonomic alignment', message)
            if reply:
                rowData['scientificName'] = reply
                rowData = self.verifyTaxonomy(rowData)
            #self.parent.userNotice(message, 'Taxonomic alignment')
            return rowData
        if resultSciName not in scientificName:
            if self.NameChangePolicy == 'Accept all suggestions':
                rowData['scientificName'] = resultSciName
                changeAuth = True
                keptResult = True
            elif self.NameChangePolicy == 'Always ask':
                 message = f'Change {scientificName} to {resultSciName} at record {rowNum}?'
                 answer = self.parent.userAsk(message, 'Taxonomic alignment')
                 if answer:
                     rowData['scientificName'] = resultSciName
                     keptResult = True
                     changeAuth = True

        if changeAuth:
            # if the scientificName changed already, update the author
            rowData['scientificNameAuthorship'] = resultAuthor
        else:
            if not keptResult:
                # condition where we need to get authority for potentially non-accepted name
                resultAuthor = self.retrieveAlignment(querySciName, retrieveAuth=True)
            if resultAuthor not in [scientificNameAuthorship, None]:
                # if the authors don't match check user policies
                # conditional actions based on AuthChangePolicy
                if self.AuthChangePolicy == 'Accept all suggestions':
                    rowData['scientificNameAuthorship'] = resultAuthor
    
                elif self.AuthChangePolicy == 'Fill blanks':
                    if scientificNameAuthorship == '':  # if it is blank fill it
                        rowData['scientificNameAuthorship'] = resultAuthor
                    else:  # if not blank, ask.
                        message = f'Update author of {rowData["scientificName"]} from:\n{scientificNameAuthorship} to {resultAuthor} at record {rowNum}?'
                        answer = self.parent.userAsk(message, 'Authority alignment')
                        if answer:
                            rowData['scientificNameAuthorship'] = resultAuthor
    
                elif self.AuthChangePolicy == 'Always ask':
                    if scientificNameAuthorship == '':  # custom dialog box if the field was empty. 'Always ask' may be annoying!
                        message = f'Fill in blank author of {rowData["scientificName"]} to {resultAuthor} at record {rowNum}?'
                    else:
                        message = f'Update author of {rowData["scientificName"]} from:\n{scientificNameAuthorship} to {resultAuthor} at record {rowNum}?'
                    answer = self.parent.userAsk(message, 'Authority alignment')
                    if answer:
                        rowData['scientificNameAuthorship'] = resultAuthor
        return rowData
        
    def normalizeStrInput(self, inputStr, retrieveAuth=False):
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

    def getITISLocal(self, inputStr, retrieveAuth=False):
        """ uses local itis reference csv to attempt alignments """
        df = self.local_Reference
        result = (None, None)
        
        if retrieveAuth:
            acceptedRow = df[df['normalized_name'] == inputStr]
        else:
            try:
                tsn_accepted = df[df['normalized_name'] == inputStr]['tsn_accepted'].mode()[0]
            except IndexError:
                return result
            acceptedRow = df[df['tsn'] == tsn_accepted]
            
        if len(acceptedRow) > 0:
            try:
                acceptedName = acceptedRow['complete_name'].mode()[0]
            except IndexError:
                acceptedName = inputStr
            try:
                acceptedAuthor = acceptedRow['taxon_author_id'].mode()[0]
            except IndexError:
                acceptedAuthor = ""
            result = (acceptedName, acceptedAuthor)
        return result

    def getITISWeb(self, inputStr, retrieveAuth=False):
        """ https://www.itis.gov/ws_description.html """
        print('go get ITIS data')
        
    def getMycoBankLocal(self, inputStr, retrieveAuth=False):
        """ uses local reference csv to attempt alignments """
        df = self.local_Reference
        result = (None, None)
        
        if retrieveAuth:
            acceptedRow = df[df['normalized_name'] == inputStr]
        else:
            try:
                acceptedName = df[df['normalized_name'] == inputStr]['Accepted_name'].mode()[0]
            except IndexError:
                return result
            acceptedRow = df[df['Accepted_name'] == acceptedName]
        if len(acceptedRow) > 0:
            try:
                acceptedName = acceptedRow['Accepted_name'].mode()[0]
            except IndexError:
                acceptedName = inputStr
            try:
                acceptedAuthor = acceptedRow['Authors'].mode()[0]
            except IndexError:
                acceptedAuthor = ""
            result = (acceptedName, acceptedAuthor)
        return result

    def getMycoBankWeb(self, inputStr, retrieveAuth=False):
        """http://www.mycobank.org/Services/Generic/Help.aspx?s=searchservice"""
        print('go get mycobank data')

    def getCOLWeb(self, inputStr, retrieveAuth=False):
        """ uses Catalog of life reference to attempt alignments """
        
        result = (None, None)
        # a list of urls for col, starting with most recent and then specifying current year, then current year -1
        urlInputStr = inputStr.replace(' ','%20')
        urlList = [f'http://webservice.catalogueoflife.org/col/webservice?name={urlInputStr}&format=json&response=full',
                   f'http://webservice.catalogueoflife.org/annual-checklist/{datetime.datetime.now().year}/webservice?name={urlInputStr}&format=json&response=full',
                   f'http://webservice.catalogueoflife.org/annual-checklist/{datetime.datetime.now().year - 1 }/webservice?name={urlInputStr}&format=json&response=full']

        for url in urlList:
            response = requests.get(url, timeout = 3)
            time.sleep(1)  # use a sleep to be polite to the service
            if response.status_code == requests.codes.ok:
                # returns a list of "results" each result is a seperate dict
                data = response.json().get('results')
                # list comprehension to navigate the json
                if retrieveAuth:
                    resultName = data[0].get('name')
                    resultAuth = data[0].get('author')
                    result = (resultName, resultAuth)
                    return result
                else:
                    try:
                        data = [x for x in data if 
                                (x.get('name_status','') == 'accepted name') and 
                                (x.get('classification')[0].get('name','') == self.value_Kingdom)][0]
                        acceptedName = data.get('name')
                        acceptedAuthor = data.get('name_html').split('</i> ')[1].strip()
                        result = (acceptedName, acceptedAuthor)
                        return result
                    except:
                        pass
        return result

    def getTNRS(self, inputStr, retrieveAuth=False):
        """ uses the Taxonomic Name Resolution Service API 
        hosted through iPlant."""

        result = (None, None)
        score = 0
        urlInputStr = inputStr.replace(' ','%20')
        # TODO add an optional dialog box with a list of the top returned results. Allow user to pick from list.
        #url = f'http://tnrs.iplantc.org/tnrsm-svc/matchNames?retrieve=all&names={urlInputStr}'
        url = f'http://tnrs.iplantc.org/tnrsm-svc/matchNames?retrieve=best&names={urlInputStr}'
        response = requests.get(url, timeout = 3)
        if response.status_code == requests.codes.ok:
            data = response.json().get('items', None)[0]
            time.sleep(1)  # use a sleep to be polite to the service
            
            try:
                if retrieveAuth:
                    acceptedName = data.get('nameScientific', None)
                    acceptedAuthor = data.get('authorAttributed', None)
                else:
                    acceptedName = data.get('acceptedName', None)
                    acceptedAuthor = data.get('acceptedAuthor', None)
                score = float(data.get('scientificScore', 0)) # the confidence in the return
            except Exception as e:
                print(e)
                pass
            if score >= float(self.value_TNRS_Threshold)/100:
                result = (acceptedName, acceptedAuthor)
                
        return result

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