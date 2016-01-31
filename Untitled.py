
# coding: utf-8

# In[2]:

import cPickle as cp
from random import sample
import sys
import pandas as pd
import pickle

sys.path.append('../')    
import GSSUtility as GU
sys.path.append('../Code/')
from articleClass import *


# In[ ]:

pathToData = '../Data/'
articleClasses = cp.load(open(pathToData + 'articleClasses.pickle', 'rb'))


# In[13]:

def filterArticles(articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, unusedGSSYears=False, noIVs=True, noDVs=True,                     centralIVs=False, nextYearBound=0, yearPublished=False, linearModels=False, GSSCentralVariable=False):
    '''
    This function filters the articleClasses list according to the following criteria.
    arguments:
     - noIVs: skip if no IVs specified
     - noDVs: skip if no DVs specified
     - GSSYearsPossible: skip if there are no GSS years possible besides the ones the article used
     - unusedGSSYears=False: If True, then keep only those articles which have some GSS Years they could have used, but didn't
     - centralIV: skip if there is no IV(s) designated as "central"
     - nextYearBound = int: skip if next future year of data is not within "int" of last year used
                     = 0 by default, in which case it's not used
     - yearPublished=False: if set to True, yearPublished is required to be not None
     - GSSCentralVariable=False: if True, keep only those articles where GSSCentralVariable is True in the mysql
                                 table gss_question
     - linearModels=False: if True, keep only those articles where model type is .. and I should think about what to use here.
     - TODO: ADD AN "UNUSED YEARS" filter
    '''
    indicesToKeep = []
    
    pathToData = '../Data/'
    if GSSCentralVariable:
        gssCentral = cp.load(open(pathToData + 'ARTICLEID_GSS_CENTRAL_VARIABLE.pickle', 'rb'))

    if linearModels:
        modelUsed = pd.read_pickle(pathToData + 'ARTICLEID_AND_TRUE_IF_LINEAR_NONLINEAR.pickle')

    for ind, a in enumerate(articleClasses):  # a = article
        
        # skip article if there is no info on DVs or IVs
        # Should we change this to skip only if BOTH controls AND IVs are not there?
        if noDVs:
            if len(a.DVs) < 1: continue
        
        if noIVs: 
            if len(a.IVs) < 1: continue

        if GSSYearsUsed:         
            # if there is no used years of GSS possible to run the data on, then just skip this article
            if len(a.GSSYearsUsed) < 1: continue
            
        if GSSYearsPossible:         
            # if there is no un-used years of GSS possible to run the data on, then just skip this article
            if len(a.GSSYearsPossible) < 1: continue

        if unusedGSSYears:
            unusedEarlyYears = [yr for yr in a.GSSYearsPossible if yr <= max(a.GSSYearsUsed)]
            if len(unusedEarlyYears)==0: continue
            
        if centralIVs:    
            # if GSS is not the central dataset used then skip
            if len(a.centralIVs) < 1: continue
                   
        if nextYearBound:
            # nextYear is an integer that specifies how soon the next available year of data is supposed to be.
            # e.g. if nextYearBound = 4, then the new future year of data is to occur within 4 years of the last year of data
            # actually used. 
            maxYearUsed = max(a.GSSYearsUsed)
            futureYearsPossible = [yr for yr in a.GSSYearsPossible if yr > maxYearUsed]
            if not futureYearsPossible or min(futureYearsPossible) > maxYearUsed + nextYearBound: continue
                   
        if yearPublished:
            if not a.yearPublished: continue
                        
        if GSSCentralVariable:
            if a.articleID not in gssCentral or gssCentral[a.articleID]==False: continue
        
        if linearModels:
            if a.articleID not in modelUsed: continue            
            
            
            
                
        # if the article survived all of the checks above add it to the list
        indicesToKeep.append(ind)
    
    return [articleClasses[ind] for ind in indicesToKeep] # return elements that have survived
                                                            # the filtering


articlesToUse = filterArticles(articleClasses, GSSYearsUsed=True, GSSYearsPossible=True,                                     centralIVs=True, nextYearBound=3, linearModels=True)            


# In[15]:

print sample([int(el.articleID) for el in articlesToUse], 20)


# In[ ]:



