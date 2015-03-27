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
articleClasses = cp.load(open(pathToData + 'articleClasses.pickle', 'rb'))

article = [a for a in articleClasses if a.articleID == 5226][0]

variables = article.IVs + article.DVs + article.controls

#yearsToTry = random.sample(GSS_YEARS, 10)
#design = df.loc[1978:1988, variables].copy(deep=True)  # Need to make a deep copy so that original df isn't changed
design = pd.concat([df.loc[year, variables] for year in article.GSSYearsUsed]).copy(deep=True)  # Need to make a deep copy so that original df isn't changed

for col in design.columns:
    if len(design[col].unique()) == 1:
        print col # if any IVs or controls constant, drop 'em
        design.drop(col, axis=1)


# remove missing values
for col in design.columns:
    mv = MISSING_VALUES_DICT[col]
    if 'values' in mv:
        design[col].replace(mv['values'], [np.nan]*len(mv['values']), inplace=True) # it's important to have inPlace=True
    # !!! need to insert the other case heer, where the missing values are in a RANGE with 'higher' and 'lower' bounds
    print design.shape
#design = design.dropna(axis=0) # drop all rows with any missing values (np.nan)        
            
# skip if there's not enough data after deleting rows
if design.shape[0] < design.shape[1]: # if number of rows is less than number of columns
    print 'Not enough IV/control data. Skipping...'
    raise Exception


#* NEED VARIABLE FOR AGE OF RESIDENCE AT 16!!!

# create index
#wellbeing = design['HAPPY']+design['SATCITY']+design['SATHOBBY']+design['SATFAM']+design['SATFIN']+design['SATFRND']+design['SATHEALT']            
#design['WELLBEING'] = pd.Series(wellbeing, index=design.index)

# create formula
formula = 'XNORCSIZ ~ C(SEX) + C(RACE) + AGE + C(MARITAL) + EDUC + FINRELA'

# estimate and print results
results = smf.ols(formula, data=design).fit()
print results.summary()
