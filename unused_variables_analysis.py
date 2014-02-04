# -*- coding: utf-8 -*-
"""
Created on Sun Dec 01 17:55:07 2013

@author: Misha
"""

#unused variables analysis


# IMPORTS #############################
# add GSS Project/Code directory to module search path, just in case
#import sys
#sys.path.append('c:/users/misha/dropbox/gss project/code/')
#from articleClass import *
import cPickle as cp
from collections import Counter

# GLOBALS
GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 
			1980, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 
			1990, 1991, 1993, 1994, 1996, 1998, 
			2000, 2002, 2004, 2006, 2008, 2010, 2012]
pathToData = 'C:/Users/Misha/Dropbox/GSS Project/Data/'  
   
# LOAD DATA ###########################
ALL_VARIABLE_NAMES = cp.load(open(pathToData + 'ALL_VARIABLE_NAMES.pickle'))
varsinarticle = cp.load(open(pathToData + 'VARS_IN_ARTICLE-9-20-2013.pickle', 'rb')) # load the variables used
articleIDAndGSSYearsUsed = cp.load(open(pathToData + 'articleIDAndGssYearsUsed-cleaned.pickle')) # load the years used
varsbyyear = cp.load(open(pathToData + 'VARS_BY_YEAR.pickle', 'rb')) # key=year, value=set('VAR1', 'VAR2', ...)
YEAR_INDICES = cp.load(open(pathToData + 'YEAR_INDICES.pickle'))
VAR_INDICES = cp.load(open(pathToData + 'VAR_INDICES.pickle'))

gssvariablelinks = cp.load(open(pathToData + 'gss_variable_links_article_id_variable.pickle'))

from collections import defaultdict
varsinarticle = defaultdict(list)

for line in gssvariablelinks:
    varsinarticle[line[0]].append(line[1])
dummy = varsinarticle.pop(0)


#alldvs = Counter(sum([a['dvs'] for a in varsinarticle.itervalues()]))
#allivs = Counter(sum([a['ivs'] for a in varsinarticle.itervalues()]))
#allcontrols = Counter(sum([a['controls'] for a in varsinarticle.itervalues()]))
allvars = reduce(set.union, varsbyyear.values())
#allusedvars = alldvs + allivs + allcontrols
allusedvars = Counter(sum(varsinarticle.values()))
allunusedvars = allvars - set(allusedvars) 

fin = open( 'c:/users/misha/dropbox/GSS Project/data/VARS_BY_APPEARANCES_IN_GSS_DATASETS.pickle', 'rb')
varsinsurveys = cp.load(fin)
fin.close()

corevars = [el[0] for el in varsinsurveys.items() if el[1] > 25] # >25 --> 164 vars

infrequentlyusedvars = [el[0] for el in allusedvars.items() if el[1] == 1]

