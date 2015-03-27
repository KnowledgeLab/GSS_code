"""

filename: main_analysis_dict_of_dataframes.py

description:
FOR NOW (9/27/2013) leaving this alone because read_stata is not converting my categorical variables to their numeric value
and not indexing the DataFrame using index, and I can't figure out why...
     * can use statsmodels.io.foreign.StataReader .. gives intuitive output that's numerical, and uses None instead of np.nan 

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

# Part 1 complete.


# OUTCOMES VARIABLES WE WANT TO MEASURE
allPropsForYearsUsed = []
allPropsForYearsPossible =[]
allParamSizesForYearsUsed = []
allParamSizesForYearsPossible = []
allRsForYearsUsed, allRsForYearsPossible = [], []


# key=year : value= Pandas DataFrame of that year's GSS Stata file
#DICT_OF_DATAFRAMES = cp.load(open(pathToData + 'DICT_OF_DATAFRAMES.pickle'))

# NEED TO PUT A SECTION/FUNCTION HERE THAT DOES ALL THE FILTERING IN ONE PLACE, SO THAT BY THE TIME
# THE CODE GETS TO articleClasses, it only works on a subset it can actually process



for article in random.sample(articleClasses, 50):
#for article in articleClasses:
#for article in [a for a in articleClasses if a.articleID == 118]:

    print 'Processing article:', article.articleID
    
    if len(article.centralIVs) < 1: 
        print 'No "central" IVs. Skipping'
        continue 
    
    # coefficients significant
    coeffsTotalForYearsUsed = 0
    coeffsSigForYearsUsed = []
    coeffsSigForYearsPossible = []
    coeffsTotalForYearsPossible = 0
    
    # proportions of significant coeffs
    propSigForYearsUsed = 0
    propSigForYearsPossible = 0

    # parameter sizes
    paramSizesForYearsUsed = []
    paramSizesForYearsPossible = []
    avgParamSizeForYearsUsed = 0.0
    avgParamSizeForYearsPossible = 0.0
    RsForYearsUsed, RsForYearsPossible = [], []
       
    for year in (article.GSSYearsUsed + article.GSSYearsPossible): # for each GSS year the article used or could've used          
        
       # that year's data 
       df = DICT_OF_DATAFRAMES[year]
       
       for DV in article.DVs: # for each model
            
            # need to time() this step to see if it takes a long time..
            try:            
                design = df[[DV] + article.IVs + article.controls].copy(deep=True)  # Need to make a deep copy so that original df isn't changed
            except:
                print 'GSS for %d did not have one of:' % (year), [DV] + article.IVs + article.controls
                continue
            
            # remove columns that are constant; if DV is constant, skip to next model
            if len(design[DV].unique()) == 1: continue # if DV constant
            for col in design.columns:
                if len(design[col].unique()) == 1: # if any IVs or controls constant, drop 'em. Is this the right step?
                    design.drop(col, axis=1)
            
            ''' Maybe don't need to manually remove MV because they seem to be already substituted with np.nan
            # remove missing values
            for col in design.columns:
                mv = MISSING_VALUES_DICT[col]
                if 'values' in mv:
                    design[col].replace(mv['values'], [np.nan]*len(mv['values']), inplace=True) # it's important to have inPlace=True
                    # there are weird behavior things with np.nan, at the very least when it comes to printing the contents
                    # of a dataframe with np.nan in it.. this may be the cause of very high coefficient estimates i'm seeing..
                # !!! need to insert the other case heer, where the missing values are in a RANGE with 'higher' and 'lower' bounds
            '''
            design = design.dropna(axis=0) # drop all rows with any missing values (np.nan)        
            
            # skip if there's not enough data after deleting rows
            if design.shape[0] < design.shape[1]: # if number of rows is less than number of columns
                print 'Not enough IV/control data. Skipping...'
                continue
            
            # create formula
            formula = DV + ' ~ ' 
            for col in design.columns[1:]: # don't include the DV in the RHS!
                if MEASURE_LEVELS[col] == 'ratio': formula += 'center('+ col + ')'  # only center() if it's a ratio?
                else: formula += ' C(' + col + ')' # i shouldn't center() this?
                formula += ' + '
            formula = formula[:-3] # get rid of the last plus sign
            print formula, ':', year
            
            # can select which formula to use HERE!
            if MEASURE_LEVELS[DV] == 'ratio': results = smf.ols(formula, data=design).fit()
            else: results = smf.ols(formula, data=design).fit()

            if year in article.GSSYearsUsed:                
                RsForYearsUsed.append( results.rsquared )
                for col in results.pvalues.index:
                    for iv in article.centralIVs:
                        if iv in col:
                            coeffsTotalForYearsUsed += 1  
                            paramSizesForYearsUsed.append(abs(results.params[col]))
                            if results.pvalues[col] < 0.05:
                                coeffsSigForYearsUsed.append(results.pvalues[col]) # start at 1 because don't want to count the constant
 
            elif year in article.GSSYearsPossible: # the GSS year the models were run on is a "new" year, (wasn't used in article)      
                RsForYearsPossible.append( results.rsquared )                
                for col in results.pvalues.index:
                    for iv in article.centralIVs:
                        if iv in col:
                            coeffsTotalForYearsPossible += 1  
                            paramSizesForYearsPossible.append(abs(results.params[col]))
                            if results.pvalues[col] < 0.05:
                                coeffsSigForYearsPossible.append(results.pvalues[col]) # start at 1 because don't want to count the constant
                            break
                
                '''
                #only count CENTRAL IVs
                coeffsSigForYearsPossible.extend([el for el in results.pvalues[indicesOfCentralIVs] if el < 0.05]) # start at 1 because don't want to count the constant
                coeffsTotalForYearsPossible += len(article.centralIVs)  
                paramSizesForYearsPossible.extend(results.params[indicesOfCentralIVs])
                '''
                
    if coeffsTotalForYearsUsed != 0:
        allRsForYearsUsed.append( np.mean(RsForYearsUsed) )                
        propSigForYearsUsed = float(len(coeffsSigForYearsUsed)) / coeffsTotalForYearsUsed
        allPropsForYearsUsed.append(propSigForYearsUsed)
        allParamSizesForYearsUsed.append( np.mean(paramSizesForYearsUsed))
    
    if coeffsTotalForYearsPossible != 0:
        allRsForYearsPossible.append( np.mean(RsForYearsPossible) )
        propSigForYearsPossible = float(len(coeffsSigForYearsPossible)) / coeffsTotalForYearsPossible
        allPropsForYearsPossible.append(propSigForYearsPossible)
        allParamSizesForYearsPossible.append( np.mean(paramSizesForYearsPossible))

# should i put a delete command for data here?
            
cp.dump(allPropsForYearsPossible, open(pathToData + 'allPropsForYearsPossible.pickle', 'wb'))
cp.dump(allPropsForYearsUsed, open(pathToData + 'allPropsForYearsUsed.pickle', 'wb'))
