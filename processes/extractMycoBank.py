#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 11 10:33:55 2019

@authors: Caleb Powell

Source of material: http://www.mycobank.org/

"""

import requests
import zipfile
import io
import pandas as pd
import numpy as np
import re

# retrieve the most recent mycobank dump
#r = requests.get('http://www.mycobank.org/localfiles/MBList.zip')
# extract it in memory to a dataFrame
#z = zipfile.ZipFile(io.BytesIO(r.content))
#buf = io.BytesIO(z.open("Export.xlsx").read())
#df = pd.read_excel(buf, na_values= '-')[['Taxon_name','Authors','Current name.Taxon_name', 'Classification']]
#dfa = df.copy(deep = True)
df = pd.read_excel("Export.xlsx", na_values= '-')[['Taxon_name','Authors','Current name.Taxon_name', 'Classification',
                  'Name_status','Rank.Rank_name', 'Year_of_effective_publication']]

def extractFamily(rowData):

    classifications = rowData['Classification'].split(", ")
    if len(classifications) < 4:
        # not likely a family is among the 3
        rowData['family'] = ""
        return rowData
    # cut off first 3 classifcations and reverse the list
    # iterate through classifications looking for a legit "fam." rank
    classifications = classifications[:2:-1]
    for c in classifications:
        parentName = c.strip()
        print(parentName)
        try:
            parentRank = df[(df['Taxon_name'] == parentName) & 
                            (df['Name_status'] == 'Legitimate')]['Rank.Rank_name'].values[0]
            if parentRank == "fam.":
                familyName = strCleaningRegex.sub('', parentName)
                rowData['family'] = familyName
                return rowData
        except IndexError:
            return rowData
    # Just in case everything else somehow misses
    return rowData

def normalizeStrInput(inputStr):
    """ returns a normalized a scientificName based on string input.
    is used to prepare queries """
    # Strip non-alpha characters
    toCleanString = strCleaningRegex.sub('', inputStr)
    # Strip additional whitespace from ends
    toCleanString = toCleanString.lower().strip()
    wordList = toCleanString.split()
    if len(wordList) > 2:
        omitList = ['var', 'ssp', 'subsp', 'x', 'f']
        toCleanString = ' '.join([x for x in wordList if x not in omitList])
    outputStr = toCleanString

    return outputStr

strCleaningRegex = re.compile('[^a-zA-Z ]')
df.fillna('', inplace = True)
df['normalized_name'] = df['Taxon_name'].transform(normalizeStrInput)
df = df.apply(extractFamily, axis=1)
df.rename(columns = {'Current name.Taxon_name':'Accepted_name'}, inplace= True)
df = df[['Accepted_name', 'normalized_name', 'Authors', 'family', 'Year_of_effective_publication']]

# sort by publication year most recent at the top
df[df['Year_of_effective_publication'] == "?"]['Year_of_effective_publication'] = 0
df.sort_values(by=['Year_of_effective_publication'], ascending=False, inplace=True)
df.to_csv('Fungi_Reference.csv', encoding = 'utf8', index = False)







