# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Minianalysis: Did not use all available data
# 
# Notes
# --
# Here I tried putting the output of the estimated models into a Pandas dataframe. During this exercise I discovered that Pandas is very bad at the situation when its elements are lists. And the two groups of observations (models run on year used, and year unused-but-available) have different numbers of model-runs in them, because the two numbers of years are usually not equal). So I averaged over DVs *and* years and put the overall average as the value for the group for a given article. This seems suboptimal, especially averaging over DVs part.
# 
# Conclusions
# --
# As the figure of Output shows, the differences are miniscule, and in the "unexpected" direction. So, I'm stopping this minianalysis here for now. (9/9/2014).

# <codecell>

import pandas as pd

from __future__ import division
#import cPickle as cp
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
#from GSSUtility import *

# <codecell>


# <codecell>

"""

filename: minianalysis__did_not_use_all_available_data.py

description: Compare models run on data used and on earlier data not used
inputs:

outputs:

@author: Misha

"""

if __name__ == "__main__":    
    
    pathToData = '../../Data/'
    dataCont = GU.dataContainer(pathToData)
    
    # group1 = models run on original data   
    # group2 = models run on unused data (but available at time of publication)
    groups = ['group1', 'group2']    
    outcomes = ['%_of_coeffs_signif.', 'avg_coeff_size', 'Rs', 'adj_Rs', 'avg_p-value']

    output = pd.DataFrame(columns=pd.MultiIndex.from_product([outcomes, groups]), dtype=float)
#     output = output.astype(object)
#     output.columns
    articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=True, \
                                      unusedGSSYears=True, centralIVs=False)            
#     for article in random.sample(articlesToUse, 10):
    for article in articlesToUse:
    #for article in [a for a in articleClasses if a.articleID == 6755]:
    
        print 'Processing article No.', article.articleID
              
        # define the outcomes I'm interseted in for the two groups. td = "temp data" 
        # and initialize them for both groups
        td = defaultdict(dict)
        for group in groups:             
    #        td[group]['coeffsSig'] = []
            td[group]['numTotal'] = 0.0   
            td[group]['numSig'] = 0.0   # proportions of significant coeffs
    #        td[group]['paramSizes'] = []
            td[group]['avg_coeff_size'] = []
            td[group]['Rs'] = []
            td[group]['adj_Rs'] = []
            td[group]['avg_p-value'] = []
            td[group]['%_of_coeffs_signif.'] = []


        RHS = article.IVs + article.controls

        for DV in article.DVs:            

            # RUN MODELS FROM GROUP 1 ############################################  
            # group 1: models on original data
            group = 'group1'          
            for year in article.GSSYearsUsed:       
                print 'Run models on original data'
                res_orig = GU.runModel(dataCont, year, DV=DV, IVs=RHS)          
                if not res_orig: continue # results will be None if the formula cant be estimated                 
                print DV, '~', ' + '.join(RHS), 'on year', year
                
                # save the (temporary) results                   
                td[group]['Rs'].append(res_orig.rsquared)
                td[group]['adj_Rs'].append(res_orig.rsquared_adj)
                td[group]['numSig'] += float(len([p for p in res_orig.pvalues[1:] if p < 0.05])) # start at 1 because don't want to count the constant
                td[group]['avg_coeff_size'].append(np.mean(np.abs(res_orig.params[1:]))) # get the absolute value of the standardized coefficients and take the mean 
                td[group]['avg_p-value'].append(np.mean(res_orig.pvalues[1:]))
                td[group]['numTotal'] += len(res_orig.params[1:])
                td[group]['%_of_coeffs_signif.'].append( 
                      float(len([p for p in res_orig.pvalues[1:] if p < 0.05])) / len(res_orig.params[1:]) )
            
            # RUN MODELS FROM GROUP 2 ############################################  
            # group2: models run on unused (early) data
            group = 'group2'
            for year in [yr for yr in article.GSSYearsPossible if yr < max(article.GSSYearsUsed)]: # unused early years
                print 'Run models on unused early data'
                res_unused = GU.runModel(dataCont, year, DV=DV, IVs=RHS)                     
                if not res_unused: continue # results will be None if the formula cant be estimated
                print DV, '~', ' + '.join(RHS), 'on year', year

                # save the (temporary) results                   
                td['group2']['Rs'].append(res_unused.rsquared)
                td['group2']['adj_Rs'].append(res_unused.rsquared_adj)
                td['group2']['numSig'] += float(len([p for p in res_unused.pvalues[1:] if p < 0.05])) # start at 1 because don't want to count the constant
                td['group2']['avg_coeff_size'].append(np.mean(np.abs(res_unused.params[-1]))) # get the absolute value of the standardized coefficients and take the mean 
                td['group2']['avg_p-value'].append(np.mean(res_unused.pvalues[1:]))
                td['group2']['numTotal'] += len(res_unused.params[1:])
                td[group]['%_of_coeffs_signif.'].append(
                           float(len([p for p in res_unused.pvalues[1:] if p < 0.05])) / len(res_unused.params[1:]) )
                              
#             # Checks on which results to record                
#             if len(res_orig.params) != len(res_unused.params):
#                 print 'The number of variables in original model is different from the number in cognate model. Skipping.'                    
#                 continue
       
            # The change I'm making is that the block below is now within the for loop
            # of "for DV in article.DVs". So I'm averaging over years but not DVs                    
            # if an article's model isn't run on both group 1 and group 2, skip it        
          
        if td['group1']['numTotal'] == 0  or td['group2']['numTotal'] == 0: continue
            
        for group in groups:      
            for outcome in outcomes:
                output.loc[article.articleID, (outcome, group)] = np.mean(td[group][outcome])
#                 output.loc[article.articleID, ('adj_Rs', group)].append( np.mean( td[group]['adj_Rs']) ) 
#                 output.loc[article.articleID, ('%_of_coeffs_signif.', group)].append( np.mean(td[group]['%_of_coeffs_signif.']) )
#                 output.loc[article.articleID, ('avg_coeff_size', group)].append( np.mean( td[group]['avg_coeff_size']) )
#                 output.loc[article.articleID, ('avg_p-value', group)].append( np.mean( td[group]['avg_p-value']) )
#                 output[group]['numTotal'].append(td[group]['numTotal'] / len(td[group]['Rs'])) #divide by len of R^2 array to get a mean of variables estimated PER model                           
        
        
#     print 'TTests'
#     for outcome in outcomes:
#         print 'Means of group1 and group2:', np.mean(output['group1'][outcome]), np.mean(output['group2'][outcome]), 'Paired T-test of ' + outcome, ttest_rel(output['group1'][outcome], output['group2'][outcome])

#     tempCognateOutput.close()    

# <codecell>

len(articlesToUse)

# <markdowncell>

# #Output

# <codecell>

print output.mean()
output.mean().plot(kind='bar')
# output.boxplot(column='%_of_coeffs_signif.')

# <codecell>

td

# <codecell>

output

# <codecell>

[(o1, 'group1') for o1 in outcomes]`b

# <codecell>

output = pd.DataFrame(columns=pd.MultiIndex.from_product([outcomes, groups]), index=[a.articleID for a in articlesToUse])


# <codecell>

for a in random.sample(articlesToUse, 20):
    print a.GSSYearsUsed, a.GSSYearsPossible

