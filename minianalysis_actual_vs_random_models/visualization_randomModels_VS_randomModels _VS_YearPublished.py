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

group1 = 'randomVariables1'
group2 = 'randomVariables2'    
output = defaultdict(dict)
groups = [group1, group2]
outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues']

pathToData = 'C:\Users\Misha\Dropbox\GSS Project\data/'
output = cp.load(open('random_vs_random_models.pickle'))

years = range(1972,2014)
for outcome in outcomes:

    print outcome

    x,y=[],[]
    x_means, y_means = [], []
    
    for yr in years:
        if not output[group1][yr][outcome]: continue
            
        x_means.append(yr)        
        for i in range(len(output[group1][yr][outcome])):
            x.append(yr)
            y.append(output[group2][yr][outcome][i]-output[group1][yr][outcome][i])
        y_means.append(np.mean(y))
    
    title(outcome)    
    plot(x, y, 'x', x_means, y_means, 'o')
    plot(x_means, y_means, 'o')
    result = smf.ols(data=pd.DataFrame({'y':y, 'x':x}), formula='y~x').fit()    
    #result = smf.OLS(y_means,smt.add_constant(x_means)).fit() 
    plot(years, np.array(years)*result.params[1] + result.params[0], 'r--')
    print 'slope:'+str(result.params[1])+', '+str(result.pvalues[1])
    print 'intercept:'+str(result.params[0])+', '+str(result.pvalues[0])

    show()
    
    raw_input('..')