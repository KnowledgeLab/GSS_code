
# coding: utf-8

# In[ ]:


# <nbformat>3.0</nbformat>

# <markdowncell>

# filename: cognateVariablesAnalysis.py
# 
# description: Runs models as specified originally and again after replacing a central variable by a cognate var.
# It compares regressions on what was then the new data vs same regressions on future waves
# 
# inputs:
# 
# outputs:
# 
# @author: Misha
# 

# <codecell>

from __future__ import division
import pandas as pd
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

# <codecell>

import seaborn as sb
custom_style = {'axes.facecolor': 'white',
                'grid.color': '0.15',
                'grid.linestyle':'-.'}
sb.set_style("darkgrid", rc=custom_style)

# <codecell>

# TO DO: TRY MEDIAN INSTEAD OF MEAN FOR PERCENT OF CENTRAL VARS STAT SIGN.

if __name__ == "__main__":    
    
    pathToData = '../../Data/'
    dataCont = GU.dataContainer(pathToData)
    
#     tempCognateOutput = open(pathToData + 'tempCognateOutput.txt', 'w')
    
    # contains for storing (variable, cognate) tuples in order to see what substitutions
    #i'm most commonly making
    variableCognateTuples = []
    
    # define the storage containers for outputs
    group1 = 'original model'
    group2 = 'cognate model'   
    groups = [group1, group2]
    outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues',  'numTotal',                 'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']
    output = defaultdict(dict)
    output['metadata'] = {'article_id':[]}
    for group in groups:
        for outcome in outcomes:
            output[group][outcome] = []
            
    
    articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, centralIVs=True) #, 
    print len(articlesToUse)
#                                         linearModels=True)            
#     for article in random.sample(articlesToUse, 200):
    for article in articlesToUse:
    #for article in [a for a in articleClasses if a.articleID == 6755]:
    
        print 'Processing article:', article.articleID

        # let's see if this article is suitable for cognates analysis:
        originalLHS = article.IVs + article.controls
        identifyCognatesReturns = GU.identifyCognates(dataCont, originalLHS, article.centralIVs, article.GSSYearsUsed, corrThreshold=0.6 )        
        if not identifyCognatesReturns: 
            print 'No suitable cognates. Skipping.'            
            continue        
        else: 
            cIV, cognate, GSSYearsWithCognate = identifyCognatesReturns
            
        # if we got this far, then this article does have suitable cognates, so let's estimate models       
        # Now let's estimate the models
        for DV in article.DVs:            
            
            if cognate == DV: continue # sometimes the cognate suggested by GU.identifyCognates is the DV
                
            for year in GSSYearsWithCognate:        

                # group 2 models (with cognates)
                print 'Running cognate models'
                
                cognateLHS = originalLHS[:] # the "[:]" makes a deep copy ?
                cognateLHS.remove(cIV)
                cognateLHS.append(cognate) # need to put it in list otherwise it treats each letter as an element
#                 print 'Substituting', cIV, 'with cognate', cognate
                #time.sleep(2)
                #raw_input('Press Enter')                
                
                result_cog = GU.runModel(dataCont, year, DV, cognateLHS)          
                if not result_cog: continue # results will be None if the formula cant be estimated
#                 print DV, '~', cognateLHS, 'on year', year
                 
                # RUN MODELS FROM GROUP 1 ############################################  
                # group 1
                print 'Running original models.'
                
#                 # make sure cIV is last in the list of variables
                originalLHS.remove(cIV)
                originalLHS.append(cIV) 
    
                result_orig = GU.runModel(dataCont, year, DV, originalLHS)                     
                if not result_orig: continue # results will be None if the formula cant be estimated

                results = [result_orig, result_cog]
                
                # new change, 2015-01-05
                # THIS BLOCK OF CODE BELOW IS ADDED FROM 'MINIANALYSIS__models_on_next_year, 
                centralVars = []            
                for civ in article.centralIVs:
                    if 'standardize(%s, ddof=1)' % (civ) in results[0].params.index:
                        centralVars.append('standardize(%s, ddof=1)' % (civ))
                    else: 
                        for col in results[0].params.index:
                            if 'C(' + civ + ')' in col:
                                centralVars.append(col)          
                                
                # the condition below means that i don't care about models in which orig var isn't stat. sig.
                # A reason for this condition is that if this central variable isn't significant in the original model
                # then the goal of the article may've been to show that this variable DOESN'T matter. In such a "negative" case,
                # what does replacing it with a cognate accomplish?

                # old condition below
#                 if result_orig.pvalues[-1] > 0.05: continue
                # new condition below
#                 if np.all(results[0].pvalues[centralVars] > 0.05): 
#                     print 'All "central" IVs are p > 0.05. Skipping.'
#                     continue                
                
                # Checks on which results to record                
                if len(result_cog.params) != len(result_orig.params):
                    print 'The number of variables in original model is different from the number in cognate model. Skipping.'                    
                    continue

                    
# ###########################################################################################                
# new way of saving results
# new change, 2015-01-05
# THIS BLOCK OF CODE BELOW IS ADDED FROM 'MINIANALYSIS__models_on_next_year,                    
                for i in range(2):                 
                    output[groups[i]]['Rs'].append(results[i].rsquared) 
                    output[groups[i]]['adjRs'].append(results[i].rsquared_adj) 
                    output[groups[i]]['propSig'].append(float(len([p for p in results[i].pvalues[1:] if p < 0.05]))/len(results[i].params[1:])) 
                    output[groups[i]]['paramSizesNormed'].append(np.mean(results[i].params[1:].abs())) 
                    output[groups[i]]['pvalues'].append(np.mean( results[i].pvalues[1:]))
                    output[groups[i]]['numTotal'].append( 1 ) #divide by len of R^2 array to get a mean of variables estimated PER model                           

                    if len(centralVars)>0:
                        output[groups[i]]['pvalues_CentralVars'].append(np.mean(results[i].pvalues[centralVars]))               
                        output[groups[i]]['propSig_CentralVars'].append(float(len([p for p in results[i].pvalues[centralVars] if p < 0.05]))                                                                 /len(results[i].params[centralVars])) 
                        output[groups[i]]['paramSizesNormed_CentralVars'].append(np.mean(results[i].params[centralVars].abs()))                
                    else:
                        output[groups[i]]['pvalues_CentralVars'].append(nan)               
                        output[groups[i]]['propSig_CentralVars'].append(nan) 
                        output[groups[i]]['paramSizesNormed_CentralVars'].append(nan)                
                
                output['metadata']['article_id'].append(article.articleID)    


# ########################################################################################                
# ## this is the old ways of saving results.. now i'm doing it the way "models_on_next_year" does it
    
#                 for i in range(2):
#                     # save the results                   
#                     td[groups[i]]['Rs'].append(results[i].rsquared)
#                     td[groups[i]]['adjRs'].append(results[i].rsquared_adj)
#                     td[groups[i]]['numTotal'] += len(results[i].params[1:])
#                     td[groups[i]]['numSig'] += float(len([p for p in results[i].pvalues[1:] if p < 0.05])) # start at 1 because don't want to count the constant
#                     td[groups[i]]['paramSizesNormed'].append(abs(results[i].params[-1])) # get the absolute value of the standardized coefficients and take the mean 
#                     td[groups[i]]['pvalues'].append(results[i].pvalues[-1])
               
#                     td[groups[i]]['pvalues_CentralVars'].append(np.mean(results[i].pvalues[centralVars]))               
#                     td[groups[i]]['propSig_CentralVars'].append(float(len([p for p in results[i].pvalues[centralVars] if p < 0.05])) \
#                                                             /len(results[i].params[centralVars])) 
#                     td[groups[i]]['paramSizesNormed_CentralVars'].append(np.mean(results[i].params[centralVars].abs()))                

                

# # # #                 print >> tempCognateOutput, 'Orig:\t', cIV, '\t\tCogn:\t', cognate, '\t\t Coeffs:\t', results.params[-1], results.pvalues[-1],resultsCognate.params[-1], resultsCognate.pvalues[-1] 
            
            
            
#             # The change I'm making is that the block below is now within the for loop
#             # of "for DV in article.DVs". So I'm averaging over years but not DVs   
            
#             # if an article's model isn't run on both group 1 and group 2, skip it        
#             if td[group1]['numTotal'] == 0 or td[group2]['numTotal'] == 0: continue
          
#             variableCognateTuples.append((cIV, cognate))
#             for group in groups:      
#                 output[group]['Rs'].append( np.mean(td[group]['Rs'])) 
#                 output[group]['adjRs'].append(np.mean( td[group]['adjRs'])) 
#                 output[group]['propSig'].append( td[group]['numSig']/td[group]['numTotal']) 
#                 output[group]['paramSizesNormed'].append(np.mean( td[group]['paramSizesNormed'])) 
#                 output[group]['pvalues'].append(np.mean( td[group]['pvalues']))
#                 output[group]['numTotal'].append(td[group]['numTotal'] / len(td[group]['Rs'])) #divide by len of R^2 array to get a mean of variables estimated PER model                           

#                 output[group]['pvalues_CentralVars'].append(np.mean(td[group]['pvalues_CentralVars']))               
#                 output[group]['propSig_CentralVars'].append(np.mean(td[group]['propSig_CentralVars'])) 
#                 output[group]['paramSizesNormed_CentralVars'].append(np.mean(td[group]['paramSizesNormed_CentralVars']))                

#             output['metadata']['article_id'].append(article.articleID)   
        


#     print 'TTests'
#     for outcome in outcomes:
#         print 'Means of group1 and group2:', np.mean(output[group1][outcome]), np.mean(output[group2][outcome]), 'Paired T-test of ' + outcome, ttest_rel(output[group1][outcome], output[group2][outcome])

#     tempCognateOutput.close()    

# <markdowncell>

# Create a Pandas DataFrame of the output
# --

# <codecell>

df_output = pd.DataFrame(index=arange(len(output[group1]['propSig'])), columns=pd.MultiIndex.from_product([groups, outcomes]))
df_output.columns.names = ['outcome','group']
for outcome in outcomes:
    for gp in groups:
        df_output[gp, outcome] = output[gp][outcome]
df_output.index = output['metadata']['article_id']
del df_output[group1, 'numTotal']
del df_output[group2, 'numTotal']
print 'Using %f models from %f articles' % (len(df_output), len(df_output.index.unique()))

# <markdowncell>

# #Plot outcomes - (new) distribution of differences approach

# <codecell>

outcomeMap = {'propSig':"% of Stat. Sign. Coeff's", 
              'paramSizesNormed':"Standard. Size of Coeff's",
              'Rs':'R-squared', 
              'adjRs':'Adj. R-squared',
              'pvalues':"Avg. P-Value of Coeff's",
              'propSig_CentralVars':"Cent. Var's: % of Stat. Sign. Coeff's",
              'paramSizesNormed_CentralVars':"Cent. Var's: Standard. Size of Coeff's", 
              'pvalues_CentralVars':"Cent. Var's: Avg. P-Value of Coeff's"}

for outcome in outcomes:
    if outcome=='article_id': continue
    if outcome=='numTotal':continue
    
    figure(figsize=(4,4))
    xticks(fontsize=12)
    yticks(fontsize=15)
    ylabel('Density', fontsize=17)

    title(outcomeMap[outcome], fontsize=20)
    print outcome + 'Group 1, Mean: %0.3f, s.d.: %0.3f' %         (df_output[group1, outcome].mean(), df_output[group1, outcome].std()/np.sqrt(len(df_output)))
    print outcome + 'Group 2, Mean: %0.3f, s.d.: %0.3f' %         (df_output[group2, outcome].mean(), df_output[group2, outcome].std()//np.sqrt(len(df_output)))
 
    sb.kdeplot((df_output[group1, outcome] - df_output[group2, outcome]), 
                color='black', legend=False)
#     sns.kdeplot(df2_output[outcome].dropna(), shade=False, color='blue', legend=False)

#     if '%' in outcomeMap[outcome] or 'P-value' in outcomeMap[outcome] or 'Size' in outcomeMap[outcome]:
#         xlim((0,1))
#     elif 'R-' in outcomeMap[outcome]:
#         xlim(0,0.6)
#     else:
#         xlim(0, 1.05*df_output[outcome].max())
#     #     df_output[outcome].dropna().plot(kind='kde', color='black', linewidth=3)

#     df_output[outcome].hist(bins=30)
#     savefig('../../Images/descriptives--' + outcome + '.svg', bbox_inches='tight')
    
    plot([0,0], [0,20], '--', color='black', linewidth=2)
    
#     break

# <markdowncell>

# #Plot outcomes - (old) bar chart approach

# <codecell>

figsize(12,8)
outcomesToUse = df_output[group1].columns
indices = np.arange(len(outcomesToUse))
width = 0.35
error_config = {'ecolor': '0.3'}

axes = figure().add_subplot(111)
rects1 = bar(left=indices, width=width, height=df_output[group1].mean(), color='0.75', 
             yerr=df_output[group1].std()/np.sqrt(len(df_output[group1])),
             error_kw=error_config) #this is not very relevant because we're not comparing independent groups
rects2 = bar(left=indices+width, width=width, height=df_output[group2].mean(), color='0.5', 
             yerr=df_output[group2].std()/np.sqrt(len(df_output[group2])),
             error_kw=error_config)

# title, legend, etc
title('Original vs. Cognate Models', fontsize=18)
legend((rects1[0], rects2[0]), ('Original models', 'Cognate models'), fontsize=15)
# legend((rects1[0], rects2[0]), ('Original models', 'Cognate models'), fontsize=15)
xlim((-1*width, len(outcomesToUse)))

# tick labels
# a = outcomesToUse
a = ['% of coeffs. stat. sign.', 'avg. coeff. size', 'R_sq.', 'adj. R_sq.', 'avg. p-value',      '"central" vars: % of coeffs. stat. sign.', '"central" vars: avg. coeff. size', '"central" vars: avg. p-value']
axes.set_xticks(indices+width)
axes.set_xticklabels(a, rotation=90, fontsize=15)

# label the bars with the difference between them
diffs = (df_output[group1] - df_output[group2]).mean().values
def autolabel(rects):
    # attach some text labels
    for i, rect in enumerate(rects):
        height = rect.get_height()
        if i!=7 and i!=4:
            axes.text(rect.get_x()+width, 1.03*height, '%0.3f'%diffs[i],
                    ha='center', va='bottom', fontsize=15)
        else: # this is for the p-value label, which has gone up
            axes.text(rect.get_x()+width, 1.03*height+0.05, '%0.3f'%diffs[i],
                    ha='center', va='bottom', fontsize=15)
autolabel(rects1)

####################################
# OLD PLOTTING CODE
# savefig('../../Images/ASA2015/original_vs_cognate_models.png', bbox_inches='tight')

# THE CODE BELOW IS OLD -- I replaced it with the code above on 2015-01-06
# figsize(5,5)

# indices = np.arange(5)
# width = 0.35
# axes = figure().add_subplot(111)
# rects1 = bar(left=indices, width=width, height=df_output['orig. models'].mean(), color='r')#, yerr=df_output['orig. models'].std()) #this is not relevant because we're not comparing groups
# rects2 = bar(left=indices+width, width=width, height=df_output['cognate models'].mean(), color='y')#, yerr=df_output['cognate models'].std())

# # title, legend, etc
# title('Original vs. Cognate Models', fontsize=18)
# legend((rects1[0], rects2[0]), ('Original models', 'Cognate models'), fontsize=15)
# xlim((-1*width, 5))

# # tick labels
# a = ['% of coeffs. stat. sign.', 'stand. coeff. size', 'R_sq.', 'adj. R_sq.', 'p-value']
# axes.set_xticks(indices+width)
# axes.set_xticklabels(a, rotation=80, fontsize=15)

# # label the bars with the difference between them
# diffs = (df_output['orig. models'] - df_output['cognate models']).mean().values
# def autolabel(rects):
#     # attach some text labels
#     for i, rect in enumerate(rects):
#         height = rect.get_height()
#         if i!=4:
#             axes.text(rect.get_x()+width, 1.02*height, '%0.3f'%diffs[i],
#                     ha='center', va='bottom')
#         else: # this is for the p-value label, which has gone up
#             axes.text(rect.get_x()+width, 1.02*height+0.05, '%0.3f'%diffs[i],
#                     ha='center', va='bottom')
# autolabel(rects1)

# savefig('../../Images/9-10-2014--original_vs_cognate_models.png', bbox_inches='tight')

# <markdowncell>

# #Examine a particular outcome
# Examine the differences distribution

# <codecell>

figsize(6,5)
(df_output['orig. models']['paramSizesNormed'] - df_output['cognate models']['paramSizesNormed']).plot(kind='kde')
plot([0,0], [0,20], '--')
title('Differences in Stand. Coeff. Size. between orig. and cognate')

# <codecell>

mn= np.mean((df_output['orig. models', 'Rs'] - df_output['cognate models', 'Rs']).values)
sd= np.std((df_output['orig. models', 'Rs'] - df_output['cognate models', 'Rs']).values)
print mn, sd, mn/(sd/sqrt(df_output.shape[0]))

# <markdowncell>

# Perform t-tests and Tests using *clustered errors*
# --
# 
# 1. Perform related-sample t-test (samples must be of equal lengths)
# 
# 2. Perform independent samples t-test (just for kicks, to see how big our effects are)
# 
# 3. Perform clustered error tests. To do this I will do a hack by running a regression with clustered errors and using that as the t-test. Source/inspiration is: http://www.stata.com/statalist/archive/2010-05/msg00663.html
# 
# Note: I am not using the 'df_correction' flag in get_robustcov_results() because that's apparently something HLM does, not canonical clustered errors:
# "This method of correcting the standard errors to account for the intraclass correlation is a "weaker" form of correction than using a multilevel model, which not only accounts for the intraclass correlation, but also corrects the denominator degrees of freedom for the number of clusters."
# source: http://www.ats.ucla.edu/stat/stata/library/cpsu.htm
# 
# Note
# --
# For some reason, I'm getting different clustered-errors-p-values when I use the 'cluster' flag in the 
# fit() function vs. when I calculate the result normally and then use get_robustcov_results function on that result. The former method yields slightly smaller p-values.
# 
# Outcome
# --
# The p-values are larger (for some outcomes, they are now > 0.05) but are still sufficiently small?

# <codecell>

outcomes.remove('numTotal')

# <codecell>

# (df_output['adjRs','orig. models'] - df_output['adjRs','cognate models']).plot(kind='kde')

from scipy.stats import ttest_1samp
import statsmodels.formula.api as smf

for outcome in outcomes:
    print outcome
    print 'Mean before substitution:', df_output[group1, outcome].mean()
    print 'Mean after substitution:', df_output[group2, outcome].mean()
    print 'Related samples t-test p-value:', np.around(ttest_rel(df_output[group1, outcome], df_output[group2, outcome])[1], 6)
 
    # GET CLUSTERED ERRORS
    # to do this run a regression Y ~ X where Y = outcomes, X = dummy {0=group1, 1=group2}
    # 1. Define variables
    outcomes_combined = list(df_output[group1, outcome]) + list(df_output[group2, outcome])
    diffs = df_output[group1, outcome] - df_output[group2, outcome]
    dummy = [0]*len(df_output[group1, outcome]) + [1]*len(df_output[group2, outcome])
    article_ids = list(df_output.article_id) 
    
    # 2. Fit models
#     result = smf.ols(formula='y~x', data=pd.DataFrame({'y':outcomes_combined, 'x':dummy})).fit() # do I need a constant???
#     result = smf.ols(formula='y~x-1', data=pd.DataFrame({'y':diffs, 'x':[1]*len(diffs)})).fit()
    result_clustered = smf.ols(formula='y~x-1',                      data=pd.DataFrame({'y':diffs, 'x':[1]*len(diffs)})).fit(missing='drop',                                                                              cov_type='cluster',                                                                     cov_kwds=dict(groups=article_ids))
                                                                                               
# these two methods produce slightly different results. neither is necessary because i'm using parameters
# of the model.fit() method above instead to use clustered standard errors.
#     # 3. Get clustered standard errors
#     robust_results = result.get_robustcov_results(cov_type='cluster', 
#                                                   use_correction=True,
#                                                   groups=article_ids, # this is article_id doubled
#                                                   df_correction=True) 
    
#     # 3.1 Get clustered standard errors another way, by regression diffs ~ const and seeing if const!=0
#     result_rob = result.get_robustcov_results(cov_type='cluster', \
#                                            groups=article_ids) # this is article_id singled
    
    print 'clustered errors p-value:', np.around(result_clustered.pvalues[0], 3)    
#     print 'clustered errors p-value:', np.around(result_rob.pvalues[0], 3)
    print

# <codecell>

df_output[group1, outcome]

# <codecell>


# <codecell>

pd.MultiIndex.from_product([outcomes, ['orig. models', 'cognate models']])

# <markdowncell>

# #How many models now have p > 0.05?

# <codecell>

print 'count:', df_output['cognate models']['pvalues'][df_output['cognate models']['pvalues'] > 0.05].shape[0]
print 'total:', df_output.shape[0]
print 'percent:', df_output['cognate models']['pvalues'][df_output['cognate models']['pvalues'] > 0.05].shape[0]/ df_output.shape[0]

