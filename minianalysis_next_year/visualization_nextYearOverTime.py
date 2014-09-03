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

outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', \
            'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']
pathToData = 'C:\Users\Misha\Dropbox\GSS Project\gss_code/minianalysis_next_year/'
output = cp.load(open(pathToData + 'outputFromNextYearOfDataOverTime.pickle'))

years = range(1974,2003)

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
    plot(Xs, Ys, 'x', alpha=0.7)    
    result = smf.rlm(data=pd.DataFrame({'y':Ys, 'x':Xs}), formula='y~x').fit()    
    #result = smf.OLS(y_means,smt.add_constant(x_means)).fit() 
    plot(years, np.array(years)*result.params[1] + result.params[0], 'r--')
    figtext(0.6, 0.8, 'slope:'+str(np.around(result.params[1],4))+', p='+str(np.around(result.pvalues[1],3)))
    figtext(0.55, 0.75, 'green=raw data, blue=means')
    print 'intercept:'+str(result.params[0])+', '+str(result.pvalues[0])
    show()
    
    #raw_input('..')