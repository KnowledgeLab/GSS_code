# -*- coding: utf-8 -*-
"""
Created on Wed May 07 14:21:37 2014

@author: Misha
"""

fig = plt.figure(1, figsize=(8,16))

results={}
for i, outcome in enumerate(outcomes):
    
    years = range(1,43)
    
    yearlyDiffs = [np.array(output[year][group2][outcome]) - np.array(output[year][group1][outcome]) for year in years]  
    yerr = [2*np.std(x) for x in yearlyDiffs]
    yearlyMeans = [np.mean(x) for x in yearlyDiffs]
 
    ax = fig.add_subplot(8, 1, i)
    ax.text(10, 0, outcome, bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})  
    if 'propSig' in outcome:
        ax.set_ylim([-.3, .3])
    ax.plot(years, yearlyMeans, 'o-')
    #ax.errorbar(years, yearlyMeans, yerr=yerr, fmt='o')
    ax.plot([min(years), max(years)], [0,0]) 
