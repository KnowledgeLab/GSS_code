"""

filename: cognateVariablesAnalysis_model_unit_of_analysis.py

description: Runs models as specified originally and again after replacing a central variable by a cognate var.
It compares regressions on what was then the new data vs same regressions on future waves

inputs:

outputs:

@author: Misha

"""
from __future__ import division
#import cPickle as cp
#import pandas as pd
import sys
sys.path.append('../')    
import numpy as np
import statsmodels.formula.api as smf 
import random
from scipy.stats import pearsonr, ttest_ind, ttest_rel
import time
from collections import Counter
from collections import defaultdict
#from GSSUtility import *
import GSSUtility as GU


    
    
############################################################
if __name__ == "__main__":    
    
    pathToData = '../../Data/'
    dataCont = GU.dataContainer(pathToData)
    
    tempCognateOutput = open(pathToData + 'tempCognateOutput.txt', 'w')
    
    # contains for storing (variable, cognate) tuples in order to see what substitutions
    #i'm most commonly making
    variableCognateTuples = []
    
    # define the storage containers for outputs
    output = defaultdict(dict)
    groups = ['group1', 'group2']
    outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', 'numTotal']
    for group in groups:
        for outcome in outcomes:
            output[group][outcome] = []
            
    
    articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, centralIVs=True)            
    for article in random.sample(articlesToUse, 20):
    #for article in articlesToUse:
    #for article in [a for a in articleClasses if a.articleID == 6755]:
    
        print 'Processing article:', article.articleID
              
        # define the outcomes I'm interseted in for the two groups. td = "temp data" 
        # and initialize them for both groups
        td = defaultdict(dict)
        for group in groups:             
            td[group]['numTotal'] = 0.0
    #        td[group]['coeffsSig'] = []
            td[group]['numSig'] = 0.0   # proportions of significant coeffs
    #        td[group]['paramSizes'] = []
            td[group]['paramSizesNormed'] = []
            td[group]['Rs'] = []
            td[group]['adjRs'] = []
            td[group]['pvalues'] = []


        # let's see if this article is suitable for cognates analysis:
        originalLHS = article.IVs + article.controls
        identifyCognatesReturns = GU.identifyCognates(dataCont, originalLHS, article.centralIVs, article.GSSYearsUsed, corrThreshold=0.6)        
        if not identifyCognatesReturns: 
            print 'No suitable cognates. Skipping.'            
            continue        
        else: 
            cIV, cognate, GSSYearsWithCognate = identifyCognatesReturns

        # if we got this far, then this article does have suitable cognates, so let's estimate models       
        # Now let's estimate the models
        for DV in article.DVs:            
            for year in GSSYearsWithCognate:        

                # group 2 models (with cognates)
                group = 'group2'
                print 'Running cognate models'
                
                cognateLHS = originalLHS[:]
                cognateLHS.remove(cIV)
                cognateLHS.append(cognate) # need to put it in list otherwise it treats each letter as an element
                print 'Substituting', cIV, 'with cognate', cognate
                #time.sleep(2)
                #raw_input('Press Enter')                
                
                resultsCognate = GU.runModel(dataCont, year, DV, cognateLHS)          
                if not resultsCognate: continue # results will be None if the formula cant be estimated
                print DV, '~', cognateLHS, 'on year', year
                 
                # RUN MODELS FROM GROUP 1 ############################################  
                # group 1
                group = 'group1'
                print 'Running original models.'
                
                # make sure cIV is last in the list of variables
                originalLHS.remove(cIV)
                originalLHS.append(cIV) 
    
                results = GU.runModel(dataCont, year, DV, originalLHS)                     
                if not results: continue # results will be None if the formula cant be estimated
                
                # Checks on which results to record                
                if len(results.params) != len(resultsCognate.params):
                    print 'The number of variables in original model is different from the number in cognate model. Skipping.'                    
                    continue
                
                # the condition below means that i don't care about models in which orig var isn't stat. sig.
                if results.pvalues[-1] > 0.05: continue
                    
                # save the results                   
                td['group2']['Rs'].append(resultsCognate.rsquared)
                td['group2']['adjRs'].append(resultsCognate.rsquared_adj)
                td['group2']['numTotal'] += len(resultsCognate.params[1:])
                td['group2']['numSig'] += float(len([p for p in resultsCognate.pvalues[1:] if p < 0.05])) # start at 1 because don't want to count the constant
                td['group2']['paramSizesNormed'].append(abs(resultsCognate.params[-1])) # get the absolute value of the standardized coefficients and take the mean 
                td['group2']['pvalues'].append(resultsCognate.pvalues[-1])
            
                # Intermediate output (for years, because will average across these)
                td['group1']['Rs'].append(results.rsquared)
                td['group1']['adjRs'].append(results.rsquared_adj)
                td['group1']['numTotal'] += len(results.params[1:])
                td['group1']['numSig'] += float(len([p for p in results.pvalues[1:] if p < 0.05])) # start at 1 because don't want to count the constant
                td['group1']['paramSizesNormed'].append(abs(results.params[-1])) # get the absolute value of the standardized coefficients and take the mean 
                td['group1']['pvalues'].append(results.pvalues[-1])
         


                print >> tempCognateOutput, 'Orig:\t', cIV, '\t\tCogn:\t', cognate, '\t\t Coeffs:\t', results.params[-1], results.pvalues[-1],resultsCognate.params[-1], resultsCognate.pvalues[-1] 
            
            
            
            # The change I'm making is that the block below is now within the for loop
            # of "for DV in article.DVs". So I'm averaging over years but not DVs                    
            # if an article's model isn't run on both group 1 and group 2, skip it        
            if td['group1']['numTotal'] == 0 or td['group2']['numTotal'] == 0: continue
          
            variableCognateTuples.append((cIV, cognate))
            for group in groups:      
                output[group]['Rs'].append( np.mean(td[group]['Rs'])) 
                output[group]['adjRs'].append(np.mean( td[group]['adjRs'])) 
                output[group]['propSig'].append( td[group]['numSig']/td[group]['numTotal']) 
                output[group]['paramSizesNormed'].append(np.mean( td[group]['paramSizesNormed'])) 
                output[group]['pvalues'].append(np.mean( td[group]['pvalues']))
                output[group]['numTotal'].append(td[group]['numTotal'] / len(td[group]['Rs'])) #divide by len of R^2 array to get a mean of variables estimated PER model                           
        
        
    print 'TTests'
    for outcome in outcomes:
        print 'Means of group1 and group2:', np.mean(output['group1'][outcome]), np.mean(output['group2'][outcome]), 'Paired T-test of ' + outcome, ttest_rel(output['group1'][outcome], output['group2'][outcome])

    tempCognateOutput.close()    