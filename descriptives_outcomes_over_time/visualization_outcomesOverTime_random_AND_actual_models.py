# -*- coding: utf-8 -*-
"""
Created on Fri May 09 12:08:37 2014

@author: Misha
"""
import statsmodels.formula.api as smf
import pandas as pd
import numpy as np
import cPickle as cp
from collections import defaultdict

outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', \
            'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']
pathToData = 'C:\Users\Misha\Dropbox\GSS Project\gss_code/minianalysis_outcomes_over_time/'
outputRandom = cp.load(open(pathToData + 'outputFromOutcomesOverTimeFromRandomVariables2.pickle'))
outputActual = cp.load(open(pathToData + 'outputFromOutcomesOverTime.pickle'))

years = range(1973,2003)

for outcome in output:

    print outcome
    
#    yErr = [2*np.std(x) for x in output[outcome]]
    yMeansActual = [np.mean(x) for x in outputActual[outcome]]
    yMeansRandom = [np.mean(x) for x in outputRandom[outcome]]

    XsRandom, YsRandom = [], []  
    XsActual, YsActual = [], []

    for row in outputRandom[outcome].index:
        XsRandom.extend([row]*len(outputRandom[outcome][row]))
        YsRandom.extend(outputRandom[outcome][row])
        XsActual.extend([row]*len(outputActual[outcome][row]))
        YsActual.extend(outputActual[outcome][row])
        
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
    plot(outputRandom.index, yMeansRandom, 'ro', alpha=0.9)
    plot(outputActual.index, yMeansActual, 'go', alpha=0.9)
    #plot(Xs, Ys, 'x', alpha=0.7)    
    resultRandom = smf.rlm(data=pd.DataFrame({'y':YsRandom, 'x':np.array(XsRandom)-1973}), formula='y~x').fit()    
    resultActual = smf.rlm(data=pd.DataFrame({'y':YsActual, 'x':np.array(XsActual)-1973}), formula='y~x').fit()    

    #result = smf.OLS(y_means,smt.add_constant(x_means)).fit() 
    plot(years, (np.array(years)-1973)*resultRandom.params[1] + resultRandom.params[0], 'r--')
    plot(years, (np.array(years)-1973)*resultActual.params[1] + resultActual.params[0], 'g--')

    figtext(0.45, 0.75, 'Red: random slope:'+str(np.around(resultRandom.params[1],4))+', p='+str(np.around(resultRandom.pvalues[1],2)))
    figtext(0.45, 0.8, 'Green: actual slope:'+str(np.around(resultActual.params[1],4))+', p='+str(np.around(resultActual.pvalues[1],2)))
    figtext(0.15, 0.75, 'random int.:'+str(np.around(resultRandom.params[0],2))+', p='+str(np.around(resultRandom.pvalues[0], 2)))
    figtext(0.15, 0.8, 'actual int.:'+str(np.around(resultActual.params[0],2))+', p='+str(np.around(resultActual.pvalues[0], 2)))
    show()