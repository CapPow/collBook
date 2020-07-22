#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 10:33:55 2019

@authors: Caleb Powell, Jacob Motley

"""

import requests
from requests import ConnectionError
from PyQt5.QtWidgets import QMessageBox
import time

import numpy as np
from math import radians, cos, sin, asin, sqrt, atan2, degrees

# status codes
# link -> https://developers.google.com/maps/documentation/geocoding/intro#StatusCodes
# link -> https://developers.google.com/maps/documentation/geocoding/intro#ReverseGeocoding

class locality():
    def __init__(self, parent, google_API_key, editable = True, *args):
        super(locality, self).__init__()
        
        self.parent = parent
        # the google key saved in apiKeys.py
        self.gAPIkey = google_API_key

    def userNotice(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
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
        try:
            apiCall = requests.get(apiUrl)
        except ConnectionError:
            return False
        status = apiCall.json()['status']
        # api returns OK (query went through, received results)
        if status == 'OK':
            results = apiCall.json()['results']
            #addressComponents = results[0]['address_components']
            addressComponents = [x['address_components'] for x in results]
            return addressComponents
        else:  # some error occured
            status = str(status)
            return status

    def genLocality(self, currentRowArg):
        """ Generate locality fields, uses API call to get
        country, state, city, etc. from GPS coordinates."""
        # both locality functions would benefit from some systemic methid of determining when to add italics to binomial (scientific) names.
        # such the italic tags "<i> and </i>" would need to be stripped before exporting for database submission.
        currentRow = f"{currentRowArg['siteNumber']}-{currentRowArg['specimenNumber']}"
        currentSiteName = f"Site {currentRowArg['siteNumber']}"
        currentLocality = currentRowArg['locality']
        latitude = currentRowArg['decimalLatitude']
        longitude = currentRowArg['decimalLongitude']
        if latitude == '' or longitude == '':
            message = f'MISSING GPS at {currentSiteName}. Would you like to halt the process to add GPS coordinates to {currentSiteName}?'
            answer = self.parent.userAsk(message, title='GeoLocation')
            if answer:
                self.parent.statusBar.pushButton_Cancel.status = True
                self.parent.selectTreeWidgetItemByName(currentSiteName)
                return currentRowArg
            else:
                return currentRowArg
        addresses = self.reverseGeoCall(latitude, longitude)
        if isinstance(addresses, list):
            
            address = addresses[0]  # Prefer the first entry
            # dig into deeper entries for a "park" type\
            addressComponents = [y for x in addresses for y in x]
            park = False
            for component in addressComponents:
                types = component['types']
                if 'park' in types:
                    address.append(component) # if park found, add to components.
            newLocality = {}

            coordUncertainty = currentRowArg['coordinateUncertaintyInMeters']
            try:
                coordUncertainty = float(coordUncertainty)
                if coordUncertainty < 50:
                    npBearing, npDist, npName = self.getNearestPlace(latitude, longitude)
                    #Given an error, npDist should == 100000
                    if npDist < 5000: # keep bearings to ~5km
                        nearest_str = f"{int(round(npDist, 0))}m bearing {round(npBearing)}° from {npName}"
                        newLocality['path'] = nearest_str
                        currentRowArg['path'] = nearest_str
            except:
                pass

            for addressComponent in address:
                if addressComponent['types'][0] == 'route':
                    try:
                        route_name = addressComponent.get('long_name', False)
                        # filter out any unnamed routes
                        if "unnamed" in route_name.lower():
                            route_name = False
                        if coordUncertainty < 50 and route_name:
                            path = f"near {addressComponent['long_name']}"
                            #check if a bearing was already derived
                            existing_path = newLocality.get('path', False)
                            if existing_path:
                                path = f"{existing_path}, {path}"
                            newLocality['path'] = path
                            currentRowArg['path'] = path
                    except:
                        pass
                #  TODO consider also using google's "natural_feature" type.
                if 'park' in addressComponent['types']:
                    parkName = addressComponent['short_name']
                    newLocality['park'] = parkName
                if addressComponent['types'][0] == 'administrative_area_level_1':
                    stateProvince = addressComponent['long_name']
                    newLocality['stateProvince'] = stateProvince
                    currentRowArg['stateProvince'] = stateProvince
                if addressComponent['types'][0] == 'administrative_area_level_2':
                    county = addressComponent['long_name']
                    newLocality['county'] = county
                    currentRowArg['county'] = county
                if addressComponent['types'][0] == 'locality':
                    municipality = addressComponent['long_name']
                    newLocality['municipality'] = municipality
                    currentRowArg['municipality'] = municipality
                if addressComponent['types'][0] == 'country':
                    country = addressComponent['short_name']
                    newLocality['country'] = country
                    currentRowArg['country'] = country
            # construct the locality items with a controlled order        
            localityList = ['country','stateProvince','county','municipality','park','path']
            localityItemList = []
            for item in localityList:
                newLocalityItem = newLocality.get(item, False)
                if newLocalityItem:
                    localityItemList.append(newLocalityItem)
            newLocality = ', '.join(localityItemList)
            if newLocality not in currentLocality:
                #TODO make a user preference setting for prepending the generated substring to existing data.
                newLocality = newLocality + ', ' + currentLocality
                newLocality = newLocality.rstrip() #clean up the string
                if newLocality.endswith(','):   #if it ends with a comma, strip the final one out.
                    newLocality = newLocality.rstrip(',').lstrip(', ')
                currentRowArg['locality'] = newLocality
       
        else:   # if the Google API call returned error/status string
            apiErrorMessage = addresses
            if apiErrorMessage == "ZERO_RESULTS":
                message = f'Location lookup error at {currentSiteName}: service responded with: "{apiErrorMessage}". Does this location exist?'
                self.parent.userNotice(message, title='GeoLocation')
            else:
                message = f'Location lookup error at {currentSiteName}: service responded with: "{apiErrorMessage}". This may be an internet connection issue.'
                notice = self.parent.userNotice(message, title='GeoLocation', retry = True)
                if notice == QMessageBox.Retry:  # if clicked retry, do it.
                    time.sleep(1)
                    currentRowArg = self.genLocality(currentRowArg)
        return currentRowArg

    # Temporary hardcoded list of acceptablePlaces
    acceptablePlaces = ['airport', 'bank', 'bus_station',
                        'campground', 'cemetery', 'church',
                        'city_hall', 'courthouse', 'embassy',
                        'fire_station', 'hindu_temple', 'hospital',
                        'library', 'light_rail_station',
                        'local_government_office', 'mosque', 'museum',
                        'park', 'place_of_worship', 'police',
                        'post_office', 'primary_school', 'school',
                        'secondary_school', 'stadium', 'subway_station',
                        'synagogue', 'tourist_attraction', 'train_station',
                        'transit_station', 'university', 'zoo']

    def getNearestPlace(self,lat,lon):
        """
        Retrieves the bearing and distance of the nearest "google place" to a point
        """
        # results will be bearing, distance(m), location name
        results = (None, 100000, None)
        apiUrl = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={str(lat)},{str(lon)}&rankby=distance&fields=name,types,geometry/location&key={self.gAPIkey}'
        try:
            apiCall = requests.get(apiUrl)
        except ConnectionError:
            return False
        status = apiCall.json()['status']
        # api returns OK (query went through, received results)
        if status == 'OK':
            nearestPlaces = apiCall.json()['results']
            qualifiedPlaces = [x for x in nearestPlaces if any(y in self.acceptablePlaces for y in x['types'])]
            nearestPlace = qualifiedPlaces[0]
            nearestPlaceLocation = nearestPlace['geometry']['location']
            npName = nearestPlace['name']
            npPlaceTypes = nearestPlace['types']
            # organize locations as lon, lat for bearing and haversine calls
            loc1 = (float(nearestPlaceLocation['lng']), float(nearestPlaceLocation['lat']))
            loc2 = (float(lon), float(lat))
            npBearing = self.bearing(loc1, loc2)
            npDist = self.haversine(*loc1, *loc2)

            results = (npBearing, npDist, npName)
        else:  # some error occured
            status = str(status)

        return results
            
    def haversine(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        see: https://stackoverflow.com/questions/29545704/fast-haversine-approximation-python-pandas
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = (np.sin(dlat/2)**2 
             + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2)
        c = 2 * np.arcsin(np.sqrt(a)) 
        km = 6367 * c
        m = km * 1000
        return m

    def bearing(self, point1, point2):
        '''
            Calculating initial bearing between two points
            (see http://www.movable-type.co.uk/scripts/latlong.html)
        '''
        lon1, lat1 = (radians(coord) for coord in point1)
        lon2, lat2 = (radians(coord) for coord in point2)

        dlat = (lat2 - lat1)
        dlon = (lon2 - lon1)
        numerator = sin(dlon) * cos(lat2)
        denominator = (
            cos(lat1) * sin(lat2) -
            (sin(lat1) * cos(lat2) * cos(dlon))
        )

        theta = atan2(numerator, denominator)
        theta_deg = (degrees(theta) + 360) % 360
        return theta_deg

#    def genLocalityNoAPI(self, currentRowArg):
#        """ Attempts to improve the locality string using existing geography data.
#        This function complains more than the inlaws."""
#    # both locality functions would benefit from some systemic method of determining when to add italics to binomial (scientific) names.
#    # such the italic tags "<i> and </i>" would need to be stripped before exporting for database submission.
#        
#        currentRow = f"{currentRowArg['siteNumber']}-{currentRowArg['specimenNumber']}"
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
