"""

filename: cognateVariablesAnalysis_model_unit_of_analysis.py

description: Runs models as specified originally and again after replacing a central variable by a cognate var.
It compares regressions on what was then the new data vs same regressions on future waves

inputs:

outputs:

@author: Misha

"""

from __future__ import division
import cPickle as cp
import pandas as pd
#import savReaderWriter as srw
import numpy as np
import statsmodels.formula.api as smf 
import random, sys
from scipy.stats import pearsonr, ttest_ind, ttest_rel
from random import choice
import time

'''
# LOAD FILES ########################################################################
sys.path.append('/mnt/ide0/home/misha/GSSproject/Code/')
sys.path.append('../')
from articleClass import * 
pathToData = '../../Data/'
ALL_VARIABLE_NAMES = cp.load(open(pathToData + 'ALL_VARIABLE_NAMES.pickle'))
ALL_VARIABLE_NAMES = [str.upper(el) for el in ALL_VARIABLE_NAMES]
MISSING_VALUES_DICT = cp.load(open(pathToData + 'MISSING_VALUES_DICT.pickle', 'rb'))
MEASURE_LEVELS = cp.load(open(pathToData + 'MEASURE_LEVELS.pickle'))
articleIDAndGSSYearsUsed = cp.load(open(pathToData + 'articleIDAndGssYearsUsed-cleaned.pickle')) # load the years used
VARS_BY_YEAR = cp.load(open(pathToData + 'VARS_BY_YEAR.pickle'))
# structure of the dictionary above: { year (int) : set of variable names (strs) } 
YEAR_INDICES = cp.load(open(pathToData + 'YEAR_INDICES.pickle'))
VAR_INDICES = cp.load(open(pathToData + 'VAR_INDICES_binary.pickle', 'rb'))
articleClasses = cp.load(open(pathToData + 'articleClasses.pickle', 'rb'))
dictOfVariableGroups = cp.load(open(pathToData + 'dictOfVariableGroups.pickle'))
variableTypes = cp.load(open(pathToData + 'variableTypes.pickle'))

'''

'''
# load GSS data, ~350megs, ~20 mins to load
#pathToDf = 'C:\Users\Misha\Dropbox\GSS Project\Data/GSS Dataset/stata/'
pathToData = '../../Data/'
pathToDf = '../../Data/GSS Dataset/stata/'
df = pd.read_stata(pathToDf + 'GSS7212_R4.DTA', convert_categoricals=False)
df.index = df['year']
df.columns = map(str.upper, df.columns)
'''
'''
# load GSS data
GSSFilename = 'GSS Dataset/GSS7212_R2_copy.sav'
data = srw.SavReader(pathToData + GSSFilename)
df = pd.DataFrame(data.all(), index=data[:,0], columns=ALL_VARIABLE_NAMES)
with data:  # this makes sure the file will be closed, memory cleaned up after the program is run
    data = np.array(data.all()) # this makes sure the entire dataset is loaded into RAM, which makes accessing much faster
'''

#from GSSFunctions import *
from collections import defaultdict
#**********************************************************

# -*- coding: utf-8 -*-
"""
Created on Wed Apr 02 
@author: Misha

description:
This file contains functions that are commonly used in all analyses. The functions are

- removeMissingValues()
- removeConstantColumns()
- runModel()
- filterArticles()

"""

def removeMissingValues(dataMat, axis=0):
    '''
    Description: Goes through each column in DataFrame and replaces its missing values with np.nan.
    if axis=0:  gets rid of all rows that have at least one missing value.
    if axis=1: gets rid of all columns that are entirely np.nan
    
    Inputs: DataFrame
    Output: DataFrame with any rows with at least one missing value removed.
    '''
    
    for col in dataMat.columns:
        
        mv = MISSING_VALUES_DICT[col]

        # if discrete missing values, replace them with np.nan
        if 'values' in mv:
            dataMat[col].replace(mv['values'], [np.nan]*len(mv['values']), inplace=True) # it's important to have inPlace=True            

        # if range of missing values [lower, upper] is given
        elif 'lower' in mv:
            dataMat[col][np.array(dataMat[col] > mv['lower']) * np.array(dataMat[col] < mv['upper'])] = np.nan                   
            # if there is a range, there is also always (?) a discrete value designated as missing
            if 'value' in mv:
                dataMat[col].replace(mv['value'], np.nan, inplace=True) # it's important to have inPlace=True                        

    if axis==0: return dataMat.dropna(axis=0) # drop all rows with any missing values (np.nan)        
    if axis==1: return dataMat.dropna(axis=1, how='all')

def removeConstantColumns(design):
    '''
    Takes a Pandas DataFrame, searches for all columns that are constant, and drops them.
      - if DV (first column) is constant, return None
      - this function should be called only after all the missing value-rows are removed

    input: dataframe
    returns: dataframe without any constant columns; if DV is constant returns None
    '''
    if len(design.ix[:,0].unique()) == 1: return None # if DV constant
    for col in design:
        if len(design[col].unique()) == 1: # if any IVs or controls constant, drop 'em
            print 'Dropping column', col, 'because it is constant'                    
            #raw_input('asdfa')            
            design = design.drop(col, axis=1) # inplace=True option not available because i'm using an old Pandas package?
            print design.columns
    
    return design
    
def createFormula(design):
    '''
    Takes the design matrix (where first column is DV)
    and creates a formula for Pandas/Statsmodels using the dict ov variableTypes,
    where I've coded some variables as being categorical (and specified how many levels)
    some as continuous, and some as DONOTUSE
    '''
    
    formula = 'standardize('+ design.columns[0] +', ddof=1) ~ ' 

    for col in design.columns[1:]: # don't include the DV in the RHS!
        if col in variableTypes:        
            varType = variableTypes[col]        
            # if I previously coded this variable as donotuse, then don't use it            
            if varType == 'DONOTUSE':
                return None
                
            # otherwise, if the varType is a number (number of levels), dummy-fy it    
            elif type(varType) == int:
                if varType > 3: return None
                else: formula += 'C('+ col + ') + '        
            
            # otherwise, the variable is continuous or continuous-like            
            else: formula += 'standardize('+ col + ', ddof=1) + ' # if it's in the dict, but C or CL
        
        # if variable not in the dict, then treat it as continuous
        else: formula += 'standardize('+ col + ', ddof=1) + ' # if it's not in dict, treat it as C

    return formula[:-2] # the last 2 characters should be '+ '
    
def runModel(year, DV, IVs, controls=[]):
    '''
    inputs:
      - the year of GSS to use
      - Dependent Variable (just 1)
      - list of independent and control variables
      
    outputs:
      If OLS model estimation was possibely, return results data structure from statsmodels OLS. results contains methods like .summary() and .pvalues
      else: return None 
    '''
   
    design = df.loc[year, [DV] + IVs + controls].copy(deep=True)  # Need to make a deep copy so that original df isn't changed
    design = removeMissingValues(design) # remove rows with missing observations
    design = removeConstantColumns(design)    

    # if the line above removed DV column, then can't use this model, return None
    if design is None or DV not in design: return None    

    #need to make sure there are still IVs left after we dropped some above    
    if design.shape[1] < 2: 
        print 'no IVs available. Skipping.'
        return None
        
    # skip if there's not enough data after deleting rows
    if design.shape[0] < design.shape[1]: # if number of rows is less than number of columns
        print 'Not enough observations. Skipping...'
        return None
    
    '''
    # create formula
    formula = 'standardize('+ DV +', ddof=1) ~ ' 
    for col in design.columns[1:]: # don't include the DV in the RHS!
        formula += 'standardize('+ col + ', ddof=1) + '  # normalize the coefficients. ddof=1 calculates typical sd, while ddof=0 does MLE 
    formula = formula[:-2] # remove the last plus sign
    '''
    formula = createFormula(design)
    if not formula: return None
        
    print formula
    
    # calculate the results                                          
    results = smf.ols(formula, data=design, missing='drop').fit() # do I need the missing='drop' part?

    # QUALITY CHECK!!!: a check on abnormal results
    if (abs(results.params) > 5).any() or results.rsquared > 0.98:
        print 'Either the  params or the R^2 is too high. Skipping.'
        return None
        # raise <--- NEED TO THINK THROUGH WHAT TO DO HERE...
        # Reasons this case may come up:
        # 1. The formula has very related variables in it: 'DENOM ~ DENOM16', and correlation was 1.0                
        # 2. The variation in DV is huge ('OTHER' [religious affiliation] or 'OCC' [occupational status]) while 
        # variation in IV is much smaller. Wait, I should standardize DV too??? Tryingt this now.

    if np.isnan(results.params).any():
        raise                

    return results


'''
description: This module contains a functil filterArticleClasses which goes through the 
  articleClasses.pickle (list of Classes) created by create_articleClasses and filters that list 
  further according to specified criteria (central variables, etc.)
  It is to be used to set up the data, before running the actual models.

returns: list of articleClasses that have passed the filters
'''

def filterArticles(articleClasses, GSSYearsUsed=True, GSSYearsPossible=True, noIVs=True, noDVs=True, centralIVs=False, nextYearBound=0):
    '''
    This function filters the articleClasses list according to the following criteria.
    arguments:
     - noIVs: skip if no IVs specified
     - noDVs: skip if no DVs specified
     - newGSSYears: skip if there are no GSS years possible besides the ones the article used
     - centralIV: skip if there is no IV(s) designated as "central"
     - nextYearBound = int: skip if next future year of data is not within "int" of last year used
                     = 0 by default, in which case it's not used
    '''
    indicesToKeep = []
        
    for ind, article in enumerate(articleClasses):
        
        a = article # to make referencing its elements shorter
        
        # skip article if there is no info on DVs or IVs
        # Should we change this to skip only if BOTH controls AND IVs are not there?
        if noDVs:
            if len(a.DVs) < 1: continue
        
        if noIVs: 
            if len(a.IVs) < 1: continue

        if GSSYearsUsed:         
            # if there is no un-used years of GSS possible to run the data on, then just skip this article
            if len(a.GSSYearsUsed) < 1: continue
            
        if GSSYearsPossible:         
            # if there is no un-used years of GSS possible to run the data on, then just skip this article
            if len(a.GSSYearsPossible) < 1: continue
            
        if centralIVs:    
            # if GSS is not the central dataset used then skip
            if len(a.centralIVs) < 1: continue
                   
        if nextYearBound:
            # nextYear is an integer that specifies how soon the next available year of data is supposed to be.
            # e.g. if nextYearBound = 4, then the new future year of data is to occur within 4 years of the last year of data
            # actually used. 
            maxYearUsed = max(a.GSSYearsUsed)
            futureYearsPossible = [yr for yr in a.GSSYearsPossible if yr > maxYearUsed]
            if not futureYearsPossible or min(futureYearsPossible) > maxYearUsed + nextYearBound: continue
                
        # if the article survived all of the checks above add it to the list
        indicesToKeep.append(ind)
    
    return [articleClasses[ind] for ind in indicesToKeep] # return elements that have survived
                                                            # the filtering


#*********************************************************
allPropsForYearsUsed = []
allPropsForYearsPossible =[]
allParamSizesForYearsUsed = []
allParamSizesForYearsPossible = []
allRsForYearsUsed, allRsForYearsPossible = [], []

 
############################################################
if __name__ == "__main__":    
    
    #tempCognateOutput = open('../Data/tempCognateOutput.txt', 'w')
    articleClasses = cp.load(open(pathToData + 'articleClasses.pickle', 'rb'))
    articlesToUse = filterArticles(articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, centralIVs=True, nextYearBound=0)     
    print 'len of articleClasses:', len(articlesToUse)
    #raw_input('...')
    
    # define the storage containers for outputs
    group1 = 'onDataUsed'
    group2 = 'onFutureYear'    
    output = defaultdict(dict)
    groups = [group1, group2]
    outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', 'numTotal', \
                'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']
    for yr in range(43):
        output[yr] = {}
        for group in groups:
            output[yr][group] = {}
            for outcome in outcomes:
                output[yr][group][outcome] = []
            
           
    #for article in random.sample(articlesToUse, 200):
    for article in articlesToUse:
    #for article in [a for a in articlesToUse if a.articleID == 6755]:
    
        print 'Processing article:', article.articleID
 
        '''             
        # define the outcomes I'm interseted in for the two groups. td = "temp data" 
        # and initialize them for both groups
        td = defaultdict(dict)
        for group in groups:             
            td[group]['numTotal'] = 0.0
    #        td[group]['coeffsSig'] = []
            td[group]['numSig'] = 0.0   # proportions of significant coeffs
    #        td[group]['paramSizes'] = []
            td[group]['paramSizesNormed'] = []
            td[group]['Rs'] = []
            td[group]['adjRs'] = []
            td[group]['pvalues'] = []
        '''
        LHS = article.IVs + article.controls
        
        for DV in article.DVs:
            maxYearUsed = max(article.GSSYearsUsed)          
            resOnDataUsed = runModel(maxYearUsed, DV, LHS) # models run on max year of data used
            if not resOnDataUsed: continue

            # Now do future years
            futureYearsPossible = [yr for yr in article.GSSYearsPossible if yr > maxYearUsed]
            for futureYear in futureYearsPossible:
                resOnFutureYear = runModel(futureYear, DV, LHS) # models run on min year of future data
                if not resOnFutureYear: continue
            
                # Checks on which results to record                
                if len(resOnDataUsed.params) != len(resOnFutureYear.params):
                    print 'The number of variables in original model is different from the number in cognate model. Skipping.'                    
                    continue
                
                results = [resOnDataUsed, resOnFutureYear]
                centralVars = []            
                for civ in article.centralIVs:
                    if 'standardize(%s, ddof=1)' % (civ) in results[0].params.index:
                        centralVars.append('standardize(%s, ddof=1)' % (civ))
                    else: 
                        for col in results[0].params.index:
                            if 'C(' + civ + ')' in col:
                                centralVars.append(col)
     
                print 'IVs:', article.IVs
                print 'centralVas:', centralVars
                '''    
                centralVars = ['standardize(%s, ddof=1)' % (cv) for cv in article.centralIVs]
                centralVars = set(centralVars).intersection(results[0].params.index) # need this step because some central                                                                                            # var columns may be removed when running model
                '''
                
                for i in range(2):                 
                    output[futureYear - maxYearUsed][groups[i]]['Rs'].append(results[i].rsquared) 
                    output[futureYear - maxYearUsed][groups[i]]['adjRs'].append(results[i].rsquared_adj) 
                    output[futureYear - maxYearUsed][groups[i]]['propSig'].append(float(len([p for p in results[i].pvalues[1:] if p < 0.05]))/len(results[i].params[1:])) 
                    output[futureYear - maxYearUsed][groups[i]]['paramSizesNormed'].append(np.mean(results[i].params[1:].abs())) 
                    '''
                    if np.isnan(np.mean( td[group]['paramSizesNormed'])).any():
                        print results[i].summary()
                        raise
                    '''
                    output[futureYear - maxYearUsed][groups[i]]['pvalues'].append(np.mean( results[i].pvalues[1:]))
                    output[futureYear - maxYearUsed][groups[i]]['numTotal'].append( 1 ) #divide by len of R^2 array to get a mean of variables estimated PER model                           
                    output[futureYear - maxYearUsed][groups[i]]['pvalues_CentralVars'].append(np.mean(results[i].pvalues[centralVars]))               
                    output[futureYear - maxYearUsed][groups[i]]['propSig_CentralVars'].append(float(len([p for p in results[i].pvalues[centralVars] if p < 0.05])) \
                                                            /len(results[i].params[centralVars])) 
                    output[futureYear - maxYearUsed][groups[i]]['paramSizesNormed_CentralVars'].append(np.mean(results[i].params[centralVars].abs()))                


            ''' 
            # The change I'm making is that the block below is now within the for loop
            # of "for DV in article.DVs". So I'm averaging over years but not DVs                    
            # if an article's model isn't run on both group 1 and group 2, skip it        
            if td[group1]['numTotal'] == 0 or td[group2]['numTotal'] == 0: continue
   
            # the part below should really be in the 'td' part above, but i'm lazy for now, so keeping things as is       
            for group in groups:      
                output[group]['Rs'].append( np.mean(td[group]['Rs'])) 
                output[group]['adjRs'].append(np.mean( td[group]['adjRs'])) 
                output[group]['propSig'].append( td[group]['numSig']/td[group]['numTotal']) 
                output[group]['paramSizesNormed'].append(np.mean( td[group]['paramSizesNormed'])) 
                if np.isnan(np.mean( td[group]['paramSizesNormed'])).any():
                    print results[i].summary()
                    raise
                output[group]['pvalues'].append(np.mean( td[group]['pvalues']))
                output[group]['numTotal'].append(td[group]['numTotal'] / len(td[group]['Rs'])) #divide by len of R^2 array to get a mean of variables estimated PER model                           
            '''        
            
    print 'TTests'

    for year in range(43):
        for outcome in outcomes:
            print year            
            print 'Means of group1 and group2:', np.mean(output[year][group1][outcome]), np.mean(output[year][group2][outcome]), 'Paired T-test of ' + outcome, ttest_rel(output[year][group1][outcome], output[year][group2][outcome])
