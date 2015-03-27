'''
from __future__ import division
import cPickle as cp
import pandas as pd
import savReaderWriter as srw
import numpy as np
import statsmodels.formula.api as smf 
import random, sys
'''
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
# Part 1 complete.
'''


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
article = [a for a in articleClasses if a.articleID == 715][0]

if len(article.centralIVs) < 1: 
    print 'No "central" IVs. Skipping'
    raise Exception
    
variables = article.IVs + article.DVs 
variables.append('RACE')

yearsToTry = random.sample(article.GSSYearsPossible, 3)
print yearsToTry
yearsUsed = article.GSSYearsUsed
#design = df.loc[1973, variables].copy(deep=True)  # Need to make a deep copy so that original df isn't changed
design = pd.concat([df.loc[yearsToTry[0], variables], df.loc[yearsToTry[1], variables], df.loc[yearsToTry[2], variables]]).copy(deep=True)  # Need to make a deep copy so that original df isn't changed
#design = pd.concat([df.loc[1977, variables], df.loc[1978, variables], df.loc[1980, variables]]).copy(deep=True)  # Need to make a deep copy so that original df isn't changed

for col in design.columns:
    if len(design[col].unique()) == 1:
        print col # if any IVs or controls constant, drop 'em
        design.drop(col, axis=1)

# remove missing values
print design.shape
for col in design.columns:
    mv = MISSING_VALUES_DICT[col]
    if 'values' in mv:
        design[col].replace(mv['values'], [np.nan]*len(mv['values']), inplace=True) # it's important to have inPlace=True
    # !!! need to insert the other case heer, where the missing values are in a RANGE with 'higher' and 'lower' bounds
#design = design.dropna(axis=0) # drop all rows with any missing values (np.nan)        
print design.shape
   
# skip if there's not enough data after deleting rows
if design.shape[0] < design.shape[1]: # if number of rows is less than number of columns
    print 'Not enough IV/control data. Skipping...'
    raise Exception
'''        
# recode 
design['SEX'][design['SEX']==2] = 0  # MALE = 1, FEMALE = 0

design['RACE'][design['RACE']==2] = 0 #BLACK = 0, WHITE =1, NO WORD ABOUT 'OTHER'...
design['RACE'][design['RACE']==3] = np.nan
design['XNORCSIZ'] = 8 - design['XNORCSIZ']
design['REGION'].replace([1,2,4,3,5,6,7,8,9], [0,0,0,0,1,1,1,0,0], inplace=True) # nonsouth = 0, south = 1
design['RELITEN'].replace([1,2,3, 4, 8, 9], [0,0,1, np.nan, np.nan, np.nan], inplace=True)
design['MEMCHURH'][design['MEMCHURH']==2]=0
design['DRINK'][design['DRINK']==2]=0 # don't drink = 0, drink = 1
design['DRUNK'][design['DRUNK']==2]=0 # don't drink = 0, drink = 1

print 'drop nonblack/white'
#design = design.dropna(axis=0) # drop all rows with any missing values (np.nan)        
print design.shape

libProt = design[design['RELIG']==1]
libProt = libProt[libProt['DENOM'].isin([30, 31, 32, 33, 34, 35, 38, 40, 41, 42, 43, 48, 50])] # lutheran, presby, episcopalians
consProt = design[design['RELIG']==1]
consProt = consProt[consProt['DENOM'].isin([10, 11, 12, 13, 14, 15, 18, 20, 21, 22, 23, 28])] #methodist, baptists, ..members of other protestant sects??
catholic = design[design['RELIG']==2] # lutheran, presby, episcopalians
jewish = design[design['RELIG']==3]
nonaffil = design[design['RELIG']==4]
'''

 # create formula
formula = 'DRINK ~ AGE + C(SEX) + C(RACE) + XNORCSIZ + C(REGION) + INCOME + EDUC + C(RELITEN) + ATTEND + C(MEMCHURH) + C(DENOM) + C(RELIG)'
#formula = 'DRINK ~ AGE + SEX + RACE + XNORCSIZ + REGION + INCOME + EDUC + RELITEN + ATTEND + MEMCHURH'

# estimate and print results
results = smf.ols(formula, data=design).fit()
print results.summary()