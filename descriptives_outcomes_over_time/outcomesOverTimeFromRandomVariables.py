"""

filename: modelsRunOnNextYear.py

description: 
    last updated: 4/11/2014
    Run model on last year of data used vs. next available year of data, as long as it is within a provided bound    
    
inputs:

outputs:

@author: Misha

"""
import GSSUtility as GU
import numpy as np
import pandas as pd
import cPickle as cp
import random

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
    VARS_BY_YEAR = cp.load(open(pathToData + 'VARS_BY_YEAR.pickle'))
     
    articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, centralIVs=False, yearPublished=True)            
    print 'len of articleClasses:', len(articlesToUse)
    raw_input('...')

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
      
            for yearUsed in article.GSSYearsUsed:

                for count in range(10):
                    
                    RHSrandom = random.sample(set(VARS_BY_YEAR[yearUsed])-set(article.DVs), len(article.IVs+ article.controls))
    
                    print DV, '~', RHSrandom
          
                    res = GU.runModel(dataCont, yearUsed, DV, RHSrandom) # models run on max year of data used
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
         
                    print 'IVs:', article.IVs
                    print 'centralVas:', centralVars
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
                
    cp.dump(output, open('outputFromOutcomesOverTimeFromRandomVariables.pickle', 'wb'))