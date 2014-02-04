"""
Created on Mon Sep 09, 2013

@author: Misha Teplitskiy

filename: create_articleClasses.py

description: 
 - This script constructs a list of articleClass instances, where each articleClass contains an article's metadata
 - This is the primary place where I select/filter which articles I want to 
   analyze (run the published models)
   
 - Current filter/selection criteria is the following
     1. gss_central_variable field must be == 'Yes'
     2. no information on GSS years used in the article
     3. must have at least 1 DV and 1 IV
     4. there must be at least one "new" year of data to run the models on
    
 
 
inputs:

outputs:
 - articleClasses.pickle -- this is a list of articleClass instances


"""
# IMPORTS #############################
# add GSS Project/Code directory to module search path, just in case
import sys
sys.path.append('c:/users/misha/dropbox/gss project/code/')
sys.path.append('c:/users/dj ukrainium/documents/dropbox/gss project/code/')
from articleClass import *
import cPickle as cp

# GLOBALS
GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 
			1980, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 
			1990, 1991, 1993, 1994, 1996, 1998, 
			2000, 2002, 2004, 2006, 2008, 2010, 2012]
pathToData = 'c:/users/dj ukrainium/documents/dropbox/gss project/Data/'  
   
# LOAD DATA ###########################
ALL_VARIABLE_NAMES = cp.load(open(pathToData + 'ALL_VARIABLE_NAMES.pickle'))
VARS_IN_ARTICLE = cp.load(open(pathToData + 'VARS_IN_ARTICLE-9-20-2013.pickle', 'rb')) # load the variables used
articleIDAndGSSYearsUsed = cp.load(open(pathToData + 'articleIDAndGssYearsUsed-cleaned.pickle')) # load the years used
VARS_BY_YEAR = cp.load(open(pathToData + 'VARS_BY_YEAR.pickle', 'rb')) # key=year, value=set('VAR1', 'VAR2', ...)
YEAR_INDICES = cp.load(open(pathToData + 'YEAR_INDICES.pickle'))
VAR_INDICES = cp.load(open(pathToData + 'VAR_INDICES.pickle'))
GSS_CENTRAL_VARIABLE = cp.load(open(pathToData + 'ARTICLEID_GSS_CENTRAL_VARIABLE.pickle', 'rb'))

# counter variables to see how many articles get disqualified for the variety of conditions
noNewGSSYears = 0
noDVs, noIVs = 0, 0

# CONSTRUCT articleCLasses LIST
articleClasses = []
for article in VARS_IN_ARTICLE: # for each article for which we have information on its variables...
    	
    # skip articles for whcih we do not have information on GSS years used
    if article not in articleIDAndGSSYearsUsed: continue 
    else: oldGSSYears = articleIDAndGSSYearsUsed[article]
    
    # check whether have all variable types for the article 
    IVs =  map(str.upper, VARS_IN_ARTICLE[article]['ivs'])
    DVs =  map(str.upper,VARS_IN_ARTICLE[article]['dvs'])
    controls =  map(str.upper,VARS_IN_ARTICLE[article]['controls'])
    centralIVs = map(str.upper,VARS_IN_ARTICLE[article]['centralIVs'])
    	
    # skip article if there is no info on DVs or IVs
    # Should we change this to skip only if BOTH controls AND IVs are not there?
    if len(DVs) < 1:
        noDVs+=1
        continue
        
    if len(IVs) < 1: 
        noIVs+=1        
        continue     
     
    ############################################
    # THIS IS A GOOD PLACE TO CHECK IF THE VARIABLES ARE OF THE APPROPRIATE FORM (NUMERIC)?
    ###################################
     
    # check to make SURE that the GSS years the article allegedly used contain all the VARIABLES
    # the article allegedly used
    oldGSSYears = [year for year in oldGSSYears if set(IVs + DVs + controls).issubset(VARS_BY_YEAR[year])]   
    if len(oldGSSYears) == 0: continue # if no years used are left, skip
     
    # Are there years for which analysis is possible but which the article didn't use?
    unusedGSSYears = set(GSS_YEARS) - set(oldGSSYears) 
    newGSSYears = []
    for availableYear in sorted(unusedGSSYears):
        VARS_BY_YEAR[availableYear] 
        if set(IVs + DVs + controls).issubset(VARS_BY_YEAR[availableYear]):  
            newGSSYears.append(availableYear)
            
    # if there is no un-used years of GSS possible to run the data on, then just skip this article
    if len(newGSSYears) < 1: 
        noNewGSSYears+=1        
        continue 
    
    # if GSS is not the central dataset used then skip
    if article not in GSS_CENTRAL_VARIABLE or not GSS_CENTRAL_VARIABLE[article]:  
        continue
    
    # if the article survived all of the checks above add it to the list
    currentArticle = articleClass(article, IVs, DVs, controls, centralIVs, oldGSSYears, newGSSYears)
    articleClasses.append(currentArticle)
    
# save the list    
cp.dump(articleClasses, open(pathToData + 'articleClasses.pickle', 'wb'))