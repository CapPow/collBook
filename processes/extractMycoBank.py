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
r = requests.get('http://www.mycobank.org/localfiles/MBList.zip')
# extract it in memory to a dataFrame
z = zipfile.ZipFile(io.BytesIO(r.content))
buf = io.BytesIO(z.open("Export.xlsx").read())
df = pd.read_excel(buf, na_values= '-')[['Taxon_name','Authors','Current name.Taxon_name']]
#dfa = df.copy(deep = True)

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
df['normalized_name'] = df['Taxon_name'].transform(normalizeStrInput)
df.fillna('', inplace = True)
df.rename(columns = {'Current name.Taxon_name':'Accepted_name'}, inplace= True)
df.to_csv('Fungi_Reference.csv', encoding = 'utf8', index = False)