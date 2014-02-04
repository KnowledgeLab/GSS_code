"""

filename: main_analysis_pandas_version_unused_early_years.py

description: This code runs linear regressions 

inputs:

outputs:

12/20/2013: 
 * For categorical variables, maybe count them as sig if more than half of the coeffs
 are signif. Need to see how categorical are dummy-ized to know which p-values to 
 grab.
 

notes/to-do's:
 - TODO 9/23/2013: 
     - why are the coefficient sizes so big???
         - probably because some columns are constant?! so when there's no variation, can multiply even by a huge constant 
         and there's little effect?...
         
     - insert code to remove missing values!!!
         - specifically, the lower/higher ranges
     - speed up code
         - can be done by creating a design matrix with one column (the first) missing (for the DV) in the block of code
           before the "for each DV" if not earlier
           - PROBABLY NEED TO CONVER THE WHOLE THING TO A PANEL OF DATAFRAMES
     - figure out how to run multinomial logit?!
     - figure out a better way to extract the right p-values and coefficients from the results
         - since the categoricals aren't centered, if the coefficients are of different sizes right now, that may be due simply
         to there being more "years possible".. if categorical coeffs tend to be of different sizes than cardinals..
      
 - Coefficient sizes
    - JE wants to center the variables and normalize them, to see coefficient size       

Created on Sun Sep 01 15:55:48 2013

@author: Misha

"""
from __future__ import division
import cPickle as cp
import pandas as pd
import savReaderWriter as srw
import numpy as np
import statsmodels.formula.api as smf 
import random, sys

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
pathToData = '../Data/'
ALL_VARIABLE_NAMES = cp.load(open(pathToData + 'ALL_VARIABLE_NAMES.pickle'))
ALL_VARIABLE_NAMES = [str.upper(el) for el in ALL_VARIABLE_NAMES]
MISSING_VALUES_DICT = cp.load(open(pathToData + 'MISSING_VALUES_DICT.pickle', 'rb'))
MEASURE_LEVELS = cp.load(open(pathToData + 'MEASURE_LEVELS.pickle'))
articleIDAndGSSYearsUsed = cp.load(open(pathToData + 'articleIDAndGssYearsUsed-cleaned.pickle')) # load the years used
VARS_BY_YEAR = cp.load(open(pathToData + 'VARS_BY_YEAR.pickle'))
# structure of the dictionary above: { year (int) : [ set of variable names (strs), [variable_i, metadata_i] ] } 
YEAR_INDICES = cp.load(open(pathToData + 'YEAR_INDICES.pickle'))
VAR_INDICES = cp.load(open(pathToData + 'VAR_INDICES_binary.pickle', 'rb'))
articleClasses = cp.load(open(pathToData + 'articleClasses.pickle', 'rb'))

# load GSS data
GSSFilename = 'GSS Dataset/GSS7212_R2.sav'
data = srw.SavReader(pathToData + GSSFilename)
df = pd.DataFrame(data.all(), index=data[:,0], columns=ALL_VARIABLE_NAMES)
with data:  # this makes sure the file will be closed, memory cleaned up after the program is run
data = np.array(data.all()) # this makes sure the entire dataset is loaded into RAM, which makes accessing much faster
'''

from collections import defaultdict
output = defaultdict(dict)
groups = ['group1', 'group2']
outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', 'numTotal']
for group in groups:
    for outcome in outcomes:
        output[group][outcome] = []

allPropsForYearsUsed = []
allPropsForYearsPossible =[]
allParamSizesForYearsUsed = []
allParamSizesForYearsPossible = []
allRsForYearsUsed, allRsForYearsPossible = [], []

# begin estimating models   
#for article in random.sample(articleClasses, 200):
for article in articleClasses:
#for article in [a for a in articleClasses if a.articleID == 4454]:

    print 'Processing article:', article.articleID
     
     
    #####I am going to make this check later, when I assign estimates to different groups
    # check if there are any unused "early" years
    if len(article.GSSYearsPossible) == 0 or min(article.GSSYearsPossible) > max(article.GSSYearsUsed): 
        print 'Article has no unused early years'
        continue
    else: # only keep the EARLY unused years, not the later waves of the survey
        article.GSSYearsPossible = [yr for yr in article.GSSYearsPossible if yr < max(article.GSSYearsUsed)]
    
    #article.GSSYearsPossible = [yr for yr in article.GSSYearsPossible if yr < max(article.GSSYearsUsed)]

    
    '''    
    # Only process articles with "central IVs" defined?
    if len(article.centralIVs) < 1: 
        print 'No "central" IVs. Skipping'
        continue 
    '''
    
    # coefficients significant
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
    # parameter sizes
    paramSizesForYearsUsed = []
    paramSizesForYearsPossible = []
    avgParamSizeForYearsUsed = 0.0
    avgParamSizeForYearsPossible = 0.0
    avgParamSizesNormedForYearsUsed, avgParamSizesNormedForYearsPossible = 0.0, 0.0
    RsForYearsUsed, RsForYearsPossible = [], []
    adjRsForYearsUsed, adjRsForYearsPossible = [], []
    pvaluesForYearsUsed, pvaluesForYearsPossible = [], []
    '''
    
    for year in (article.GSSYearsUsed + article.GSSYearsPossible): # for each GSS year the article used or could've used          
        
       for DV in article.DVs: # for each model

            design = df.loc[year, [DV]+article.IVs+article.controls].copy(deep=True)  # Need to make a deep copy so that original df isn't changed

            # MISSING VALUES
            for col in design.columns:
                mv = MISSING_VALUES_DICT[col]
                # if discrete missing values, replace them with np.nan
                if 'values' in mv:
                    design[col].replace(mv['values'], [np.nan]*len(mv['values']), inplace=True) # it's important to have inPlace=True            
                # if range of missing values [lower, upper] is given
                elif 'lower' in mv:
                    design[col][np.array(design[col] > mv['lower']) * np.array(design[col] < mv['upper'])] = np.nan                   
                    # if there is a range, there is also always (?) a discrete value designated as missing
                    if 'value' in mv:
                        design[col].replace(mv['value'], np.nan, inplace=True) # it's important to have inPlace=True                        
            design = design.dropna(axis=0) # drop all rows with any missing values (np.nan)        


            # remove columns that are constant; if DV is constant, skip to next model
            # this needs to come after the step above because some columns will be constant
            # only after all the missing value-rows are removed
            if len(design[DV].unique()) == 1: continue # if DV constant
            for col in design.columns:
                if len(design[col].unique()) == 1: # if any IVs or controls constant, drop 'em
                    print 'Dropping column', col, 'because it is constant'                    
                    design = design.drop(col, axis=1) # inplace=True option not available because i'm using an old Pandas package?
            
            #need to make sure there are still IVs left after we dropped some above
            if design.shape[1] < 2: 
                print 'no IVs available. Skipping.'
                continue
                
            # skip if there's not enough data after deleting rows
            # PROBLEM: dummy-ing categorical variables produces many more columns,
            # so the question is if there is enough data AFTER dummy-ing..
            if design.shape[0] < design.shape[1]: # if number of rows is less than number of columns
                print 'Not enough observations. Skipping...'
                continue
            
            '''
            # create formula
            formula = DV + ' ~ ' 
            for col in design.columns[1:]: # don't include the DV in the RHS!
                if MEASURE_LEVELS[col] == 'ratio': formula += 'center('+ col + ')'  # only center() if it's a ratio?
                else: formula += ' C(' + col + ')' # i shouldn't center() this?
                formula += ' + '
            formula = formula[:-2] 
            '''
            
            # create formula
            formula = DV + ' ~ ' 
            for col in design.columns[1:]: # don't include the DV in the RHS!
                formula += 'standardize('+ col + ', ddof=1) + '  # normalize the coefficients?
            formula = formula[:-2] # remove the last plus sign

            # calculate the results                                          
            results = smf.ols(formula, data=design, missing='drop').fit() # do I need the missing='drop' part?
                
            # QUALITY CHECK!!!: a check on abnormal results
            if (abs(results.params) > 10000).any() or results.rsquared > 0.98:
                print 'Either the  params or the R^2 is too high. Skipping.'
                print year, article.articleID
                continue
                # this has happened becaseuse the formula had 'DENOM ~ DENOM16', and correlation was 1.0                
            if np.isnan(results.params).any():
                raise
                
            # figure out which group the current model is in
#            if year in article.GSSYearsUsed: group = 'group1'
#            else: group = 'group2' 
            # if the article used all of the possible data, it's group 1
            # if it didn't use some of the e
		
             
            ########################################################## KEY STEP #######################
            # DEFINE WHICH GROUP THE ESTIMATE WILL GO INTO 
            if year in article.GSSYearsUsed: group = 'group1'
            elif year in article.GSSYearsPossible: group = 'group2'
            else: continue
            
            print 'Year used: ', year
            td[group]['Rs'].append(results.rsquared)
            td[group]['adjRs'].append(results.rsquared_adj)
            td[group]['numTotal'] += len(results.params[1:])
            td[group]['numSig'] += float(len([p for p in results.pvalues[1:] if p < 0.05])) # start at 1 because don't want to count the constant
            td[group]['paramSizesNormed'].append(results.params[1:].abs().mean()) # get the absolute value of the standardized coefficients and take the mean 
            td[group]['pvalues'].append(results.pvalues[1:].mean())
           
            # should need the 2nd condition here because i limited GSSYearsUsed above..
#            elif year in article.GSSYearsPossible and year < max(article.GSSYearsUsed): # the GSS year the models were run on is a "new" year, (wasn't used in article)      
#                    for iv in article.centralIVs:
#                       if iv in col:
#                    coeffsTotalForYearsPossible += 1             
                
    '''
    #only count CENTRAL IVs
    coeffsSigForYearsPossible.extend([el for el in results.pvalues[indicesOfCentralIVs] if el < 0.05]) # start at 1 because don't want to count the constant
    coeffsTotalForYearsPossible += len(article.centralIVs)  
    paramSizesForYearsPossible.extend(results.params[indicesOfCentralIVs])
    '''
                
            
    # if an article's model isn't run on both UNUSED EARLY YEARS and USED years, then skip it        
    if td['group1']['numTotal'] == 0 or td['group2']['numTotal'] == 0: continue
        
    if td['group1']['numTotal'] != 0:
        group = 'group1'
        output[group]['Rs'].append( np.mean(td[group]['Rs'])) 
        output[group]['adjRs'].append(np.mean( td[group]['adjRs'])) 
        output[group]['propSig'].append( td[group]['numSig']/td[group]['numTotal']) 
        output[group]['paramSizesNormed'].append(np.mean( td[group]['paramSizesNormed'])) 
        output[group]['pvalues'].append(np.mean( td[group]['pvalues']))
        output[group]['numTotal'].append(td[group]['numTotal'] / len(td[group]['Rs'])) #divide by len of R^2 array to get a mean of variables estimated PER model 
                      
#        propSigForYearsUsed = float(len(coeffsSigForYearsUsed)) / coeffsTotalForYearsUsed
#        allPropsForYearsUsed.append(propSigForYearsUsed)
#        allParamSizesForYearsUsed.append( np.mean(paramSizesForYearsUsed))
    
    if td['group2']['numTotal'] != 0:
        group = 'group2'
        output[group]['Rs'].append( np.mean(td[group]['Rs'])) 
        output[group]['adjRs'].append(np.mean( td[group]['adjRs'])) 
        output[group]['propSig'].append( td[group]['numSig']/td[group]['numTotal']) 
        output[group]['paramSizesNormed'].append(np.mean( td[group]['paramSizesNormed'])) 
        output[group]['pvalues'].append(np.mean( td[group]['pvalues']))
        output[group]['numTotal'].append(td[group]['numTotal'] / len(td[group]['Rs'])) #divide by len of R^2 array to get a mean of variables estimated PER model 

#        allRsForYearsPossible.append( np.mean(RsForYearsPossible) )
#        propSigForYearsPossible = float(len(coeffsSigForYearsPossible)) / coeffsTotalForYearsPossible
#        allPropsForYearsPossible.append(propSigForYearsPossible)
#        allParamSizesForYearsPossible.append( np.mean(paramSizesForYearsPossible))

 
# should i put a delete command for data here?
'''            
cp.dump(allPropsForYearsPossible, open(pathToData + 'allPropsForYearsPossible.pickle', 'wb'))
cp.dump(allPropsForYearsUsed, open(pathToData + 'allPropsForYearsUsed.pickle', 'wb'))
'''

# The comparisons to make:
# 1. Proportion of coefficients that are significant
from scipy.stats import ttest_ind, ttest_rel
'''
print np.mean(allPropsForYearsUsed), np.mean(allPropsForYearsPossible), 'ttest of Props Sig:', ttest_ind(allPropsForYearsUsed, allPropsForYearsPossible, equal_var=False)
print np.mean(allRsForYearsUsed), np.mean(allRsForYearsPossible), 'ttest of R sizes:', ttest_ind(allRsForYearsUsed, allRsForYearsPossible, equal_var=False)
print np.mean(allParamSizesForYearsUsed), np.mean(allParamSizesForYearsPossible), 'ttest of Param Sizes:', ttest_ind(allParamSizesForYearsUsed, allParamSizesForYearsPossible, equal_var=False)
'''

print 'TTests'
for outcome in outcomes:
    if outcome == 'paramSizes': continue
    print 'Means of group1 and group2:', np.mean(output['group1'][outcome]), np.mean(output['group2'][outcome]), 'Paired T-test of ' + outcome, ttest_rel(output['group1'][outcome], output['group2'][outcome])
