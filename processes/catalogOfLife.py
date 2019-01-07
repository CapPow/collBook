#!/usr/bin/env python
# Author
# License

import urllib.request
from urllib.error import HTTPError
import re
import xml.etree.ElementTree as ET
import html
import sys
import datetime
try:
    from tkinter import messagebox
except:
    import tkMessageBox as messagebox


# catalog of life scientific name search
# queries catalog of life with a scientific name
# returns the most up-to-date, accepted, scientific name for a specimen
# or an error message to calling function
def colNameSearch(givenScientificName):
    identification = str(givenScientificName).split()
    if givenScientificName != '':
        identQuery = [identification[0]]
    # no sci-name in row
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