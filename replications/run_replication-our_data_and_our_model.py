
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

# In[73]:

# the article we are running
ARTICLE_ID = 6686


# In[74]:

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


# In[75]:

get_ipython().magic(u'rm ../GSSUtility.pyc # remove this file because otherwise it will be used instead of the updated .py file')
reload(GU)


# In[76]:

pathToData = '../../Data/'
dataCont = GU.dataContainer(pathToData)


# In[77]:

# small_set = [a for a in articlesToUse if 
#              a.articleID in [1651, 1944, 2506, 3567, 3613, 5754]]


# In[78]:

# for article in small_set:
#     print 'id:', article.articleID
#     print 'used:', article.GSSYearsUsed
#     print 'possible:', article.GSSYearsPossible


# In[79]:

# custom_data.astype(float) # doesn't work because stata has files in numerical and string formats, unlike the file I used which was all numerical


# In[80]:

################################
# ANALYSIS

articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=False,                                     centralIVs=False, nextYearBound=0, linearModels=False)            
article = [a for a in articlesToUse if a.articleID == ARTICLE_ID][0]
maxYearUsed = max(article.GSSYearsUsed)

print 'article id:', article.articleID
print
print 'GSS Years Used:', article.GSSYearsUsed
print
print 'DVs:', article.DVs
print
print 'IVs:', article.IVs
print
print 'Controls:', article.controls
print
print 'Central IVs:', article.centralIVs


# In[81]:

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

RHS = article.IVs + article.controls
dfoutput = pd.DataFrame(index=article.DVs)


# In[ ]:




# In[85]:

print 'Running article:', article.articleID

for DV in article.DVs:
    print DV, '~', RHS
#     RHS.remove('AGEWED')

#         futureYearsPossible = [yr for yr in article.GSSYearsPossible if yr > maxYearUsed]
#         nextYear = min(futureYearsPossible) # the arguments of GU.filterArticles function ensure that there is a suitable future year (within bound)

#             log.write('id'+str(article.articleID)+' year '+str(maxYearUsed))

    resOnDataUsed = GU.runModel(dataCont, max(article.GSSYearsUsed), DV, RHS, 
#                                 custom_data=custom_data,
                                standardized=False) # models run on max year of data used
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


# In[86]:

#2506
# dfoutput.loc[['SPKRAC', 'ANTIREL', 'LIBHOMO', 'COLRAC'], :].mean().T
# MARITAL AVG = [6:10].mean()
# race avg = [3:5].mean()
# dfoutput.loc[['FEPOLY', 'FEPRES', 'FEFAM'], :].mean().T
# dfoutput.loc[['HOMOSEX', 'PREMARSX', 'XMARSEX'], :].mean().T
# dfoutput.loc[['NATENVIR','NATHEAL','NATEDUC', 'NATSOC'], :].mean().T
# dfoutput.loc[['NATRACE', 'NATCITY', 'NATFARE'], :].mean().T
# dfoutput.loc[['COMMUN', 'CHINA', 'RUSSIA'], :].mean().T[3:5].mean()


# In[90]:

dfoutput.iloc[:2,:]


# In[47]:

from scipy.stats import pearsonr
pearsonr([0.359, 0.469], [0.215, 1.166])


# In[29]:

np.mean([0.0089, 0.0124])

