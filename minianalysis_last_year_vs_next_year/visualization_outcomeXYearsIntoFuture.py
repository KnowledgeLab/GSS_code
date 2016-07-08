# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 10:07:45 2014

@author: Misha
"""
import matplotlib.pylab as plt
import cPickle as cp
import statsmodels.formula.api as smf

pathToData = 'C:/Users/Misha/Dropbox/GSS Project/Data/'
output = cp.load(open('lastYearUsed_vs_x_Years_Into_Future.pickle'))
outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', \
                'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']
group1 = 'onDataUsed'
group2 = 'onFutureYear'    

#ax.errorbar(x, y, yerr=yerr, fmt='o')

#fig, axs = plt.subplots(nrows=len(outcomes), ncols=1, sharex=True)

#fig = pl.figure(figsize=(3,8))
#fig = plt.figure(1, figsize=(8,25))
years = range(43)
results={}
outcomeMap = {'propSig':"Proportion of Stat. Sign. Coeff's", 
              'paramSizesNormed':'Standardized Coefficients',
              'Rs':'R_squared', 
              'adjRs':'Adjusted R_squared',
              'pvalues':'Average P-Value',
              'propSig_CentralVars':"Central Vars: Proportion of Stat. Sign. Coeff's",
              'paramSizesNormed_CentralVars':'Central Vars: Standardized Coefficients', 
              'pvalues_CentralVars':'Central Vars: Average P-Value'}

for i, outcome in enumerate(outcomes):
    
    
    yearlyDiffs = [np.array(output[year][group2][outcome]) - np.array(output[year][group1][outcome]) for year in years]  
    yerr = [2*np.std(x) for x in yearlyDiffs]
    means = [np.mean(x) for x in yearlyDiffs]
    x, y = [], []
    for j in range(len(years)):
        for diffy in yearlyDiffs[j]:
            x.append(j)
            y.append(diffy)    
    
    
    '''
    ax = fig.add_subplot(8, 1, i)
#    ax.plot(x, y, '.', alpha=0.99)
    ax.plot(years, means, '.', alpha=0.99)
    if i==0:plt.xlabel('Years after last GSS wave used')
   
    #ax.text(0.1, i, outcome, bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})  

    formula = outcome+'~years'
    result = smf.ols(formula, data=pd.DataFrame({'years':x, outcome:y}).dropna(axis=0), missing='drop').fit()
    results[outcome] = result    
    ax.plot(years, np.array(years)*result.params[1] + result.params[0], 'r--')
#    fig.savefig('test.png', dpi=100)
    '''
    plot(years, means, '.', alpha=0.8)
    xlim((-1,43))
    xlabel('Years after publication')
    ylabel('Change in ' + outcomeMap[outcome])
    title(outcomeMap[outcome] + ' Over Time')
    formula = outcome+'~years'
    result = smf.rlm(formula, data=pd.DataFrame({'years':x, outcome:y}).dropna(axis=0), missing='drop').fit()
    plot(years, np.array(years)*result.params[1] + result.params[0], 'r--')
    figtext(0.2, 0.3, 'slope:'+str(np.around(result.params[1],4))+', p='+str(np.around(result.pvalues[1],3)))
#    figtext(0.6, 0.75, 'blue dot = model from an article')
    print 'intercept:'+str(result.params[0])+', '+str(result.pvalues[0])

    show()