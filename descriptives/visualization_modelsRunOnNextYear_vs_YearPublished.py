# -*- coding: utf-8 -*-
"""
Created on Fri May 09 12:08:37 2014

@author: Misha
"""
import statsmodels.formula.api as smf
import statsmodels.tools as smt
import pandas as pd
import numpy as np
import cPickle as cp
from collections import defaultdict

group1 = 'onDataUsed'
group2 = 'onNextYear'    
output = defaultdict(dict)
groups = [group1, group2]
outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', \
            'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']
 
pathToData = 'C:\Users\Misha\Dropbox\GSS Project\data/'
output = cp.load(open(pathToData + 'actual_vs_random_models.pickle'))

years = range(1972,2014)
for outcome in outcomes:

    print outcome

    x,y=[],[]
    x_means, y_means = [], []
    
    for yr in output.keys():
        if not output[yr][group1][outcome]: continue
            
        x_means.append(yr)        
        for i in range(len(output[yr][group1][outcome])):
            x.append(yr)
            y.append(output[yr][group2][outcome][i]-output[yr][group1][outcome][i])
        y_means.append(np.mean(y))
        
    scatter(x,y)
    #plot(x_means, y_means, 'o')
#    result = smf.ols(data=pd.DataFrame({'y':y, 'x':x}), formula='y~x').fit()    
    #result = smf.OLS(y_means,smt.add_constant(x_means)).fit() 
 #  plot(years, np.array(years)*result.params[1] + result.params[0], 'r--')

    show()
    
    raw_input('..')