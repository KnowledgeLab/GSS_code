"""

filename: EDUC_vs_DEGREE.py

description: This code compares models that use the 'EDUC' variable and replaces them with the less commonly used cognate 'DEGREE.'
It then does the same for models that use 'DEGREE' and replaces them with 'EDUC'

inputs:

outputs:

@author: Misha

"""
from __future__ import division
import cPickle as cp
import pandas as pd
import savReaderWriter as srw
import numpy as np
import statsmodels.formula.api as smf 
import random, sys
from scipy.stats import pearsonr, ttest_ind, ttest_rel
from random import choice
import time

# global variables
# i am taking out year 1984 for now because i don't have variables data on it! need to log in to commander.uchicago.edu
# and create a text file from variable view from that year's GSS...
GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 
			1980, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 
			1990, 1991, 1993, 1994, 1996, 1998, 
			2000, 2002, 2004, 2006, 2008, 2010, 2012]


# LOAD FILES ########################################################################

'''
sys.path.append('../Code/')
from articleClass import *
from filterArticleClasses import filterArticles 
pathToData = '../Data/'
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

# load GSS data
GSSFilename = 'GSS Dataset/GSS7212_R2.sav'
data = srw.SavReader(pathToData + GSSFilename)
df = pd.DataFrame(data.all(), index=data[:,0], columns=ALL_VARIABLE_NAMES)
with data:  # this makes sure the file will be closed, memory cleaned up after the program is run
    data = np.array(data.all()) # this makes sure the entire dataset is loaded into RAM, which makes accessing much faster
'''

from collections import defaultdict

allPropsForYearsUsed = []
allPropsForYearsPossible =[]
allParamSizesForYearsUsed = []
allParamSizesForYearsPossible = []
allRsForYearsUsed, allRsForYearsPossible = [], []

print 'len of articleClasses:', len(articleClasses)

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

    # if line above removed DV, then can't use this model, return None
    if not design: return None    

    #need to make sure there are still IVs left after we dropped some above    
    if design.shape[1] < 2: 
        print 'no IVs available. Skipping.'
        return None
        
    # skip if there's not enough data after deleting rows
    if design.shape[0] < design.shape[1]: # if number of rows is less than number of columns
        print 'Not enough observations. Skipping...'
        return None
       
    # create formula
    formula = 'standardize('+ DV +', ddof=1) ~ ' 
    for col in design.columns[1:]: # don't include the DV in the RHS!
        formula += 'standardize('+ col + ', ddof=1) + '  # normalize the coefficients. ddof=1 calculates typical sd, while ddof=0 does MLE 
    formula = formula[:-2] # remove the last plus sign

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

    
    
def identifyCognates(LHS, cIVs, GSSYearsUsed, corrThreshold):
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
    cIVsWithCognates = set(cIVs).intersection(set(dictOfVariableGroups)) #- set(['EDUC', 'DEGREE']))        
    if not len(cIVsWithCognates):
        print 'No cognates for the specified central IVs'            
        return None
    
    # figure out which of the central IVs actually has cognates.
    # and choose the one that correlates most highly                
    cIVCogPairs = {}
            
    for cIV in cIVsWithCognates:

        potCogsMat = reduce(pd.DataFrame.append, [df.loc[yr, [cIV] + list(dictOfVariableGroups[cIV])] for yr in GSSYearsUsed])

        # some columsn will be all np.nan, because those cognates won't be in the appropriate GSS datasets
        # get rid of those columns
        potCogsMat = removeMissingValues(potCogsMat, axis=1) # this replaces ALL miss.values with np.NaN, even
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
        for potCog in set(potCogsMat)-set([cIV]):        
            subPotCogsMat = potCogsMat[[cIV, potCog]].dropna(axis=0)
            currCorr = pearsonr(subPotCogsMat[cIV], subPotCogsMat[potCog])[0]             
            
            # the next line is very important. It sets the threshold for minimum             
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
    
    
############################################################
if __name__ == "__main__":    
    
    # contains for storing (variable, cognate) tuples in order to see what substitutions
    #i'm most commonly making
    from collections import Counter
    variableCognateTuples = []
    
    # define the storage containers for outputs
    outputEDUC, outputDEGREE = defaultdict(dict), defaultdict(dict)
    groups = ['original', 'cognate']
    outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', 'numTotal']
    for group in groups:
        for outcome in outcomes:
            outputEDUC[group][outcome], outputDEGREE[group][outcome] = [], []
            
    articleClasses = filterArticles(articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, centralIVs=True)

    # Define the 2 groups of articles I'm interested in
    articleClassesEDUC = [a for a in articleClasses if 'EDUC' in a.centralIVs and 'DEGREE' not in (a.centralIVs+a.IVs)]            
    articleClassesDEGREE = [a for a in articleClasses if 'DEGREE' in a.centralIVs and 'EDUC' not in (a.centralIVs+a.IVs)]            

    for article in random.sample(articleClassesEDUC, 20):
    #for article in articleClasses:
    #for article in [a for a in articleClasses if a.articleID == 934]:
        
        print 'Processing article:', article.articleID, 'in EDUC articles.'
                      
        # define the outcomes I'm interseted in for the two groups. td = "temp data" 
        # and initialize them for both groups
        td = defaultdict(dict)
        for group in groups:             
            td[group]['numTotal'] = 0.0
    #        td[group]['coeffsSig'] = []
            td[group]['numSig'] = []   # proportions of significant coeffs
    #        td[group]['paramSizes'] = []
            td[group]['paramSizesNormed'] = []
            td[group]['Rs'] = []
            td[group]['adjRs'] = []
            td[group]['pvalues'] = []

        # let's see if this article is suitable for cognates analysis:
        originalLHS = article.IVs + article.controls

        # if we got this far, then this article does have suitable cognates, so let's estimate models       
        # Now let's estimate the models
        for DV in article.DVs:            
            for year in article.GSSYearsUsed:
                
                # RUN MODELS FROM GROUP 1 ############################################  
                # group 1
                group = 'original'
                print 'Running original models.'
                
                # make sure cIV is **last** in the list of variables
                originalLHS.remove('EDUC')
                originalLHS.append('EDUC')
    
                results = runModel(year, DV, originalLHS)                     
                if not results: continue # results will be None if the formula cant be estimated
            

                # GROUP 2 MODELS (WITH 'EDUC' REPLACED BY 'DEGREE')
                group = 'cognate'
                print 'Running cognate models'
                
                cognateLHS = originalLHS[:]                
                cognateLHS.remove('EDUC')
                cognateLHS.append('DEGREE') # need to put it in list otherwise it treats each letter as an element [???]
                
                resultsCognate = runModel(year, DV, cognateLHS)          
                if not resultsCognate: continue # results will be None if the formula cant be estimated

                # check to make sure both models estimated the same number of parameters
                if len(results.params) != len(resultsCognate.params):
                    print 'The number of variables in original model is different from the number in cognate model. Skipping.'                    
                    continue         
                
                if results.pvalues[-1] > 0.05: continue
                    
                    
                # save the intermediate results                   
                # Intermediate output (for years, because will average across these)
                td['original']['Rs'].append(results.rsquared)
                td['original']['adjRs'].append(results.rsquared_adj)
                td['original']['numTotal'] += len(results.params[1:])
                td['original']['numSig'].append(results.pvalues[-1] < 0.05) # start at 1 because don't want to count the constant
                td['original']['paramSizesNormed'].append(abs(results.params[-1])) # get the absolute value of the standardized coefficients and take the mean 
                td['original']['pvalues'].append(results.pvalues[-1])  

                td['cognate']['Rs'].append(resultsCognate.rsquared)
                td['cognate']['adjRs'].append(resultsCognate.rsquared_adj)
                td['cognate']['numTotal'] += len(resultsCognate.params[1:])
                td['cognate']['numSig'].append(resultsCognate.pvalues[-1] < 0.05) # start at 1 because don't want to count the constant
                td['cognate']['paramSizesNormed'].append(abs(resultsCognate.params[-1])) # get the absolute value of the standardized coefficients and take the mean 
                td['cognate']['pvalues'].append(resultsCognate.pvalues[-1])

                
            # The change I'm making is that the block below is now within the for loop
            # of "for DV in article.DVs". So I'm averaging over years but not DVs                    
            # if an article's model isn't run on both group 1 and group 2, skip it        
            if td['original']['numTotal'] == 0 or td['cognate']['numTotal'] == 0: continue
                
            for group in groups:      
                outputEDUC[group]['Rs'].append( np.mean(td[group]['Rs'])) 
                outputEDUC[group]['adjRs'].append(np.mean( td[group]['adjRs'])) 
                outputEDUC[group]['propSig'].append(np.mean(td[group]['numSig'])) 
                outputEDUC[group]['paramSizesNormed'].append(np.mean( td[group]['paramSizesNormed'])) 
                outputEDUC[group]['pvalues'].append(np.mean( td[group]['pvalues']))
                outputEDUC[group]['numTotal'].append(td[group]['numTotal'] / len(td[group]['Rs'])) #divide by len of R^2 array to get a mean of variables estimated PER model                           
        

    for article in articleClassesDEGREE:
    #for article in articleClasses:
    #for article in [a for a in articleClasses if a.articleID == 934]:
        
        print 'Processing article:', article.articleID, 'in DEGREE articles.'
                     
        # define the outcomes I'm interseted in for the two groups. td = "temp data" 
        # and initialize them for both groups
        td = defaultdict(dict)
        for group in groups:             
            td[group]['numTotal'] = 0.0
    #        td[group]['coeffsSig'] = []
            td[group]['numSig'] = []   # proportions of significant coeffs
    #        td[group]['paramSizes'] = []
            td[group]['paramSizesNormed'] = []
            td[group]['Rs'] = []
            td[group]['adjRs'] = []
            td[group]['pvalues'] = []

        # let's see if this article is suitable for cognates analysis:
        originalLHS = article.IVs + article.controls

        # if we got this far, then this article does have suitable cognates, so let's estimate models       
        # Now let's estimate the models
        for DV in article.DVs:            
            for year in article.GSSYearsUsed:
                
                # RUN MODELS FROM GROUP 1 ############################################  
                # group 1
                group = 'original'
                print 'Running original models.'
                
                # make sure cIV is **last** in the list of variables
                originalLHS.remove('DEGREE')
                originalLHS.append('DEGREE')
    
                results = runModel(year, DV, originalLHS)                     
                if not results: continue # results will be None if the formula cant be estimated
                
                # GROUP 2 MODELS (WITH 'EDUC' REPLACED BY 'DEGREE')
                group = 'cognate'
                print 'Running cognate models'
                
                cognateLHS = originalLHS[:]                
                cognateLHS.remove('DEGREE')
                cognateLHS.append('EDUC') # need to put it in list otherwise it treats each letter as an element [???]
                
                resultsCognate = runModel(year, DV, cognateLHS)          
                if not resultsCognate: continue # results will be None if the formula cant be estimated
                print DV, '~', cognateLHS, 'on year', year
                                 
                # check to make sure both models estimated the same number of parameters
                if len(results.params) != len(resultsCognate.params):
                    print 'The number of variables in original model is different from the number in cognate model. Skipping.'                    
                    continue         
                
                # !!!!!!!!!! NEW CONDITION. NEEDS TO BE IN 2 PLACES, HERE AND ABOVE.
                if results.pvalues[-1] > 0.05: continue
                    
                # save the intermediate results                   
                # Intermediate output (for years, because will average across these)
                td['original']['Rs'].append(results.rsquared)
                td['original']['adjRs'].append(results.rsquared_adj)
                td['original']['numTotal'] += len(results.params[1:])
                td['original']['numSig'].append(results.pvalues[-1] < 0.05) # start at 1 because don't want to count the constant
                td['original']['paramSizesNormed'].append(abs(results.params[-1])) # get the absolute value of the standardized coefficients and take the mean 
                td['original']['pvalues'].append(results.pvalues[-1])  

                td['cognate']['Rs'].append(resultsCognate.rsquared)
                td['cognate']['adjRs'].append(resultsCognate.rsquared_adj)
                td['cognate']['numTotal'] += len(resultsCognate.params[1:])
                td['cognate']['numSig'].append(resultsCognate.pvalues[-1] < 0.05) # start at 1 because don't want to count the constant
                td['cognate']['pvalues'].append(resultsCognate.pvalues[-1])  
                td['cognate']['paramSizesNormed'].append(abs(resultsCognate.params[-1])) # get the absolute value of the standardized coefficients and take the mean 
         
            # The change I'm making is that the block below is now within the for loop
            # of "for DV in article.DVs". So I'm averaging over years but not DVs                    
            # if an article's model isn't run on both group 1 and group 2, skip it        
            if td['original']['numTotal'] == 0 or td['cognate']['numTotal'] == 0: continue
          
            for group in groups:      
                outputDEGREE[group]['Rs'].append( np.mean(td[group]['Rs'])) 
                outputDEGREE[group]['adjRs'].append(np.mean( td[group]['adjRs'])) 
                outputDEGREE[group]['propSig'].append( np.mean(td[group]['numSig'])) 
                outputDEGREE[group]['paramSizesNormed'].append(np.mean( td[group]['paramSizesNormed'])) 
                outputDEGREE[group]['pvalues'].append(np.mean( td[group]['pvalues']))
                outputDEGREE[group]['numTotal'].append(td[group]['numTotal'] / len(td[group]['Rs'])) #divide by len of R^2 array to get a mean of variables estimated PER model                           

        
    print 'TTests'
    for output in [outputEDUC, outputDEGREE]:
        print '\n'
        for outcome in outcomes:
            print 'Means of original and cognate:', np.mean(output['original'][outcome]), np.mean(output['cognate'][outcome]), 'Paired T-test of ' + outcome, ttest_rel(output['original'][outcome], output['cognate'][outcome])

    # should i put a delete command for data here?
    '''            
    cp.dump(allPropsForYearsPossible, open(pathToData + 'allPropsForYearsPossible.pickle', 'wb'))
    cp.dump(allPropsForYearsUsed, open(pathToData + 'allPropsForYearsUsed.pickle', 'wb'))
    '''