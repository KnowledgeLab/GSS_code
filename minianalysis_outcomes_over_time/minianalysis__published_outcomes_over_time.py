# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #minianalysis__published_outcomes_over_time
# 
# 
# 
# description: 
#     
# inputs:
# 
# outputs:
# 
# @author: Misha

# <codecell>

import sys
sys.path.append('../')
import GSSUtility as GU
import numpy as np
import pandas as pd
import cPickle as cp
import random
import seaborn

import statsmodels.formula.api as smf

# <codecell>

#*********************************************************
allPropsForYearsUsed = []
allPropsForYearsPossible =[]
allParamSizesForYearsUsed = []
allParamSizesForYearsPossible = []
allRsForYearsUsed, allRsForYearsPossible = [], []

 
############################################################
if __name__ == "__main__":    
    
    pathToData = '../../Data/'
    dataCont = GU.dataContainer(pathToData)
    
    articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, centralIVs=False, yearPublished=True)            
    print 'len of articleClasses:', len(articlesToUse)
#     raw_input('...')

    YEARS = range(1972, 2013)
    outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', \
                'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']
    output = pd.DataFrame(np.empty((len(YEARS), len(outcomes))), columns=outcomes, index=YEARS)    
    output = output.astype(object)
    for row in output.iterrows():
        for col in range(len(row[1])):
            row[1][col] = []
    
    #for article in random.sample(articlesToUse, 150):
    for article in articlesToUse:
    #for article in [a for a in articlesToUse if a.articleID == 6755]:
    
        print 'Processing article:', article.articleID
        
        RHS = article.IVs + article.controls
        
        for DV in article.DVs: 

#             print DV, '~', RHS
            
            for yearUsed in article.GSSYearsUsed:

                res = GU.runModel(dataCont, yearUsed, DV, RHS) # models run on max year of data used
                if not res: continue
                         
                # the lines below no longer work because i'm using both continuous and dummies!!
                centralVars = []            
                for civ in article.centralIVs:
                    if 'standardize(%s, ddof=1)' % (civ) in res.params.index:
                        centralVars.append('standardize(%s, ddof=1)' % (civ))
                    else: 
                        for col in res.params.index:
                            if 'C(' + civ + ')' in col:
                                centralVars.append(col)
     
#                 print 'IVs:', article.IVs
#                 print 'centralVas:', centralVars
    #            raw_input('...')
                '''                
                centralVars = ['standardize(%s, ddof=1)' % (cv) for cv in article.centralIVs]
                centralVars = set(centralVars).intersection(results[0].params.index) # need this step because some central                                                                                            # var columns may be removed when running model
                '''    
          
                output.loc[article.yearPublished]['Rs'].append(res.rsquared) 
                output.loc[article.yearPublished]['adjRs'].append(res.rsquared_adj) 
                output.loc[article.yearPublished]['propSig'].append(float(len([p for p in res.pvalues[1:] if p < 0.05]))/len(res.params[1:])) 
                output.loc[article.yearPublished]['paramSizesNormed'].append(np.mean(res.params[1:].abs())) 
                output.loc[article.yearPublished]['pvalues'].append(np.mean( res.pvalues[1:]))            
                if len(centralVars) > 0:            
                    output.loc[article.yearPublished]['pvalues_CentralVars'].append(np.mean(res.pvalues[centralVars]))               
                    output.loc[article.yearPublished]['propSig_CentralVars'].append(float(len([p for p in res.pvalues[centralVars] if p < 0.05])) \
                                                            /len(res.params[centralVars])) 
                    output.loc[article.yearPublished]['paramSizesNormed_CentralVars'].append(np.mean(res.params[centralVars].abs()))                
            
#     cp.dump(output, open('outputFromOutcomesOverTime.pickle', 'wb'))

# <codecell>

output

# <markdowncell>

# #Plot outcomes

# <codecell>

import cPicle as cp
outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', \
            'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']
# pathToData = 'C:\Users\Misha\Dropbox\GSS Project\gss_code/minianalysis_outcomes_over_time/'
output = cp.load(open('outputFromOutcomesOverTimeFromRandomVariables.pickle'))

years = range(1973,2003)

for outcome in output:

    print outcome
    
    yErr = [2*np.std(x) for x in output[outcome]]
    yMeans = [np.mean(x) for x in output[outcome]]

    Xs, Ys = [], []
    
    for row in output[outcome].index:
        Xs.extend([row]*len(output[outcome][row]))
        Ys.extend(output[outcome][row])

    ''' 
    ax = fig.add_subplot(8, 1, i)
    ax.text(10, 0, outcome, bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})  
    if 'propSig' in outcome:
        ax.set_ylim([-.3, .3])
    ax.plot(years, yearlyMeans, 'o-')
    
    print
    for yr in years:
        if not output[group1][yr][outcome]: continue
            
        x_means.append(yr)        
        for i in range(len(output[group1][yr][outcome])):
            x.append(yr)
            y.append(output[group2][yr][outcome][i]-output[group1][yr][outcome][i])
        y_means.append(np.mean(y))
    '''
    '''
    errorbar(output.index, yMeans, yerr=yErr, fmt='o-')
    result = smf.ols(data=pd.DataFrame({'y':Ys, 'x':Xs}), formula='y~x').fit()    
    #result = smf.OLS(y_means,smt.add_constant(x_means)).fit() 
    plot(years, np.array(years)*result.params[1] + result.params[0], 'r--')
    print 'slope:'+str(result.params[1])+', '+str(result.pvalues[1])
    '''

    
    title(outcome)
    xlabel('Year article was published')    
#    plot(x, y, 'x', x_means, y_means, 'o')
    plot(output.index, yMeans, 'o', alpha=0.9)
    #plot(Xs, Ys, 'x', alpha=0.7)    
    result = smf.ols(data=pd.DataFrame({'y':Ys, 'x':np.array(Xs)-1973}), formula='y~x').fit()    
    #result = smf.OLS(y_means,smt.add_constant(x_means)).fit() 
    plot(years, (np.array(years)-1973)*result.params[1] + result.params[0], 'r--')
    figtext(0.6, 0.8, 'slope:'+str(np.around(result.params[1],4))+', p='+str(np.around(result.pvalues[1],3)))
    figtext(0.55, 0.75, 'green=raw data, blue=means')
    print 'intercept:'+str(result.params[0])+', '+str(result.pvalues[0])
    show()

# <codecell>


