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

# This block only necessary to generate the itis_Taxonomy_Reference.csv
# dumps itis sql db to csvs
# This block only necessary to generate the itis_Taxonomy_Reference.csv
# dumps itis sql db to csvs

def ITIS_To_csv(sqlLocStr, csvLoc):
    """ accepts a string with the sql db location and output csv location
    breaks each table out into a csv file"""
    #db = sqlite3.connect('../projectSupport/orig_results_county_Dist-master/itisSqlite102918/ITIS.sqlite')
    db = sqlite3.connect(sqlLocStr)
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(tables)
    # only interested in a few tables from these data
    tablesOfInterest = ['hierarchy','taxonomic_units','synonym_links','taxon_authors_lkp']
    for table_name in tables:
        table_name = table_name[0]
        if table_name in tablesOfInterest:
            table = pd.read_sql_query("SELECT * from %s" % table_name, db)
            table.fillna("", inplace=True)
            csvFN = csvLoc + table_name + '.csv'
            table.to_csv(csvFN, index_label='index')
    
def mergeITISCsvs(csvDir, kingdomID):
    """ merges the csv files created in ITIS_To_csv() keeping 
    only those fields which are necessary for local taxonamy alignments.
    
    csvDir: string path to the folder containing csvs generated
            from ITIS_To_csv.
    
    kingdomIDs: 1 = Bacteria, 2 = Protozoa, 3 = Plantae, 4 = Fungi, 
                5 = Animalia, 6 = Chromista, 7 = Archaea   
    """
    kingdomID = str(kingdomID)
    # keep only the necessary columns
    colsOfInterest = ['tsn','complete_name', 'n_usage', 'kingdom_id', 'taxon_author_id', 'parent_tsn', 'rank_id', 'update_date']
    tax = pd.read_csv('{}taxonomic_units.csv'.format(csvDir), usecols = colsOfInterest, dtype=str)
    
    def cvt_parent_tsn(val):
        if (val == "nan") or pd.isna(val):
            val= 0
        else:
            val = str(val).split(".")[0]
        return val

    tax['parent_tsn'] = tax['parent_tsn'].transform(cvt_parent_tsn)

    tax = tax.loc[tax['kingdom_id'] == kingdomID]   
    tax['complete_name'] = tax['complete_name'].transform(cleanInputStr)
    
    # merge in synonym links
    syn = pd.read_csv('{}/synonym_links.csv'.format(csvDir), usecols= ['tsn','tsn_accepted'], dtype='str')
    tax = pd.merge(tax, syn, on='tsn', how='left', sort=False)    
    # fill in accepted blank accepted TSNs with the default TSN
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

    tax['taxon_author_id'] = tax['taxon_author_id'].transform(lookupAuthor)

    # convert rank_id to int
    def lookupFamily(tsn):
        """ called during mergeITISCsvs to fill in family names """
        tsn = str(tsn)
        tsnData = tax[tax['tsn']==tsn]
        try:
            rankID = int(tsnData['rank_id'].values[0])
            if rankID < 140:
                # already a higher rank than family
                return ""
            elif rankID == 140:
                # already at family
                return tsnData['complete_name'].values[0]
            else:
                # otherwise lower rank than family, iterate up parent_tsn
                while rankID > 140:
                    target_tsn = tsnData['parent_tsn'].values[0]
                    if (target_tsn == "0") or (target_tsn == ""):
                        # no valid parent rank cannot determine family
                        return ""
                    else:
                        # otherwise rankID is set to the target_tsn's parent tsn
                        tsnData = tax[tax['tsn']==target_tsn]
                        rankID = int(tsnData['rank_id'].values[0])
                            
                # once iterations are done should be at rank_id == 140
                family_name = tsnData['complete_name'].values[0]
                return family_name
        except IndexError:
            print(f"Index Error at: TSN:{tsn}, tsnData:{tsnData}")
            return ""

    #tax_sample = tax.sample(500)
    tax['family'] = tax['tsn'].transform(lookupFamily)

    # sort everything by the update_date, newest first
    tax['update_date'] = pd.to_datetime(tax['update_date'], format="%Y-%m-%d")
    tax.sort_values(by=['update_date', 'complete_name'], ascending=[False, True], inplace=True)
    # reduce the dataframe to only the necessary cols
    tax = tax[['tsn', 'tsn_accepted', 'complete_name', 'taxon_author_id', 'family']]
    
    return tax


strCleaningRegex = re.compile('[^a-zA-Z. ]')

def cleanInputStr(inputStr):
    # drop to lower case, strip both sides of whitespace
    #strCleaningRegex = re.compile('[^a-zA-Z. ]')    
    #toCleanString = inputStr.lower()
    toCleanString = strCleaningRegex.sub('', inputStr)
    toCleanString = toCleanString.strip()
    wordList = toCleanString.split()
    if len(wordList) > 2:
        omitList = ['var','ssp','x','f']
        toCleanString = toCleanString.replace(' . ', ' ')
        toCleanString = ' '.join([x for x in wordList if x.lower() not in omitList])
    outputStr = toCleanString
    return outputStr

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


itis_SQL_Loc = './itisSqlite062620/ITIS.sqlite'
csvLoc = './itisSqlite062620/csvs/'
#ITIS_To_csv(itis_SQL_Loc, csvLoc)
# ITIS kingdomId for Plantae is 3
itisAlignmentRef = mergeITISCsvs(csvLoc, 3)
# now add a normalized col for referencing
strCleaningRegex = re.compile('[^a-zA-Z ]')
itisAlignmentRef['normalized_name'] = itisAlignmentRef['complete_name'].transform(normalizeStrInput)
# save it all
itisAlignmentRef.to_csv('Plantae_Reference.csv', index = False, encoding = 'utf-8')