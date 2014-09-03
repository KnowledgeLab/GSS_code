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
sys.path.append('c:/users/misha/dropbox/gss project/gss_code/')
sys.path.append('c:/users/dj ukrainium/documents/dropbox/gss project/code/')
from GSSUtility import articleClass
import cPickle as cp

# GLOBALS
GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 
			1980, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 
			1990, 1991, 1993, 1994, 1996, 1998, 
			2000, 2002, 2004, 2006, 2008, 2010, 2012]
pathToData = 'c:/users/misha/dropbox/gss project/Data/'  
   
# LOAD DATA ###########################
VARS_IN_ARTICLE = cp.load(open(pathToData + 'VARS_IN_ARTICLE-9-20-2013.pickle', 'rb')) # load the variables used
articleIDAndGSSYearsUsed = cp.load(open(pathToData + 'articleIDAndGssYearsUsed-cleaned.pickle')) # load the years used
VARS_BY_YEAR = cp.load(open(pathToData + 'VARS_BY_YEAR.pickle', 'rb')) # key=year, value=set('VAR1', 'VAR2', ...)
articleIDAndYearPublished = cp.load(open(pathToData + 'articleIDAndYearPublished.pickle'))

maxyear = 0

# CONSTRUCT articleCLasses LIST
articleClasses = []
for articleID in VARS_IN_ARTICLE: # for each article for which we have information on its variables...
    	
    # check if the central variable in the article is from GSS and skip if it's not
    # (GSS_C..V.. is a dict where {article : Bool})
    # 2 conditions in IF statement because need to make sure we have a record for this
    # article first, and then see what the record says
    # I AM GOING TO IGNORE THIS FILTER FOR NOW  
    # if articleID not in GSS_CENTRAL_VARIABLE or not GSS_CENTRAL_VARIABLE[articleID]:continue
    
    # get all variable types for the article 
    IVs =  map(str.upper, VARS_IN_ARTICLE[articleID]['ivs'])
    DVs =  map(str.upper,VARS_IN_ARTICLE[articleID]['dvs'])
    controls =  map(str.upper,VARS_IN_ARTICLE[articleID]['controls'])
    centralIVs = map(str.upper,VARS_IN_ARTICLE[articleID]['centralIVs'])


    # skip articles for whcih we do not have information on GSS years used
    try: oldGSSYears = articleIDAndGSSYearsUsed[articleID]
    except: continue               
    # check to make SURE that the GSS years the article allegedly used contain all the VARIABLES
    # the article allegedly used
    oldGSSYears = [yr for yr in oldGSSYears if set(IVs + DVs + controls + centralIVs).issubset(VARS_BY_YEAR[yr])]   

    unusedGSSYears = set(GSS_YEARS) - set(oldGSSYears) 
    newGSSYears = [yr for yr in sorted(unusedGSSYears) if set(IVs + DVs + controls + centralIVs).issubset(VARS_BY_YEAR[yr])]  

    # some of the entries in the dictionary below are bunk (=0).. where to do the 
    # check for the quality of these? I'll just do it here, I guess
    yearPublished = articleIDAndYearPublished[articleID]
    if yearPublished < 1972 or yearPublished > 2014: yearPublished=None
    
    if yearPublished > maxyear:
        maxyear = yearPublished

    currentArticle = articleClass(articleID, IVs, DVs, controls, centralIVs, oldGSSYears, newGSSYears, yearPublished=yearPublished)
    articleClasses.append(currentArticle)

    
# save the list    
cp.dump(articleClasses, open(pathToData + 'articleClasses.pickle', 'wb'))