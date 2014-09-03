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
import pandas as pd
import cPickle as cp
import GSSUtility as GU
  
    
############################################################
if __name__ == "__main__":    
    
    pathToData = '../../Data/'
    dataCont = GU.dataContainer(pathToData)
    
#    tempCognateOutput = open(pathToData + 'tempCognateOutput.txt', 'w')
    
    # contains for storing (variable, cognate) tuples in order to see what substitutions
    #i'm most commonly making
    variableCognateTuples = []
    
    # define the storage container (pandas DataFrame) for output
    groups = ['actualModel', 'cognateModel']         
    YEARS = range(1972, 2013)
    outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', \
                'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']
    columnIndex = pd.MultiIndex.from_product([groups, outcomes])
    output = pd.DataFrame(np.empty((len(YEARS), len(outcomes)*2)), columns=columnIndex, index=YEARS)    
    output = output.astype(object)
    for row in output.iterrows():
        for col in range(len(row[1])):
            row[1][col] = []
                
    articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, centralIVs=True)            
    print 'len of articleClasses:', len(articlesToUse)
    raw_input('...')

    #for article in random.sample(articlesToUse, 50):       
    for article in articlesToUse:
    #for article in [a for a in articleClasses if a.articleID == 6755]:
        
        print 'Processing article:', article.articleID
              
        # let's see if this article is suitable for cognates analysis:
        originalLHS = list(set(article.IVs + article.controls))
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
                print 'Running cognate models'
                
                cognateLHS = originalLHS[:]
                cognateLHS.remove(cIV)
                cognateLHS.append(cognate) # need to put it in list otherwise it treats each letter as an element
                print 'Substituting', cIV, 'with cognate', cognate
                #time.sleep(2)               
                
                resultsCognate = GU.runModel(dataCont, year, DV, cognateLHS)          
                if not resultsCognate: continue # results will be None if the formula cant be estimated
                print DV, '~', cognateLHS, 'on year', year
                 
                # RUN MODELS FROM GROUP 1 ############################################  
                # group 1
                print 'Running original models.'
                
                # make sure cIV is last in the list of variables
                resultsOriginal = GU.runModel(dataCont, year, DV, originalLHS)                     
                if not resultsOriginal: continue # results will be None if the formula cant be estimated
                
                # Checks on which results to record                
                if len(resultsOriginal.params) != len(resultsCognate.params):
                    print 'The number of variables in original model is different from the number in cognate model. Skipping.'                    
                    continue

                results = [resultsOriginal, resultsCognate]                    
                # save the results

                cIVParamNames = []            
                if 'standardize(%s, ddof=1)' % (cIV) in resultsOriginal.params.index:
                    cIVParamNames.append('standardize(%s, ddof=1)' % (cIV))
                else: 
                    for col in resultsOriginal.params.index:
                        if 'C(' + cIV + ')' in col:
                            cIVParamNames.append(col)
                
                cognateParamNames = []            
                if 'standardize(%s, ddof=1)' % (cognate) in resultsCognate.params.index:
                    cognateParamNames.append('standardize(%s, ddof=1)' % (cognate))
                else: 
                    for col in resultsCognate.params.index:
                        if 'C(' + cognate + ')' in col:
                            cognateParamNames.append(col)
                
                # param names for the cIV-->cognate substitution are stored here
                substitutionParamNames = [cIVParamNames, cognateParamNames]
                 
                for i in range(2):
                    output[groups[i]]['Rs'][article.yearPublished].append(results[i].rsquared) 
                    output[groups[i]]['adjRs'][article.yearPublished].append(results[i].rsquared_adj) 
                    output[groups[i]]['propSig'][article.yearPublished].append(float(len([p for p in results[i].pvalues[1:] if p < 0.05]))/len(results[i].params[1:])) 
                    output[groups[i]]['paramSizesNormed'][article.yearPublished].append(np.mean(results[i].params[1:].abs())) 
                    output[groups[i]]['pvalues'][article.yearPublished].append(np.mean( results[i].pvalues[1:]))            
    
                    # CIV that I substituted for
                    output[groups[i]]['pvalues_CentralVars'][article.yearPublished].append(np.mean(results[i].pvalues[substitutionParamNames[i]]))               
                    output[groups[i]]['propSig_CentralVars'][article.yearPublished].append(float(len([p for p in results[i].pvalues[substitutionParamNames[i]] if p < 0.05])) \
                                                                /len(results[i].params[substitutionParamNames[i]])) 
                    output[groups[i]]['paramSizesNormed_CentralVars'][article.yearPublished].append(np.mean(results[i].params[substitutionParamNames[i]].abs()))                
            

#                print >> tempCognateOutput, 'Orig:\t', cIV, '\t\tCogn:\t', cognate, '\t\t Coeffs:\t', results.params[substitutionParamNames[i]], results.pvalues[substitutionParamNames[i]],resultsCognate.params[substitutionParamNames[i]], resultsCognate.pvalues[-1] 
            
            
            variableCognateTuples.append((cIV, cognate))

    '''        
    print 'TTests'
    for outcome in outcomes:
        print 'Means of group1 and group2:', np.mean(output['group1'][outcome]), np.mean(output['group2'][outcome]), 'Paired T-test of ' + outcome, ttest_rel(output['group1'][outcome], output['group2'][outcome])
    '''
 #   tempCognateOutput.close()    
    
    cp.dump(output, open('outputFromCognateVariableAnalysis_vs_YearPublished.pickle', 'wb'))
