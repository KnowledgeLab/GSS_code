# -*- coding: utf-8 -*-
"""
Created on Fri May 09 12:08:37 2014

@author: Misha
"""
from scipy.stats import ttest_rel, ttest_ind
import pandas as pd
import numpy as np
import cPickle as cp
from collections import defaultdict

outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', \
            'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']
pathToData = 'C:\Users\Misha\Dropbox\GSS Project\gss_code/minianalysis_cognate_variables/'
output = cp.load(open(pathToData + 'outputFromCognateVariableAnalysis_vs_YearPublished.pickle'))

groups = ['actualModel', 'cognateModel']

# the dict below is used to convert shorthand outcome names
# to more descriptive strings
outcomeMap = {'propSig':"Proportion of Stat. Sign. Coeff's", 
              'paramSizesNormed':'Standardized Coeff. Size',
              'Rs':'R_squared', 
              'adjRs':'Adjusted R_squared',
              'pvalues':'Average P-Value',
              'propSig_CentralVars':"Central Vars: Proportion of Stat. Sign. Coeff's",
              'paramSizesNormed_CentralVars':'Central Vars: Standardized Coefficients', 
              'pvalues_CentralVars':'Central Vars: Average P-Value'}

for outcome in outcomes:

    print outcomeMap[outcome]
    
#    yErr = [2*np.std(x) for x in output[outcome]]
#    yMeans = [np.mean(x) for x in output[outcome]]
    
    '''
    errorbar(output.index, yMeans, yerr=yErr, fmt='o-')
    result = smf.ols(data=pd.DataFrame({'y':Ys, 'x':Xs}), formula='y~x').fit()    
    #result = smf.OLS(y_means,smt.add_constant(x_means)).fit() 
    plot(years, np.array(years)*result.params[1] + result.params[0], 'r--')
    print 'slope:'+str(result.params[1])+', '+str(result.pvalues[1])
    '''

    meanActual = np.mean(output['actualModel'][outcome].sum())
    meanCognate = np.mean(output['cognateModel'][outcome].sum())
    stActual = np.std(output['actualModel'][outcome].sum())
    stCognate = np.std(output['cognateModel'][outcome].sum())  

    width=0.25
    fig, ax = plt.subplots()
    rects = ax.bar(left=[0.25,0.6], width=width, \
        height=[meanActual, meanCognate], \
        #yerr = [stActual, stCognate], \
        alpha=0.5)
    #ax.set_ylabel('')
    ax.set_title(outcomeMap[outcome])
    ax.set_xticks([0.2+width/2,0.6+width/2])
    ax.set_xticklabels( ('Actual models', 'Cognate models') )
    
    def autolabel(rects):
    # attach some text labels
        global maxHeight        
        for rect in rects:
            height = rect.get_height()
            #if heightx>maxHeight:maxHeight=heightx
            ax.text(rect.get_x()+rect.get_width()/2, 1.05*height, \
                    '%s'%(np.around(height, decimals=3)), \
                    ha='center', va='bottom')
    ylim((0,max([meanActual, meanCognate])+.1))
    autolabel(rects)
    show()
    
    print ttest_ind(output['actualModel'][outcome].sum(), \
                    output['cognateModel'][outcome].sum())
    print ttest_rel(output['actualModel'][outcome].sum(), \
                    output['cognateModel'][outcome].sum())                    