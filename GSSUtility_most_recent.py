
# coding: utf-8

# In[ ]:


from __future__ import division
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
# import rpy2.robjects as robjects
# from rpy2.robjects import pandas2ri
# pandas2ri.activate()
# from rpy2.robjects import StrVector
# import rpy2
# import pandas.rpy.common as com


# In[ ]:


# DEFINE CONSTANTS

# maximum levels a categorical variable can have. if more than this, than dropping this variable. This is to prevent
# the use of variables that have 20-50 levels and will be estimated with each level separately, which a researcher
# would never actually do in real life
MAX_LEVELS_OF_CAT_VARIABLE = 15

GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 
            1980, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 
            1990, 1991, 1993, 1994, 1996, 1998, 
            2000, 2002, 2004, 2006, 2008, 2010, 2012]


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
    df_vartypes['DENOM'] = 30
    df_vartypes['DENOM16'] = 30
    df_vartypes['PARTYID'] = 'DONOTUSE'
    df_vartypes['WRKSTAT'] = 'DONOTUSE'

    # temp_file = open(pathToData + 'variableTypes.pickle', 'wb')
    dump(df_vartypes.to_dict(), open(pathToData + 'variableTypes.pickle', 'wb'))


# In[3]:


# df_vartypes['PARTYID']


# In[2]:


'''
Created on Wed Apr 02, 2014
@author: Misha Teplitskiy, mishateplitskiy.com

description:
This file contains classes and functions that are commonly used in all analyses of GSS project. The functions are

- removeMissingValues()
- removeConstantColumns()
- runModel()
- filterArticles()
- createFormula()

The classes are articleClass, dataContainer
'''

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
    # lines below are fold old way of imputing (using R)
#     r = None
#     mice = None
#     complete = None
    
    def __init__(self, pathToData='../../Data/'):
        
          # lines below are for old way of imputing (using R)
#         import rpy2.robjects as robjects
#         self.r = robjects.r
        
#         from rpy2.robjects.packages import importr
#         importr('mice')
#         self.mice = self.r['mice']
#         self.complete = self.r['complete']
        
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
            import cPickle            
#             df = cPickle.load(open(pathToDf + 'df.pickle', 'rb'))            
            df = pd.read_pickle(pathToDf + 'df.pickle')
            globals()['df'] = df
            self.df = df                  
        else: 
            self.df = globals()['df']
            
        
def removeMissingValues(design, axis=0):
    '''
    Description: Goes through each column in DataFrame and replaces its missing values with np.nan.
    if axis=0: gets rid of all rows that have at least one missing value.
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
        if len(design[col].unique()) == 1 or np.all(design[col].isnull()): # if any IVs or controls constant, drop 'em
            print 'Dropping column', col, 'because it is constant'                    
            #raw_input('asdfa')            
            design = design.drop(col, axis=1) # inplace=True option not available because i'm using an old Pandas package?
#             print design.columns
    
    return design
    
def createFormula(dataCont, design, return_nominals=False, standardized=True):
    '''
    Takes the design matrix (where first column is DV)
    and creates a formula for Pandas/Statsmodels using the dict of variableTypes,
    where I've coded some variables as being categorical (and specified how many levels [answer choices] they have)
    some as continuous, and some as DONOTUSE (at the moment, 2016-07-08, I cannot remember what DONOTUSE is about.. 
    but I think norc-coding-scheme code variable is one such DONOTUSE variable, because it's not used in the model specification in the paper, presumably)
    codes:
        C = continuous, CL = continuous-like (no difference betw. this and "C")
        number = categorical, where number is the number of levels
        DONOTUSE = would need to go back to the spreadsheet file to see where I used this code (probably for things with many, many levels)
       
    return_nominals: default=False
        if True, returns a list of variables that are nominal (=categorical); doesn't return the formula
        
    standardized=True: this is used for running models for the replication analysis, so that we can compare the returned 
        coefficients to the published (unstandardized) ones. So, standardize by default (for our mini-analyses for the paper), but do not 
        standardize for the replication analysis.        
        Note: the name is "standardized" and not "standardize" because standardize is an operator in the Patsy formula-making language!!!
    
    2017-07-13:
        - added "ddof=1" to standardize functions because I discovered that makes a difference (???). 
            - now need to run, but haven't yet.
            - also need to try "manual standardize" in the runModel section
    '''
    
    nominals = []
    
    # LHS (dep. variable type)
    # check to make sure the DV is not 'DONOTUSE' or a categorical
    DV = design.columns[0]
    
    # if do not know what type DV is, assume it's continuous
    if DV not in dataCont.variableTypes: 
        if standardized:
            formula = 'standardize('+ DV +', ddof=1) ~ ' 
        else: 
            formula = DV + ' ~ '
    
    # if DO know what variable type DV is then...
    else:
        varType = dataCont.variableTypes[DV]
        
        if varType == 'DONOTUSE' and not return_nominals: # DV is unsuitable because DONOTUSE
            print 'DV %s is of type DONOTUSE' % DV
            return None
        elif type(varType) == int and varType > 2 and not return_nominals: # DV is unsuitable because categorical with >2 levels
            print 'DV %s is categorical with more than 2 categories' % DV
            return None
        
        else:
            if standardized:
                formula = 'standardize('+ DV +', ddof=1) ~ ' 
            else:
                formula = DV + ' ~ '
                
    # RHS (right-hand side)
    for col in design.columns[1:]: # don't include the DV in the RHS (the DV is the first element)!
 
        if col in dataCont.variableTypes:        

            varType = dataCont.variableTypes[col]        

            if varType == 'DONOTUSE': 
                print 'IV %s is of type "DONOTUSE"' % col
                continue
                
            elif type(varType) == int:
                if varType > MAX_LEVELS_OF_CAT_VARIABLE: # A variable defined at the beginning of script that limits how many levels a categorical variable is allowed to have (some, like region, will have dozens of levels)
                    print 'categorical variable %s has more than %d levels' % (col, MAX_LEVELS_OF_CAT_VARIABLE)
                else: 
                    formula += 'C('+ col + ') + '        
                    nominals.append(col)
                continue
        
        # all other cases (not in dict, in dict but C or CL), treat it as continuous
        if standardized:
            formula += 'standardize('+ col + ', ddof=1) + ' # if it's not in dict, treat it as C
        else:
            formula += col + ' + ' # if it's not in dict, treat it as C
    # the last 3 characters should be ' + '
    formula = formula[:-3]
    
#     print 'IVs count=', design.shape[1]-1, 'fomula is:', formula
    
    if '~' not in formula and not return_nominals: 
        print 'Couldnt construct formula:', formula
        return None # no suitable IVs added to formula
    else: 
        if return_nominals==True: return nominals
        else: return formula
    
def independent_columns(A, tol = 1e-02):
    """
    Return an array composed of independent columns of A.

    Note the answer may not be unique; this function returns one of many
    possible answers.

    http://stackoverflow.com/q/13312498/190597 (user1812712)
    http://math.stackexchange.com/a/199132/1140 (Gerry Myerson)
    http://mail.scipy.org/pipermail/numpy-discussion/2008-November/038705.html
        (Anne Archibald)"""
    Q, R = np.linalg.qr(A.dropna())
    independent = np.where(np.abs(R.diagonal()) > tol)[0]
    return A.iloc[:, independent]

def matrixrank(A,tol=1e-2):
    """
    http://mail.scipy.org/pipermail/numpy-discussion/2008-February/031218.html
    """
    s = np.linalg.svd(A,compute_uv=0)
    return sum( np.where( s>tol, 1, 0 ) )

def runModel(dataCont, year, DV, IVs, controls=[], custom_data=None, standardized=True):
    '''  
    inputs:
      - the year of GSS to use
      - Dependent Variable (just 1)
      - list of independent and control variables
      - custom_data = a Pandas Dataframe with a custom GSS dataset. This will be used by "run_specific_article_on_current_data" Notebook where I will provide (a subset of) the GSS data that was used in some publication
      - standardized=True: this is used for running models for the replication analysis, so that we can compare the returned 
            coefficients to the published (unstandardized) ones. So, standardize by default (for our mini-analyses for the paper), but do not 
            standardize for the replication analysis. Note: the name is "standardized" and not "standardize" because standardize is an operator in the Patsy formula-making language!!!        
    
    outputs:
      if: OLS model estimation was possible, return results data structure from statsmodels OLS. 
          results contains methods like .summary() and .pvalues
      else: return None 
    '''
    if custom_data is None:
        design = df.loc[year, [DV] + IVs + controls]
    else:
        design = custom_data.loc[year, [DV] + IVs + controls]
        
    design = design.astype(float) # again because R messes up for ints

#    design.index = range(len(design)) # using R for imputation messes up when the index is all the same values (year)
         
#     try:
        
#         # MI version
#         rcode='''
#             library(mi)
#             mydf = %s
#             IMP = mi(mydf, n.imp=2, n.iter=6, max.minutes=1)
#             imp1 <- mi.data.frame(IMP, m = 1)
#             ''' % com.convert_to_r_dataframe(design).r_repr()
#         dataCont.r(rcode)
#         design = com.convert_robj(dataCont.r['imp1'])
        
        #MICE version
#         design.iloc[:,:] = com.convert_robj(dataCont.complete(dataCont.mice(design.values, m=1))).values
        
#         print 'imputing worked fine'
#     except:
#         print 'imputing didnt work'
#         print year, DV, IVs

    # check if we need to impute at all. if number of complete cases <= number of variables, then impute
#     if design.dropna().shape[0] <= design.shape[1]:

    # IMPUTE MISSING VALUES (in the naive way, with mode [nominal variables] and mean [continuous variables]
    nominals = createFormula(dataCont, design, return_nominals=True)
    non_nominals = list(set(design.columns) - set(nominals)) # list because sets are unhashable and cant be used for indices
    if len(non_nominals)>0: 
        design[non_nominals] = design[non_nominals].fillna(design[non_nominals].mean()) # the naive way
    if len(nominals)>0:
        design[nominals] = design[nominals].fillna(design[nominals].mode())

    # constant columns happen somewhat often, e.g. a variable like religous is always == 1 if the study also uses a varaiable
    # like denom == the specific denomination
    design = removeConstantColumns(design) # i used to have design.dropna() passed to the function, but it seems silly because we filled NaNs just above
     
    # if the line above removed DV column, then can't use this model, return None
    if design is None or DV not in design: 
        print 'design is None or DV not in design'
        return None    

#     keep only non-collinear columns
    design = independent_columns(design)

    #need to make sure there are still IVs left after we dropped some above    
    if design.shape[1] < 2: 
        print 'no IVs available. Skipping.'
        return None
        
    # skip if there's not enough data after deleting rows
    if design.shape[0] < design.shape[1]: # if number of rows is less than number of columns
        print 'Not enough observations. Skipping...'
        return None

    # create formula
    formula = createFormula(dataCont, design, standardized=standardized)
    if not formula: 
        print 'Couldnt construct a suitable formula'
        return None
    
    
    # calculate the results   
#     try:       
    results = smf.ols(formula, data=design.dropna()).fit() 
        
#     except:
#         print 'Error running model', formula
#         print design
#         return None
    
    # QUALITY CHECK!!!: a check on abnormal results
    if (standardized and (abs(results.params) > 10).any()) or results.rsquared > 0.98:
        print 'Either the  params or the R^2 is too high. Skipping. Formula:'
        print formula
        return None
        # raise <--- NEED TO THINK THROUGH WHAT TO DO HERE...
        # Reasons this case may come up:
        # 1. The formula has very related variables in it: 'DENOM ~ DENOM16', and correlation was 1.0                
        # 2. Seems to happen even with less extreme collinearity

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
        modelUsed = pd.read_pickle(pathToData + 'ARTICLEID_AND_TRUE_IF_LINEAR_NONLINEAR.pickle')

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


# In[134]:


# # PRACTICE ################

# import rpy2.robjects as robjects
# from rpy2.robjects import pandas2ri
# pandas2ri.activate()
# import pandas.rpy.common as com
# # import GSSUtility as GU
# from rpy2.robjects.packages import importr
# # R's "base" package
# amelia = importr('Amelia')


# design = pd.DataFrame({'educ':np.random.randint(0,3,100), 'status':np.random.randint(0, 2, 100), 'income':np.random.randn(100)} )
# design['tenure'] = np.random.randn(100) + 3*design.status + 2*design.educ + 3*design.income
# design.iloc[np.random.randint(0, 100, 80), 0] = np.nan
# design.iloc[np.random.randint(0, 100, 70), 1] = np.nan
# design.iloc[np.random.randint(0, 100, 70), 2] = np.nan
# design.index = range(100,200)

# from rpy2.robjects import conversion
# dataf = conversion.py2ro(design)

# # amelia.amelia_amelia(design, m = 1, boot.type = "none")

# # gonna cut off the following from the line above.. shouldn't need it:
# #.copy(deep=True)  # Need to make a deep copy so that original df isn't changed

# # constant columns happen somewhat often, e.g. a variable like religous is always == 1 if the study also uses a varaiable
# # like denom == the specific denomination
# # design = removeConstantColumns(design) 

# # IMPUTE MISSING VALUES
# # We will use R's "mi" module to imput missing values
# r = robjects.r
# design_r_version = com.convert_to_r_dataframe(design).r_repr()

# # rcode = '''
# #     library(mi)
# #     library(stats)
# #     library(Amelia)
# #     library(Zelig)

# #     mydf = %s
# #     mydfimp = amelia(mydf, m = 1, boot.type = "none", noms=c("status", "educ"))
   
   
# #    #mydfimp = amelia(mydf, noms=c("status", "educ"))
    
# # #     res = zelig(tenure~income+factor(educ)+factor(status), data=mydfimp$imputations, model="ls")
# # #     res2 = lm(tenure~income+educ+status, data=mydf)
    
# # #     coefs = coef(summary(res))
    
# # ''' % (design_r_version)

# # r(rcode)



# # # # QUALITY CHECK!!!: a check on abnormal results
# # # if (abs(results.params) > 5).any() or results.rsquared > 0.98:
# # #     print 'Either the  params or the R^2 is too high. Skipping.'
# # #     return None
# # #     # raise <--- NEED TO THINK THROUGH WHAT TO DO HERE...
# # #     # Reasons this case may come up:
# # #     # 1. The formula has very related variables in it: 'DENOM ~ DENOM16', and correlation was 1.0                
# # #     # 2. The variation in DV is huge ('OTHER' [religious affiliation] or 'OCC' [occupational status]) while 
# # #     # variation in IV is much smaller. Wait, I should standardize DV too??? Tryingt this now.

# # # if np.isnan(results.params).any():
# # #     raise                

# # # return results

# amelia


# In[122]:


# com.convert_robj(r('mydfimp$imputations$imp1'))


# In[123]:


# print r('summary(res)')


# In[124]:


# # com.convert_robj(r('coef(summary(res))'))
# print r('mean(as.numeric(sapply(res, summary)["r.squared",]))')
# print r('mean(as.numeric(sapply(res, summary)["adj.r.squared",]))')


# In[125]:


# import re
# pattern = r'C\(.+?\)'
# res = re.match(pattern, 'asdfs~C(sdfsdaf)+Casdfdsf')


# In[130]:


# mydf = pd.read_csv('../Data/test_for_errors.csv', index_col=0)
# mydf.index = range(len(mydf))


# In[131]:


# from rpy2 import robjects
# import rpy2.robjects.packages as rpackages
# import rpy2.robjects.numpy2ri as numpy2ri
# numpy2ri.activate()
# # robjects.activate()


# rpackages.importr('Amelia')
# rpackages.importr('mi')

# amelia = robjects.r['amelia']
# mi = robjects.r['mi']

# obj1 = amelia(com.convert_to_r_dataframe(mydf), m=1, boot="none")


# In[128]:


# com.convert_robj(obj1.rx2('imputations').rx2('imp1'))

