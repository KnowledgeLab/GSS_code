"""
Created on Mon Sep 09, 2013

@author: Misha Teplitskiy

filename: create_articleClasses.py

description: 
 - This script constructs a list of articleClass instances, where each articleClass contains an article's metadata
 - the filtering of the articles is done mostly by filterArticleClasses.py,
 - But I do make the following filters/selections here:
   
     1. gss_central_variable field must be == 'Yes'
     2. no information on GSS years used in the article
     3. make sure the stated GSS years the article used actually contain the variables
         the article allegedly used

- the other filter criteria are performed by filterArticleClasses.py    
 
 
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
pathToData = 'c:/users/misha/dropbox/gss project/Data/'  
   
# LOAD DATA ###########################
ALL_VARIABLE_NAMES = cp.load(open(pathToData + 'ALL_VARIABLE_NAMES.pickle'))
VARS_IN_ARTICLE = cp.load(open(pathToData + 'VARS_IN_ARTICLE-9-20-2013.pickle', 'rb')) # load the variables used
articleIDAndGSSYearsUsed = cp.load(open(pathToData + 'articleIDAndGssYearsUsed-cleaned.pickle')) # load the years used
VARS_BY_YEAR = cp.load(open(pathToData + 'VARS_BY_YEAR.pickle', 'rb')) # key=year, value=set('VAR1', 'VAR2', ...)
YEAR_INDICES = cp.load(open(pathToData + 'YEAR_INDICES.pickle'))
VAR_INDICES = cp.load(open(pathToData + 'VAR_INDICES.pickle'))
GSS_CENTRAL_VARIABLE = cp.load(open(pathToData + 'ARTICLEID_GSS_CENTRAL_VARIABLE.pickle', 'rb'))


# CONSTRUCT articleCLasses LIST
articleClasses = []
for article in VARS_IN_ARTICLE: # for each article for which we have information on its variables...
    	
    # skip articles for whcih we do not have information on GSS years used
    if article not in articleIDAndGSSYearsUsed: continue 
    else: oldGSSYears = articleIDAndGSSYearsUsed[article]
    
    # check if the central variable in the article is from GSS and skip if it's not
    # (GSS_C..V.. is a dict where {article : Bool})
    # 2 conditions in IF statement because need to make sure we have a record for this
    # article first, and then see what the record says
    if article not in GSS_CENTRAL_VARIABLE or not GSS_CENTRAL_VARIABLE[article]:continue
    
    # check whether have all variable types for the article 
    IVs =  map(str.upper, VARS_IN_ARTICLE[article]['ivs'])
    DVs =  map(str.upper,VARS_IN_ARTICLE[article]['dvs'])
    controls =  map(str.upper,VARS_IN_ARTICLE[article]['controls'])
    centralIVs = map(str.upper,VARS_IN_ARTICLE[article]['centralIVs'])

    unusedGSSYears = set(GSS_YEARS) - set(oldGSSYears) 
    newGSSYears = []
    for availableYear in sorted(unusedGSSYears):
        VARS_BY_YEAR[availableYear] 
        if set(IVs + DVs + controls).issubset(VARS_BY_YEAR[availableYear]):  
            newGSSYears.append(availableYear)
     
    # check to make SURE that the GSS years the article allegedly used contain all the VARIABLES
    # the article allegedly used
    oldGSSYears = [year for year in oldGSSYears if set(IVs + DVs + controls).issubset(VARS_BY_YEAR[year])]   
    if len(oldGSSYears) == 0: skip = True # if no years used are left, skip

    currentArticle = articleClass(article, IVs, DVs, controls, centralIVs, oldGSSYears, newGSSYears)
    articleClasses.append(currentArticle)

    
# save the list    
cp.dump(articleClasses, open(pathToData + 'articleClasses.pickle', 'wb'))