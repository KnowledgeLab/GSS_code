"""

filename: random models vs other equally random model

description: 
    last updated: 4/11/2014
    Run model on last year of data used vs. next available year of data
    
    
inputs:

outputs:

@author: Misha

"""
import sys
sys.path.append('../')
import GSSUtility as GU
import random
from collections import defaultdict
import numpy as np
import cPickle as cp

 
############################################################
if __name__ == "__main__":    
    
    pathToData = '../../Data/'
    dataCont = GU.dataContainer(pathToData)
    VARS_BY_YEAR = cp.load(open(pathToData + 'VARS_BY_YEAR.pickle'))
    
    articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=True, centralIVs=False, nextYearBound=3, yearPublished=True)            
    print 'len of articleClasses:', len(articlesToUse)
    raw_input('...')
    
    # define the storage containers for outputs
    group1 = 'randomVariables1'
    group2 = 'randomVariables2'    
    output = defaultdict(dict)
    groups = [group1, group2]
    outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues']   
    for year in range(1972,2014):
        for group in groups:
            output[group][year] = defaultdict(list)
            #for outcome in outcomes:
            #    output[group][year][outcome] = []
            
           
    for article in random.sample(articlesToUse, 300):
#    for article in articlesToUse:
    #for article in [a for a in articlesToUse if a.articleID == 6755]:
    
        print 'Processing article:', article.articleID

        maxYearUsed = max(article.GSSYearsUsed)
        
        RHS_random1 = random.sample(set(VARS_BY_YEAR[maxYearUsed])-set(article.DVs), len(article.IVs+ article.controls))
        RHS_random2 = random.sample(set(VARS_BY_YEAR[maxYearUsed])-set(article.DVs), len(article.IVs+ article.controls))
        
        for DV in article.DVs:
            print DV, '~', RHS_random1  

#            futureYearsPossible = [yr for yr in article.GSSYearsPossible if yr > maxYearUsed]
#            nextYear = min(futureYearsPossible) # the arguments of GU.filterArticles function ensure that there is a suitable future year (within bound)            
            resRandom1 = GU.runModel(dataCont, maxYearUsed, DV, RHS_random1) # models run on max year of data used
            if not resRandom1: continue
            resRandom2 = GU.runModel(dataCont, maxYearUsed, DV, RHS_random2) # models run on min year of future data
            if not resRandom2: continue
            
            # Checks on which results to record                
            if len(resRandom1.params) != len(resRandom2.params):
                print 'The number of variables in original model is different from the number in model on future years. Skipping.'                    
                continue
            
            # the condition below means that i don't care about models in which orig var isn't stat. sig.
#            if results.pvalues[-1] > 0.05: continue
            results = [resRandom1, resRandom2]
            
            # the lines below no longer work because i'm using both continuous and dummies!!
            
            for i in range(2):                 
                output[groups[i]][article.yearPublished]['Rs'].append(results[i].rsquared) 
                output[groups[i]][article.yearPublished]['adjRs'].append(results[i].rsquared_adj) 
                output[groups[i]][article.yearPublished]['propSig'].append(float(len([p for p in results[i].pvalues[1:] if p < 0.05]))/len(results[i].params[1:])) 
                output[groups[i]][article.yearPublished]['paramSizesNormed'].append(np.mean(results[i].params[1:].abs())) 
                output[groups[i]][article.yearPublished]['pvalues'].append(np.mean( results[i].pvalues[1:]))
                
   
    '''
    print 'TTests'
    for outcome in outcomes:
        print 'Means of group1 and group2:', np.mean(output[article.yearPublished][group1][article.yearPublished][outcome]), np.mean(output[article.yearPublished][group2][outcome]), 'Paired T-test of ' + outcome, ttest_rel(output[article.yearPublished][group1][outcome], output[article.yearPublished][group2][outcome])
    '''
    cp.dump(output, open('random_vs_random_models.pickle', 'wb'))