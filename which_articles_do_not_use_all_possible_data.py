# -*- coding: utf-8 -*-
"""
description:
This script will see how many studies do not use all the GSS datasets they could've used.
Approach:
 - Look at the latest GSS set the article DID use
 - See if this set of variables was also present in a previous dataset but is not
   captured by GSSYearsUsed
   
Created on Fri Dec 13 18:32:08 2013

@author: Misha
"""
import cPickle as cp
from collections import defaultdict
sys.path.append('../Code/')
from articleClass import *

pathToData = 'C:/Users/Misha/Dropbox/GSS Project/Data/'  
   
# LOAD DATA ###########################
varsinarticle = cp.load(open(pathToData+'varsInArticleFromGssVariableLinks.pickle'))
articleClasses = cp.load(open(pathToData + 'articleClasses.pickle', 'rb'))
# ^ note, this uses the consensus coding idea of what variables are in an article
articleIDAndGSSYearsUsed = cp.load(open(pathToData + 'articleIDAndGssYearsUsed-cleaned.pickle')) # load the years used
varsbyyear = cp.load(open(pathToData + 'VARS_BY_YEAR.pickle', 'rb')) # key=year, value=set('VAR1', 'VAR2', ...)

unusedYears = defaultdict(list)
for article in set(varsinarticle).intersection(articleIDAndGSSYearsUsed):
    
    yearsUsed = articleIDAndGSSYearsUsed[article]
    maxUsed = max(yearsUsed)
    earlierYears = set([y for y in varsbyyear if y < maxUsed])
    unusedEarlierYears = earlierYears.difference(yearsUsed)
    
    if len(unusedEarlierYears):
        for year in unusedEarlierYears:
            if set(varsinarticle[article]).issubset(varsbyyear[year]):
                #print 'Article', article, 'didnt use year', year
                unusedYears[article].append(year)
    
    


