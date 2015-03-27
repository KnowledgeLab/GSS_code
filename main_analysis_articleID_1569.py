"""

filename: main_analysis_pandas_version.py

description:


inputs:

outputs:

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
      
 - Need to run the apprporiate models for different variable types
     - For binary dependent, do logistic
     - Split categorical IVs into dummies
     - Don't need to make any changes to ordinal IVs?
     
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



GSSFilename = 'GSS Dataset/GSS7212_R2.sav'
#data = srw.SavReader(pathToData + GSSFilename)
#df = pd.DataFrame(data.all(), index=data[:,0], columns=ALL_VARIABLE_NAMES)
#data.close()

#with data:  # this makes sure the file will be closed, memory cleaned up after the program is run
#data = np.array(data.all()) # this makes sure the entire dataset is loaded into RAM, which makes accessing much faster
   
# NEED TO PUT A SECTION/FUNCTION HERE THAT DOES ALL THE FILTERING IN ONE PLACE, SO THAT BY THE TIME
# THE CODE GETS TO articleClasses, it only works on a subset it can actually process



#for article in random.sample(articleClasses, 50):
#for article in articleClasses:
article = [a for a in articleClasses if a.articleID == 1569][0]

if len(article.centralIVs) < 1: 
    print 'No "central" IVs. Skipping'
    raise Exception
    
variables = article.IVs + article.DVs 
#variables.remove('LIFE')
yearsToTry = random.sample(article.GSSYearsPossible, 2)
print yearsToTry
#design = df.loc[1978:1988, variables].copy(deep=True)  # Need to make a deep copy so that original df isn't changed
#design = pd.concat([df.loc[1972, variables], df.loc[1975, variables]]).copy()  # Need to make a deep copy so that original df isn't changed
design = pd.concat([df.loc[yearsToTry[0], variables], df.loc[yearsToTry[1], variables]]).copy()  # Need to make a deep copy so that original df isn't changed


for col in design.columns:
    if len(design[col].unique()) == 1:
        print col # if any IVs or controls constant, drop 'em
        design.drop(col, axis=1)

# remove missing values
print design.shape
print design.RELIG.unique()
for col in design.columns:
    mv = MISSING_VALUES_DICT[col]
    if 'values' in mv:
        design[col].replace(mv['values'], [np.nan]*len(mv['values']), inplace=True) # it's important to have inPlace=True
    # !!! need to insert the other case heer, where the missing values are in a RANGE with 'higher' and 'lower' bounds
design['RELIG'][design['RELIG'] > 2] = np.nan # don't care about all denominations other than protestant =1, catholic=2
#design = design.dropna(axis=0) # drop all rows with any missing values (np.nan)        
print design.shape
print design.RELIG.unique()
            
# skip if there's not enough data after deleting rows
if design.shape[0] < design.shape[1]: # if number of rows is less than number of columns
    print 'Not enough IV/control data. Skipping...'
    raise Exception
        
# recode 
for col in article.DVs:
    design[col].replace([1,2], [2,1], inplace=True)
    
design['RACE'][design['RACE'] != 1] = 0
design['CHLDIDEL'].replace([6, 7, 8], [5, 5, 5], inplace=True)
design['RELIG'].replace([1,2], [0,1])
# create index
abIndex = sum([design[DV] for DV in article.DVs])
design['ABINDEX'] = pd.Series(abIndex, index=design.index)

# create formula
formula = 'ABINDEX ~ CHLDIDEL + EDUC + AGE + C(RELIG) + ATTEND + C(SEX) + C(RACE) + SRCBELT'

# estimate and print results
results = smf.ols(formula, data=design).fit()
print results.summary()