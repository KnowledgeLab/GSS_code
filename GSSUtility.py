
# coding: utf-8

# In[1]:

if __name__ == '__main__':
    #########
    # small script to amend the varTypes dict that stores variable types
    # the original list is in an Excel file in the Data folder on my local machine 
    #
    import pandas as pd
    from cPickle import load, dump

    pathToData='../Data/'
    temp_file = open(pathToData + 'variableTypes.pickle', 'rb')
    varTypes = load(temp_file)
    temp_file.close()

    df_vartypes = pd.Series(varTypes)
    df_vartypes['HOMOSEX'] = 'CL'
    df_vartypes['LIFE'] = 'CL'

    # temp_file = open(pathToData + 'variableTypes.pickle', 'wb')
    dump(df_vartypes.to_dict(), open(pathToData + 'variableTypes.pickle', 'wb'))


# In[2]:

# df_vartypes['INCOME']


# In[3]:

"""
Created on Wed Apr 02, 2014
@author: Misha

description:
This file contains classes and functions that are commonly used in all analyses. The functions are

- removeMissingValues()
- removeConstantColumns()
- runModel()
- filterArticles()
- createFormula()

The classes are articleClass, dataContainer

"""
# from __future__ import division
import cPickle as cp
import pandas as pd
#import sys
#sys.path.append('../')    
import numpy as np
import statsmodels.formula.api as smf 
from scipy.stats import pearsonr, ttest_ind, ttest_rel
import time
from collections import Counter
from collections import defaultdict
from GSSUtility import *
from cPickle import load, dump
import random # note, scipy.random.choice doesn't work even though it ought to be the same function!!!


GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 
            1980, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 
            1990, 1991, 1993, 1994, 1996, 1998, 
            2000, 2002, 2004, 2006, 2008, 2010, 2012]


class articleClass():
    # attributes
    articleID = None
    IVs = []
    DV = []
    controls = []
    centralIVs = []
    GSSYearsUsed = []
    GSSYearsPossible = []
    yearPublished = None
    missingValues = [] #? 
    '''there's a missingValues dict in the data file missingValues = {"someNumvar1": {"values": [999, -1, -2]},  # discrete values
                 "someNumvar2": {"lower": -9, "upper": -1}, # range, cf. MISSING VALUES x (-9 THRU -1)
                 "someNumvar3": {"lower": -9, "upper": -1, "value": 999},
                 "someStrvar1": {"values": ["foo", "bar", "baz"]},
                 "someStrvar2": {"values': "bletch"}}
                 '''
    
    # methods
    def __init__(self, articleID=None, IVs=[], DVs=[], controls=[], centralIVs=[], GSSYearsUsed=[], GSSYearsPossible=[], yearPublished=None):
        self.articleID = articleID
        self.IVs = IVs
        self.DVs = DVs
        self.controls = controls
        self.centralIVs = centralIVs
        self.GSSYearsUsed = GSSYearsUsed
        self.GSSYearsPossible = GSSYearsPossible
        self.yearPublished = yearPublished
        
        
class dataContainer:

    # members
    dictOfVariableGroups = []    
    variableTypes = []
    articleClasses = []
    df = None
    
    # functions
    def __init__(self, pathToData='../../Data/'):
        
        self.dictOfVariableGroups = load(open(pathToData + 'dictOfVariableGroups.pickle'))
        self.variableTypes = load(open(pathToData + 'variableTypes.pickle'))
        self.articleClasses = load(open(pathToData + 'articleClasses.pickle', 'rb'))
        
        # load the dataframe 'df' only if it hasn't been loaded yet, and put it in globals() so it's there for future runs          
        if 'df' not in globals():
            '''
            pathToDf = '../../Data/GSS Dataset/stata/'
            df = pd.read_stata(pathToDf + 'GSS7212_R4.DTA', convert_categoricals=False)
            df.index = df['year']
            df.columns = map(str.upper, df.columns)
            '''
            # going to start loading 'df' via a pickle because it's 20x faster (~2 minutes)
            print 'Loading DataFrame df. This may take a few minutes.'            
            pathToDf = '../../Data/'
            import pickle            
            df = pickle.load(open(pathToDf + 'df.pickle'))            
            globals()['df'] = df
            self.df = df                  
        else: 
            self.df = globals()['df']
        
def removeMissingValues(design, axis=0):
    '''
    Description: Goes through each column in DataFrame and replaces its missing values with np.nan.
    if axis=0:  gets rid of all rows that have at least one missing value.
    if axis=1: gets rid of all columns that are entirely np.nan
    
    Inputs: DataFrame
    Output: DataFrame with any rows with at least one missing value removed.
    
    Note: Now that I'm using the Stata version of the combined GSS data, it already has missing
    values marked as np.nan. So, my only task is to drop those rows where this is the case. Don't 
    need to do it with this function.
    '''
    
    for col in design.columns:
        
        mv = dataCont.MISSING_VALUES_DICT[col]

        # if discrete missing values, replace them with np.nan
        if 'values' in mv:
            design[col].replace(mv['values'], [np.nan]*len(mv['values']), inplace=True) # it's important to have inPlace=True            

        # if range of missing values [lower, upper] is given
        elif 'lower' in mv:
            design[col][np.array(design[col] > mv['lower']) * np.array(design[col] < mv['upper'])] = np.nan                   
            # if there is a range, there is also always (?) a discrete value designated as missing
            if 'value' in mv:
                design[col].replace(mv['value'], np.nan, inplace=True) # it's important to have inPlace=True                        

    if axis==0: return design.dropna(axis=0) # drop all rows with any missing values (np.nan)        
    if axis==1: return design.dropna(axis=1, how='all')

def dropRowsWithNans(dataMat, axis=0):
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
#             print design.columns
    
    return design
    
def createFormula(dataCont, design):
    '''
    Takes the design matrix (where first column is DV)
    and creates a formula for Pandas/Statsmodels using the dict of variableTypes,
    where I've coded some variables as being categorical (and specified how many levels)
    some as continuous, and some as DONOTUSE
    codes:
        C = continuous, CL = continuous-like (no difference betw. this and "C")
        number = categorical, where number is the number of levels
        DONOTUSE = would need to go back to the spreadsheet file to see where I used this code (probably for things with many, many levels)
        
    '''
    
#     print design.columns
    
    # LHS (left-hand side)
    # check to make sure the DV is not 'DONOTUSE' or a categorical
    DV = design.columns[0]
    if DV not in dataCont.variableTypes: formula = 'standardize('+ DV +', ddof=1) ~ ' 
    else:
        varType = dataCont.variableTypes[DV]
        if varType == 'DONOTUSE':
#             print 'DV %s is of type DONOTUSE' % DV
            return None
        elif type(varType) == int and varType > 2:
#             print 'DV %s is categorical with more than 2 categories' % DV
            return None
        else:
            formula = 'standardize('+ DV +', ddof=1) ~ ' 

    # RHS (right-hand side)
    for col in design.columns[1:]: # don't include the DV in the RHS (the DV is the first element)!
 
        if col in dataCont.variableTypes:        

            varType = dataCont.variableTypes[col]        

            if varType == 'DONOTUSE': 
                print 'IV %s is of type "DONOTUSE"' % col
                continue
                
            elif type(varType) == int:
                if varType > 15: # if >15 levels
                    print 'categorical variable %s has more than 15 levels' % col
                else: formula += 'C('+ col + ') + '        
                continue
        
        # all other cases (not in dict, in dict but C or CL), treat it as continuous
        formula += 'standardize('+ col + ', ddof=1) + ' # if it's not in dict, treat it as C
    
    # the last 3 characters should be ' + '
    formula = formula[:-3]
    
#     print 'IVs count=', design.shape[1]-1, 'fomula is:', formula
    
    if '~' not in formula: return None # no suitable IVs added to formula
    else: return formula
    
def runModel(dataCont, year, DV, IVs, controls=[]):
    '''
    inputs:
      - the year of GSS to use
      - Dependent Variable (just 1)
      - list of independent and control variables
      
    outputs:
      If OLS model estimation was possibely, return results data structure from statsmodels OLS. results contains methods like .summary() and .pvalues
      else: return None 
    '''
   
    design = df.loc[year, [DV] + IVs + controls]
    # gonna cut off the following from the line above.. shouldn't need it:
    #.copy(deep=True)  # Need to make a deep copy so that original df isn't changed

    # IMPUTE MISSING VALUES: Just use the mean. THis is to avoid having too few observations for estimation, 
    # as happens sometimes when you don't impute.
    # keep in mind that this gets messy when the variable is categorical!!! should maybe use mode.. 
    design = design.fillna(design.mean())
    
    # the line below should now never (?) do anything, because there should be no more nan's
    design = dropRowsWithNans(design) # remove rows with missing observations
    
    design = removeConstantColumns(design)    

    # if the line above removed DV column, then can't use this model, return None
    if design is None or DV not in design: 
        print 'design is None or DV not in design'
        return None    

    #need to make sure there are still IVs left after we dropped some above    
    if design.shape[1] < 2: 
        print 'no IVs available. Skipping.'
        return None
        
    # skip if there's not enough data after deleting rows
    if design.shape[0] < design.shape[1]: # if number of rows is less than number of columns
        print 'Not enough observations. Skipping...'
        return None
    
    formula = createFormula(dataCont, design)
    if not formula: 
        print 'Couldnt construct a suitable formula'
        return None
        
#     print formula
    
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

def filterArticles(articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, unusedGSSYears=False, noIVs=True, noDVs=True,                     centralIVs=False, nextYearBound=0, yearPublished=False, linearModels=False, GSSCentralVariable=False):
    '''
    This function filters the articleClasses list according to the following criteria.
    arguments:
     - noIVs: skip if no IVs specified
     - noDVs: skip if no DVs specified
     - GSSYearsPossible: skip if there are no GSS years possible besides the ones the article used
     - unusedGSSYears=False: If True, then keep only those articles which have some GSS Years they could have used, but didn't
     - centralIV: skip if there is no IV(s) designated as "central"
     - nextYearBound = int: skip if next future year of data is not within "int" of last year used
                     = 0 by default, in which case it's not used
     - yearPublished=False: if set to True, yearPublished is required to be not None
     - GSSCentralVariable=False: if True, keep only those articles where GSSCentralVariable is True in the mysql
                                 table gss_question
     - linearModels=False: if True, keep only those articles where model type is .. and I should think about what to use here.
     - TODO: ADD AN "UNUSED YEARS" filter
    '''
    indicesToKeep = []
    
    pathToData = '../../Data/'
    if GSSCentralVariable:
        gssCentral = cp.load(open(pathToData + 'ARTICLEID_GSS_CENTRAL_VARIABLE.pickle', 'rb'))

    if linearModels:
        modelUsed = cp.load(open(pathToData + 'ARTICLEID_AND_TRUE_IF_LINEAR_NONLINEAR.pickle', 'rb'))

    for ind, a in enumerate(articleClasses):  # a = article
        
        # skip article if there is no info on DVs or IVs
        # Should we change this to skip only if BOTH controls AND IVs are not there?
        if noDVs:
            if len(a.DVs) < 1: continue
        
        if noIVs: 
            if len(a.IVs) < 1: continue

        if GSSYearsUsed:         
            # if there is no used years of GSS possible to run the data on, then just skip this article
            if len(a.GSSYearsUsed) < 1: continue
            
        if GSSYearsPossible:         
            # if there is no un-used years of GSS possible to run the data on, then just skip this article
            if len(a.GSSYearsPossible) < 1: continue

        if unusedGSSYears:
            unusedEarlyYears = [yr for yr in a.GSSYearsPossible if yr <= max(a.GSSYearsUsed)]
            if len(unusedEarlyYears)==0: continue
            
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
                   
        if yearPublished:
            if not a.yearPublished: continue
                        
        if GSSCentralVariable:
            if a.articleID not in gssCentral or gssCentral[a.articleID]==False: continue
        
        if linearModels:
            if a.articleID not in modelUsed: continue            
            
            
            
                
        # if the article survived all of the checks above add it to the list
        indicesToKeep.append(ind)
    
    return [articleClasses[ind] for ind in indicesToKeep] # return elements that have survived
                                                            # the filtering


def identifyCognates(dataCont, LHS, cIVs, GSSYearsUsed, corrThreshold):
    '''
    This function takes as input the variables the articles uses on the LHS, identifies suitable
    cognate variables and returns one of them, along with the suitable GSS years that have that cognate.
    GSS years to use are that subset of GSSYearsUsed which also contain the cognate
    
    inputs:
    
     LHS: list of IVs and control variables
     cIVs: list of "central" IVs
     GSSYearsUsed = Years the article actually used
     
    returns:
     None: if suitable cognates and years were not found
     (cIV, cognate, GSS years to use)        
    '''
    # check to see if there are any cognate variables for the central IVs. if not, skip.
    cIVsWithCognates = set(cIVs).intersection(set(dataCont.dictOfVariableGroups)) #- set(['EDUC', 'DEGREE']))        
    if not len(cIVsWithCognates):
        print 'No cognates for the specified central IVs'            
        return None
    
    # figure out which of the central IVs actually has cognates.
    # and choose the one that correlates most highly                
    cIVCogPairs = {}
            
    for cIV in cIVsWithCognates:

        potCogsMat = reduce(pd.DataFrame.append, [df.loc[yr, [cIV] + list(dataCont.dictOfVariableGroups[cIV])] for yr in GSSYearsUsed])

        # some columsn will be all np.nan, because those cognates won't be in the appropriate GSS datasets
        # get rid of those columns
        potCogsMat = dropRowsWithNans(potCogsMat, axis=1) # this replaces ALL miss.values with np.NaN, even
                                                           # though it only removes along axis=1
        #  below is the version which, for a given central IV (cIV), takes the cognate that's max correlated
        '''
        # first value is name of variable, second is current max, third is possible years   
        maxCorr = (None, 0.0, []) 
        for potCog in set(potCogsMat)-set([cIV]):
            # The step below is important. I am reducing my matrix down to just two columns, cIV and potCog
            # and removing the missing values from those (not the full matrix of cognates)            
            subPotCogsMat = potCogsMat[[cIV, potCog]].dropna(axis=0)
            currCorr = pearsonr(subPotCogsMat[cIV], subPotCogsMat[potCog])[0]             
            if currCorr > maxCorr[1]:
                # last value gives possibleYears (i.e. all unique row labels after missing values were removed)
                maxCorr = (potCog, currCorr, subPotCogsMat.index.unique()) 
                
        #Check to see that the potential cognate is not already in the articles' variables, 
        # and that it correlates highly enough
        if maxCorr[0] not in LHS and maxCorr[1] > 0.5: 
            print 'Possibility:', maxCorr[0], 'in place of', cIV, '. Correlation is', maxCorr[1]
            cIVCogPairs[cIV] = (maxCorr[0], maxCorr[2])
        '''             
        
        # below is the version which for a given cIV takes a random cognate that's correlated at 
        #above some threshold amount
        cogsPossForCIV = []        
        for potCog in set(potCogsMat)-set([cIV]): # for each potential cognate variable       
            subPotCogsMat = potCogsMat[[cIV, potCog]].dropna(axis=0)
            currCorr = pearsonr(subPotCogsMat[cIV], subPotCogsMat[potCog])[0]             
            
            # the following line tests if the potential cognate is a) not already in the formula
            # and b) correlated at at least corrThreshold with the cIV
            if potCog not in LHS and currCorr > corrThreshold: 
                cogsPossForCIV.append((potCog, subPotCogsMat.index.unique()))
        if cogsPossForCIV:
            cIVCogPairs[cIV] = random.choice(cogsPossForCIV)
            
    if not cIVCogPairs:  # if there is nothing in this dict 
        print 'Could not find suitable cognate. Skipping.'
        return None
    
    else:
        # of the cognate variable options, choose a random one
        cIV, (cognate, GSSYearsWithCognate) = random.choice(cIVCogPairs.items())     
        return cIV, cognate, GSSYearsWithCognate    

