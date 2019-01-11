#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 10:33:55 2019

@authors: Caleb Powell, Jacob Motley

"""

import requests
from PyQt5.QtWidgets import QMessageBox

# status codes
# link -> https://developers.google.com/maps/documentation/geocoding/intro#StatusCodes
# link -> https://developers.google.com/maps/documentation/geocoding/intro#ReverseGeocoding

class locality():
    def __init__(self, parent=None, editable = True, *args):
        super(locality, self).__init__()
        
        self.parent = parent
        
        with open('key.txt', 'r') as keyRing:
            gAPIkey=keyRing.read()
        self.gAPIkey = gAPIkey

    def userNotice(self, text):
        msg = QMessageBox()
        msg.setIcon(MessageBox.Warning)
        msg.setText(text)
        #msg.setInformativeText("This is additional information")
        msg.setWindowTitle('GeoLocation')
        #msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def userAsk(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(text)
        msg.setWindowTitle('GeoLocation')
        msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        reply = msg.exec_()
        if reply == QMessageBox.Yes:
            return True
        elif reply == QMessageBox.No:
            return False
        else:
            return "cancel"

    def reverseGeoCall(self, latitude, longitude):
        apiUrl = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={str(latitude)},{str(longitude)}&key={self.gAPIkey}'
        apiCall = requests.get(apiUrl)
        status = apiCall.json()['status']
        # api returns OK (query went through, received results)
        if status == 'OK':
            results = apiCall.json()['results']
            addressComponents = results[0]['address_components']
            return addressComponents
        else:  # some error occured
            status = str(status)
            return status

   
    def genLocality(self, currentRowArg):
        """ Generate locality fields, uses API call to get
        country, state, city, etc. from GPS coordinates."""
    # both locality functions would benefit from some systemic methid of determining when to add italics to binomial (scientific) names.
    # such the italic tags "<i> and </i>" would need to be stripped before exporting for database submission.
        
        currentRow = f"{currentRowArg['site#']}-{currentRowArg['specimen#']}"
        currentLocality = currentRowArg['locality']
        latitude = currentRowArg['decimalLatitude']
        longitude = currentRowArg['decimalLongitude']
        if latitude == '' or longitude == '':
            message = f'MISSING GPS at row {currentRow}. Would you like to halt record processing to add GPS coordinates for row {currentRow}?'
            answer = self.userAsk(message)
            if answer:
                self.parent.selectTreeWidgetItemByName(currentRow)
                raise Exception
            else:
                return currentRowArg
        
        address = self.reverseGeoCall(latitude, longitude)
        if isinstance(address, list):
            newLocality = []
            for addressComponent in address:
                if addressComponent['types'][0] == 'route':
                    # path could be Unamed Road
                    # probably don't want this as a result?

                    #TODO include a path inclusison uncertainty threshold
                    coordUncertainty = currentRowArg['coordinateUncertaintyInMeters']
                    try:
                        coordUncertainty = int(coordUncertainty)
                        if coordUncertainty < 200:
                            path = f"near {addressComponent['long_name']}"
                            newLocality.append(path)
                            currentRowArg['path'] = path
                    except ValueError:
                        pass
                if addressComponent['types'][0] == 'administrative_area_level_1':
                    stateProvince = addressComponent['long_name']
                    newLocality.append(stateProvince)
                    currentRowArg['stateProvince'] = stateProvince
                if addressComponent['types'][0] == 'administrative_area_level_2':
                    county = addressComponent['long_name']
                    newLocality.append(county)
                    currentRowArg['county'] = county
                if addressComponent['types'][0] == 'locality':
                    municipality = addressComponent['long_name']
                    newLocality.append(municipality)
                    currentRowArg['municipality'] = municipality
                if addressComponent['types'][0] == 'country':
                    country = addressComponent['short_name']
                    newLocality.append(country)
                    currentRowArg['country'] = country
            newLocality = ', '.join(newLocality[::-1]) # build it in reverse order
            if newLocality not in currentLocality:
                #TODO make a user preference setting for prepending the generated substring to existing data.
                newLocality = newLocality + ', ' + currentLocality
                newLocality = newLocality.rstrip() #clean up the string
                if newLocality.endswith(','):   #if it ends with a comma, strip the final one out.
                    newLocality = newLocality.rstrip(',').lstrip(', ')
                currentRowArg['locality'] = newLocality
       
        else:   # if the Google API call returned error/status string
            apiErrorMessage = address
            message = f'MISSING GPS at row {currentRow+1}. Location lookup error at row {currentRow+1}: Google reverse Geolocate service responded with: "{str(apiErrorMessage)}". This may be internet connection problems, or invalid GPS values.'
            self.userNotice( message )
            # could consider a retry option here
            raise Exception

        return currentRowArg


#    def genLocalityNoAPI(self, currentRowArg):
#        """ Attempts to improve the locality string using existing geography data.
#        This function complains more than the inlaws."""
#    # both locality functions would benefit from some systemic method of determining when to add italics to binomial (scientific) names.
#    # such the italic tags "<i> and </i>" would need to be stripped before exporting for database submission.
#        
#        currentRow = f"{currentRowArg['site#']}-{currentRowArg['specimen#']}"
#        currentLocality = currentRowArg['locality']
#        latitude = currentRowArg['decimalLatitude']
#        longitude = currentRowArg['decimalLongitude']
#        stateProvince = currentRowArg['stateProvince']
#        county = currentRowArg['county']
#        municipality = currentRowArg['municipality']
#        country = currentRowArg['country']
#        
#        try:
#            currentLocality = self.model.getValueAt(currentRow, localityColumn)
#            localityFields = [x for x in [country, stateProvince, county, municipality, path, locality] if str(x) not in['','nan']]
#            #combine values from each item remaining in localityFields
#            newLocality = [x for x in localityFields if x.lower() not in currentLocality.lower()]
#            #join the list into a single string
#            newLocality = ', '.join(newLocality)
#            userWarnedAboutGeo = False # set a trigger to restrict the amount of times we complain about their slack gps data.
#            for geoGeographyField in [stateColumn, countyColumn]:
#                if self.model.getValueAt(currentRow, geoGeographyField) in['','nan']:
#                    message = f'Row {currentRow+1} is missing important geographic data!\nYou may need to manually enter data into location fields (such as State, and County).'
#                    self.userNotice(message)
#                    userWarnedAboutGeo = True
#                    break
#            if not userWarnedAboutGeo:
#                if newLocality != currentLocality: # if we actually changed something give the user a heads up the methods were sub-par.
#                    newLocality = '{}, {}'.format(newLocality,currentLocality).rstrip(', ').lstrip(', ')
#                    message = f'Locality at row {currentRow+1} was generated using limited methods'
#                    self.userNotice(message)
#                else:# if we could infer nothing from existing geographic fields, AND we have no GPS values then they have work to do!
#                    message = f'Row {currentRow+1} is missing important geographic data!\nYou may need to manually enter data into location fields (such as State, and County).'
#                    self.userNotice(message)
#                    return newLocality
#            return newLocality
#    
#        except ValueError:
#            #if some lookup fails, toss value error and return empty
#            message = f'Offline Locality generation requires atleast a column named locality. None found at row {currentRow+1}'
#            self.userNotice(message)
#            return