
# coding: utf-8

# In[1]:

#######################
# this is an improvement over the code: GSSproject/Code/DEPRECATED--get-random-articles-from-articleClasses-pickle.py

# can use this code to give data to Julianna St Onge (UChicago RA). for example, per email from James Evans 2016-05-22


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


# In[3]:

pathToData = '../Data/'
articleClasses = cp.load(open(pathToData + 'articleClasses.pickle', 'rb'))


# In[4]:

def filterArticles(articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, unusedGSSYears=False, noIVs=True, noDVs=True,                     centralIVs=True, nextYearBound=0, yearPublished=False, linearModels=True, GSSCentralVariable=False):
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
            
        # if the article survived all of the checks above, add it to the list
        indicesToKeep.append(ind)
    
    return [articleClasses[ind] for ind in indicesToKeep] # return elements that have survived
                                                            # the filtering


# In[5]:

# note, nextYearBound = 40 essentially requires that there's at least one future year
articlesToUse = filterArticles(articleClasses, GSSYearsUsed=True, GSSYearsPossible=True,                                     centralIVs=True, nextYearBound=40, linearModels=False)        

suitable_articles = []
for article in articlesToUse:
    maxYearUsed = max(article.GSSYearsUsed)
    futureYearsPossible = [yr for yr in article.GSSYearsPossible if yr > maxYearUsed]
    suitable_articles.append( (article.articleID, futureYearsPossible) )  
    
sample_i = sample(suitable_articles, 50)


# In[6]:

', '.join([str(el[0]) for el in sample_i])


# In[7]:

# code below is used to give data to Julianna, where it's clear which articles use regression models and which don't
# per email with James Evans 2016-05-22. but note that i'm using model==linear_nonlinear, and it's not clear that this is 
# the model type that designates regressions...


# In[8]:

all_articles = [a.articleID for a in filterArticles(articleClasses, 
                                  GSSYearsUsed=True, 
                                  GSSYearsPossible=False, 
                                  centralIVs=False, 
                                  nextYearBound=0, 
                                  linearModels=False)]

linear_articles = [a.articleID for a in filterArticles(articleClasses, 
                                  GSSYearsUsed=True, 
                                  GSSYearsPossible=False, 
                                  centralIVs=False, 
                                  nextYearBound=0, 
                                  linearModels=True)]


# In[9]:

data = []
for a in all_articles:
    data.append([a, True if a in linear_articles else False])

all_articles = pd.DataFrame(data, columns=['true_article_id', 'uses_linear_models'])


# In[10]:

titles = pd.read_csv('../Data/true_article_id_name_year_title_ALL.csv', index_col=0)
titles.index = titles.true_article_id
titles.head()


# In[11]:

all_articles_and_titles = pd.merge(left=all_articles, right=titles, on='true_article_id')


# In[25]:

file_articles_from_next = open('minianalysis_next_year/minianalysis_next_year_list_of_articles_used.csv', 'rb').read()
articles_from_next = map(int, file_articles_from_next.split(','))

file_articles_from_cognate = open('minianalysis_cognate_variables/minianalysis_cognate_variables_list_of_articles_used.csv', 'rb').read()
articles_from_cognate = map(int, file_articles_from_cognate.split(','))

file_articles_from_x_years = open('minianalysis_last_year_used_vs_x_years_into_future/minianalysis_x_years_list_of_articles_used.csv', 'rb').read()
articles_from_x_years = map(int, file_articles_from_x_years.split(','))


# In[26]:

all_articles_and_titles['used_in_last_vs_next'] = False
all_articles_and_titles.loc[all_articles_and_titles.true_article_id.isin(articles_from_next), 'used_in_last_vs_next'] = True

all_articles_and_titles['used_in_cognate'] = False
all_articles_and_titles.loc[all_articles_and_titles.true_article_id.isin(articles_from_cognate), 'used_in_cognate'] = True

all_articles_and_titles['used_in_x_years_into_future'] = False
all_articles_and_titles.loc[all_articles_and_titles.true_article_id.isin(articles_from_x_years), 'used_in_x_years_into_future'] = True


# In[27]:

all_articles_and_titles


# In[28]:

all_articles_and_titles.to_csv('../Data/all_articles_linear_models_and_titles.csv', index=False)

