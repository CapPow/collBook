#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 18:28:30 2019

@author: Caleb Powell

Created to extract and simplify data from a SQL db provided by ITIS for use
as a local taxanomic alignment reference.

"""
import pandas as pd
import sqlite3
import re
# This block only necessary to generate the itis_Taxonomy_Reference.csv
# dumps itis sql db to csvs

def ITIS_To_csv(sqlLocStr):
    """ accepts a strin gwith the sql db location and breaks them out into csv files """
    #db = sqlite3.connect('../projectSupport/orig_results_county_Dist-master/itisSqlite102918/ITIS.sqlite')
    db = sqlite3.connect(sqlLocStr)
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    # only interested in a few tables from these data
    tablesOfInterest = ['taxonomic_units','synonym_links','taxon_authors_lkp']
    for table_name in tables:
        if table_name in tablesOfInterest:
            table_name = table_name[0]
            table = pd.read_sql_query("SELECT * from %s" % table_name, db)
            table.to_csv(table_name + '.csv', index_label='index')
    
def mergeITISCsvs(csvDir, kingdomID):
    """ merges the csv files created in ITIS_To_csv() keeping 
    only those fields which are necessary for local taxonamy alignments.
    
    csvDir: string path to the folder containing csvs generated
            from ITIS_To_csv.
    
    kingdomIDs: 1 = Bacteria, 2 = Protozoa, 3 = Plantae, 4 = Fungi, 
                5 = Animalia, 6 = Chromista, 7 = Archaea   
    """

    kingdomID = str(kingdomID)
    df = pd.DataFrame()
    colsOfInterest = ['tsn','complete_name', 'n_usage', 'kingdom_id', 'taxon_author_id', 'hybrid_author_id']
    
    #tax = pd.read_csv('../projectSupport/orig_results_county_Dist-master/itisSqlite102918/csvs/taxonomic_units.csv', usecols = colsOfInterest, dtype='str')
    tax = pd.read_csv('{}/taxonomic_units.csv'.format(csvDir), usecols = colsOfInterest, dtype='str')
    tax = tax.loc[tax['kingdom_id'] == kingdomID]   
    tax['complete_name'] = tax['complete_name'].transform(cleanInputStr)
    #syn = pd.read_csv('../projectSupport/orig_results_county_Dist-master/itisSqlite102918/csvs/synonym_links.csv', usecols= ['tsn','tsn_accepted'], dtype='str')
    syn = pd.read_csv('{}/synonym_links.csv'.format(csvDir), usecols= ['tsn','tsn_accepted'], dtype='str')
    tax = pd.merge(tax, syn, on='tsn', how='left', sort=False)    
    tax['tsn_accepted'].fillna(tax['tsn'], inplace= True)

    # used in lookupAuthor, keeping it outside the function to avoid loading it in every lookup
    #adf = pd.read_csv('../projectSupport/orig_results_county_Dist-master/itisSqlite102918/csvs/taxon_authors_lkp.csv',usecols= ['taxon_author_id','taxon_author'], dtype='str')
    adf = pd.read_csv('{}/taxon_authors_lkp.csv'.format(csvDir), dtype='str')

    def lookupAuthor(authorID):
        """ called during mergeITISCsvs to fill in author names """
        authorID = str(authorID)
        authNames= adf[adf['taxon_author_id'] == authorID]['taxon_author'].values
        if len(authNames) < 1:
            return ''
        elif len(authNames) >1:
            print(authNames)
        authName = authNames[0]            
        
        return authName

    for col in ['taxon_author_id', 'hybrid_author_id']:
        tax[col] = tax[col].transform(lookupAuthor)
    
    return tax

def cleanInputStr(inputStr):
    # drop to lower case, strip both sides of whitespace
    #if not strCleaningRegex:
    #    strCleaningRegex = re.compile('[^a-z ]')    
    toCleanString = inputStr.lower()
    toCleanString = strCleaningRegex.sub('', toCleanString)
    toCleanString = toCleanString.strip()
    wordList = toCleanString.split()
    if len(wordList) > 2:
        omitList = ['var','ssp','x']
        toCleanString = ' '.join([x for x in wordList if x not in omitList])
    outputStr = toCleanString
    return outputStr

strCleaningRegex = re.compile('[^a-z ]')
itis_SQL_Loc = '../projectSupport/orig_results_county_Dist-master/itisSqlite102918/ITIS.sqlite'
ITIS_To_csv(itis_SQL_Loc)
csv_Loc = '../projectSupport/orig_results_county_Dist-master/itisSqlite102918/csvs'
itisAlignmentRef = mergeITISCsvs(csv_Loc, 3)
itisAlignmentRef.to_csv('itis_Taxonomy_Reference.csv', index = False, encoding = 'utf-8')