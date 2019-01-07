#!/usr/bin/env python
# Author
# License
import requests

# status codes
# link -> https://developers.google.com/maps/documentation/geocoding/intro#StatusCodes
# link -> https://developers.google.com/maps/documentation/geocoding/intro#ReverseGeocoding


def reverseGeoCall(latitude, longitude):
    apiKey = 'AIzaSyCwugFdGLz6QUtcYqD1z0PKKsYJhay3vIg'
    apiUrl = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(latitude) + ',' + str(longitude) + '&key=' + apiKey
    apiCall = requests.get(apiUrl)

    status = apiCall.json()['status']
    # api returns OK (query went through, received results)
    if status == 'OK':
        results = apiCall.json()['results']
        addressComponents = results[0]['address_components']
        return addressComponents
    # some error occured
    # will be indicated by the status
    else:
        status = str(status)
        return status

def genLocalityNoAPI(self, currentRowArg):
    """ Attempts to improve the locality string using existing geography data.
    This function complains more than the inlaws."""
# both locality functions would benefit from some systemic method of determining when to add italics to binomial (scientific) names.
# such the italic tags "<i> and </i>" would need to be stripped before exporting for database submission.
    currentRow = currentRowArg
    pathColumn = self.findColumnIndex('path')
    localityColumn = self.findColumnIndex('locality')
    municipalityColumn = self.findColumnIndex('municipality')
    countyColumn = self.findColumnIndex('county')
    stateColumn = self.findColumnIndex('stateProvince')
    countryColumn = self.findColumnIndex('country')
    try:
        currentLocality = self.model.getValueAt(currentRow, localityColumn)
        #Gen list of locality value locations
        localityFields = [self.model.getValueAt(currentRow,x) for x in [countryColumn, stateColumn, countyColumn, municipalityColumn, pathColumn, localityColumn]]
        #Clean nans and empty fields out of the list
        localityFields = [x for x in localityFields if str(x) not in['','nan']]
        #combine values from each item remaining in localityFields
        newLocality = [x for x in localityFields if x.lower() not in currentLocality.lower()]
        #join the list into a single string
        newLocality = ', '.join(newLocality)
        userWarnedAboutGeo = False # set a trigger to restrict the amount of times we complain about their slack gps data.
        for geoGeographyField in [stateColumn, countyColumn]:
            if self.model.getValueAt(currentRow, geoGeographyField) in['','nan']:
                messagebox.showinfo('LIMITED Location data at row {}'.format(currentRow+1), 'Row {} is missing important geographic data!\nYou may need to manually enter data into location fields (such as State, and County).'.format(currentRow+1))
                userWarnedAboutGeo = True
                break
        if not userWarnedAboutGeo:
            if newLocality != currentLocality: # if we actually changed something give the user a heads up the methods were sub-par.
                newLocality = '{}, {}'.format(newLocality,currentLocality).rstrip(', ').lstrip(', ')
                messagebox.showinfo('LIMITED Location data at row {}'.format(currentRow+1), 'Locality at row {} was generated using limited methods'.format(currentRow+1))
            else:# if we could infer nothing from existing geographic fields, AND we have no GPS values then they have work to do!
                messagebox.showinfo('LIMITED Location data at row {}'.format(currentRow+1), 'Row {} is missing important geographic data!\nYou may need to manually enter data into location fields (such as State, and County).'.format(currentRow+1))
                return newLocality
        return newLocality

    except ValueError:
        #if some lookup fails, toss value error and return empty
        messagebox.showinfo('Location ERROR at row {}'.format(currentRow+1), "Offline Locality generation requires atleast a column named locality.")
        return

def genLocality(self, currentRowArg):
    """ Generate locality fields, uses API call to get
    country, state, city, etc. from GPS coordinates."""
# both locality functions would benefit from some systemic methid of determining when to add italics to binomial (scientific) names.
# such the italic tags "<i> and </i>" would need to be stripped before exporting for database submission.

    currentRow = currentRowArg
    pathColumn = self.findColumnIndex('path')
    localityColumn = self.findColumnIndex('locality')
    municipalityColumn = self.findColumnIndex('municipality')
    countyColumn = self.findColumnIndex('county')
    stateColumn = self.findColumnIndex('stateProvince')
    countryColumn = self.findColumnIndex('country')
    latitudeColumn = self.findColumnIndex('decimalLatitude')
    longitudeColumn = self.findColumnIndex('decimalLongitude')
    coordUncertaintyColumn = self.findColumnIndex('coordinateUncertaintyInMeters')
    
    if localityColumn != '':
        currentLocality = self.model.getValueAt(currentRow, localityColumn)
        try:
            latitude = (self.model.getValueAt(currentRow, latitudeColumn))
            longitude = (self.model.getValueAt(currentRow, longitudeColumn))
            if latitude == '' or longitude == '':
                raise ValueError("Latitude/Longitude have no values")
        except ValueError:
            if messagebox.askyesno('MISSING GPS at row {}'.format(currentRow+1), 'Would you like to halt record processing to add GPS coordinates for row {}?'.format(currentRow+1)):
                self.setSelectedRow(currentRow)
                self.setSelectedCol(latitudeColumn)
                return "user_set_gps"
            else:
                return "loc_error_no_gps"
        address = reverseGeoCall(latitude, longitude)
        if isinstance(address, list):
            newLocality = []
            for addressComponent in address:
                if addressComponent['types'][0] == 'route':
                    # path could be Unamed Road
                    # probably don't want this as a result?
                    
                    #Testing the idea of excluding the "path" if the coord uncertainty is over a threshold.
                    #the threshold of 200 meters was chosen arbitrarily and should be reviewed.
                    coordUncertainty = (self.model.getValueAt(currentRow, coordUncertaintyColumn))
                    try:
                        coordUncertainty = int(coordUncertainty)
                        if coordUncertainty < 200:
                            path = 'near {}'.format(addressComponent['long_name'])
                            newLocality.append(path)
                            self.model.setValueAt(path, currentRow, pathColumn)
                    except ValueError:
                        pass
                if addressComponent['types'][0] == 'administrative_area_level_1':
                    stateProvince = addressComponent['long_name']
                    newLocality.append(stateProvince)
                    self.model.setValueAt(stateProvince, currentRow, stateColumn)
                if addressComponent['types'][0] == 'administrative_area_level_2':
                    county = addressComponent['long_name']
                    newLocality.append(county)
                    self.model.setValueAt(county, currentRow, countyColumn)
                if addressComponent['types'][0] == 'locality':
                    municipality = addressComponent['long_name']
                    newLocality.append(municipality)
                    self.model.setValueAt(municipality, currentRow, municipalityColumn)
                if addressComponent['types'][0] == 'country':
                    country = addressComponent['short_name']
                    newLocality.append(country)
                    self.model.setValueAt(country, currentRow, countryColumn)
            newLocality = ', '.join(newLocality[::-1]) # build it in reverse order because the list is oddly being built incorrectly.
            if newLocality not in currentLocality:
                newLocality = newLocality + ', ' + currentLocality
                newLocality = newLocality.rstrip() #clean up the string
                if newLocality.endswith(','):   #if it ends with a comma, strip the final one out.
                    newLocality = newLocality.rstrip(',').lstrip(', ')
                return newLocality
            else:
                return currentLocality
        # Google API call returned error/status string
        else:
            apiErrorMessage = address
            messagebox.showinfo('MISSING GPS at row {}'.format(currentRow+1), 'Location lookup error at row {}:\nGoogle reverse Geolocate service responded with: "{}"/nThis may be internet connection problems, or invalid GPS values.'.format(currentRow+1,str(apiErrorMessage)))
#Commenting out for now, not sure we want people clicking yes retry repeatedly
#                if messagebox.askyesno("Locality Error", "This function requires an internet connection, would you like to retry?"):
#                    self.genLocality(currentRow)
#                else:
#                    return "loc_apierr_no_retry"
            return "loc_apierr_no_retry"
    else:
        messagebox.showinfo('Location ERROR at row {}'.format(currentRow+1), "Locality generation requires GPS coordinates, and a column named locality.")
        return
    return