# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 10:07:45 2014

@author: Misha
"""
import matplotlib.pylab as plt

#ax.errorbar(x, y, yerr=yerr, fmt='o')

#fig, axs = plt.subplots(nrows=len(outcomes), ncols=1, sharex=True)

#fig = pl.figure(figsize=(3,8))
fig = plt.figure(1, figsize=(8,16))
results={}
for i, outcome in enumerate(outcomes[:4]):
    
    yearlyDiffs = [np.array(output[year][group2][outcome]) - np.array(output[year][group1][outcome]) for year in years]  
    yerr = [2*np.std(x) for x in yearlyDiffs]
    means = [np.mean(x) for x in yearlyDiffs]
    x, y = [], []
    for j in range(len(years)):
        for diffy in yearlyDiffs[j]:
            x.append(j)
            y.append(diffy)    
    
    ax = fig.add_subplot(4, 1, i)
    ax.plot(x, y, '.', alpha=0.99)
    if i==0:plt.xlabel('Years after last GSS wave used')
   
    ax.text(32, 0.1, outcome, bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})  

    formula = outcome+'~years'
    result = smf.ols(formula, data=pd.DataFrame({'years':x, outcome:y}).dropna(axis=0), missing='drop').fit()
    results[outcome] = result    
    ax.plot(years, np.array(years)*result.params[1] + result.params[0], 'r--')

fig.savefig('test.png', dpi=100)