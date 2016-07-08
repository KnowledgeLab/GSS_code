
# coding: utf-8

# ###filename: run_replication.ipynb
# 
# ###description: 
#     last updated: 2016-07-08
#     Run models from an article for the purposes of comparing results to "manual/gold standard" replications by Julianna. 
#     
# 
# ###inputs:
# 
# ###outputs:
# 
# ##TO-DOs:
#     
#     
# @author: Misha
# 

# In[87]:

# the article we are running
ARTICLE_ID = 6686


# In[52]:

from __future__ import division
import pandas as pd
import pickle
import sys
sys.path.append('../')    
import GSSUtility as GU
import numpy as np
import statsmodels.formula.api as smf 
import random
from scipy.stats import pearsonr, ttest_ind, ttest_rel
import time
from collections import Counter
from collections import defaultdict

import matplotlib.pyplot as plt
import seaborn as sb
custom_style = {'axes.facecolor': 'white',
                'grid.color': '0.15',
                'grid.linestyle':'-.'}
sb.set_style("darkgrid", rc=custom_style)


# In[79]:

get_ipython().magic(u'rm ../GSSUtility.pyc # remove this file because otherwise it will be used instead of the updated .py file')
reload(GU)


# In[ ]:




# In[ ]:




# In[80]:

# custom_data.astype(float) # doesn't work because stata has files in numerical and string formats, unlike the file I used which was all numerical


# In[91]:

pathToData = '../../Data/'
dataCont = GU.dataContainer(pathToData)

articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=False,                                     centralIVs=False, nextYearBound=0, linearModels=False)            
print 'len of articleClasses:', len(articlesToUse)
#     raw_input('...')


# define the storage containers for outputs
group1 = 'on last GSS year'
group2 = 'on first "future" GSS year'   
groups = [group1, group2]
outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues',  'numTotal',             'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']

output = defaultdict(dict)
output['metadata'] = {'article_id':[]}
for group in groups:
    for outcome in outcomes:
        output[group][outcome] = []


article = [a for a in articlesToUse if a.articleID == ARTICLE_ID][0]
maxYearUsed = max(article.GSSYearsUsed)

maxYearUsed = 1986

# load custom data
custom_data = pd.read_csv('../../Data/juliana_replications/%d/%d_%d.csv' % (ARTICLE_ID, ARTICLE_ID, 1986), index_col=0)  
custom_data.columns = map(str.upper, custom_data.columns)

custom_data = custom_data.replace({'.i':np.nan, # i should probably check to make sure all these answers are legitimately NaNs
                                   '.a':np.nan, 
                                   '.n':np.nan,
                                   '.d':np.nan,
                                   'dk':np.nan, 
                                   'dk,na,iap':np.nan})

RHS = article.IVs + article.controls

dfoutput = pd.DataFrame(index=article.DVs)


# In[89]:

article.GSSYearsUsed


# In[92]:

print 'Running article:', article.articleID

for DV in article.DVs:
    print DV, '~', RHS
#     RHS.remove('AGEWED')

#         futureYearsPossible = [yr for yr in article.GSSYearsPossible if yr > maxYearUsed]
#         nextYear = min(futureYearsPossible) # the arguments of GU.filterArticles function ensure that there is a suitable future year (within bound)

#             log.write('id'+str(article.articleID)+' year '+str(maxYearUsed))

    resOnDataUsed = GU.runModel(dataCont, maxYearUsed, DV, RHS, custom_data=custom_data, standardize=False) # models run on max year of data used
    if not resOnDataUsed: continue

# #             log.write('id'+str(article.articleID)+' year '+str(nextYear))           
#         resOnNextYear = GU.runModel(dataCont, nextYear, DV, RHS); # models run on min year of future data
#         if not resOnNextYear: continue

#         # Checks on which results to record                
#         if len(resOnDataUsed.params) != len(resOnNextYear.params):
#             print 'The number of variables in original model is different from the number in model on future years. Skipping.'                    
#             continue

    # the condition below means that i don't care about models in which orig var isn't stat. sig.
#            if results.pvalues[-1] > 0.05: continue
#         results = [resOnDataUsed, resOnNextYear]

    centralVars = []            
    for civ in article.centralIVs:
        if civ in resOnDataUsed.params.index:
            centralVars.append(civ)
        else: 
            for col in resOnDataUsed.params.index:
                if 'C(' + civ + ')' in col:
                    centralVars.append(col)

#             print 'IVs:', article.IVs
#             print 'centralVas:', centralVars
#            raw_input('...')
    '''                
    centralVars = ['standardize(%s, ddof=1)' % (cv) for cv in article.centralIVs]
    centralVars = set(centralVars).intersection(results[0].params.index) # need this step because some central                                                                                            # var columns may be removed when running model
    '''

    dfoutput.loc[DV, 'Rs'] = resOnDataUsed.rsquared
    dfoutput.loc[DV, 'adjRs'] = resOnDataUsed.rsquared_adj

    for col in resOnDataUsed.params.index:          
        dfoutput.loc[DV, col] = resOnDataUsed.params[col]


# In[93]:

dfoutput


# In[95]:

article.IVs


# In[ ]:



