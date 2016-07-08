"""

filename: lastYearUsed_vs_x_Years_Into_Future.py

description: Take models run on the last year of GSS an article used and compare them vs that model on future 
             waves of GSS. Each difference in outcomes counts as one observation, i.e. many observations
             per article.

inputs:

outputs:

@author: Misha

"""

import GSSUtility as GU # this also imports a whole bunch of other modules

if __name__ == "__main__":    

    pathToData = '../../Data/'
    dataCont = GU.dataContainer(pathToData)
    
    articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, centralIVs=True)            
    print 'len of articleClasses:', len(articlesToUse)
    raw_input('...')
    
    # define the storage containers for outputs
    group1 = 'onDataUsed'
    group2 = 'onFutureYear'    
    output = defaultdict(dict)
    groups = [group1, group2]
    outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', 'numTotal', \
                'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']
    for yr in range(43):
        output[yr] = {}
        for group in groups:
            output[yr][group] = {}
            for outcome in outcomes:
                output[yr][group][outcome] = []
            
           
    #for article in random.sample(articlesToUse, 30):
    for article in articlesToUse:
    #for article in [a for a in articlesToUse if a.articleID == 6755]:
    
        print 'Processing article:', article.articleID
 
        '''             
        # define the outcomes I'm interseted in for the two groups. td = "temp data" 
        # and initialize them for both groups
        td = defaultdict(dict)
        for group in groups:             
            td[group]['numTotal'] = 0.0
    #        td[group]['coeffsSig'] = []
            td[group]['numSig'] = 0.0   # proportions of significant coeffs
    #        td[group]['paramSizes'] = []
            td[group]['paramSizesNormed'] = []
            td[group]['Rs'] = []
            td[group]['adjRs'] = []
            td[group]['pvalues'] = []
        '''
        LHS = article.IVs + article.controls
        
        for DV in article.DVs:
            maxYearUsed = max(article.GSSYearsUsed)          
            resOnDataUsed = GU.runModel(dataCont, maxYearUsed, DV, LHS) # models run on max year of data used
            if not resOnDataUsed: continue

            # Now do future years
            futureYearsPossible = [yr for yr in article.GSSYearsPossible if yr > maxYearUsed]
            for futureYear in futureYearsPossible:
                resOnFutureYear = GU.runModel(dataCont, futureYear, DV, LHS) # models run on min year of future data
                if not resOnFutureYear: continue
            
                # Checks on which results to record                
                if len(resOnDataUsed.params) != len(resOnFutureYear.params):
                    print 'The number of variables in original model is different from the number in cognate model. Skipping.'                    
                    continue
                
                results = [resOnDataUsed, resOnFutureYear]

                # get column names of 'central variables'; this is tricky because some hve been dummy-fied                
                centralVars = []            
                for civ in article.centralIVs:
                    if 'standardize(%s, ddof=1)' % (civ) in results[0].params.index:
                        centralVars.append('standardize(%s, ddof=1)' % (civ))
                    else: 
                        for col in results[0].params.index:
                            if 'C(' + civ + ')' in col:
                                centralVars.append(col)
     
                print 'IVs:', article.IVs
                print 'centralVars:', centralVars
                
                for i in range(2):                 
                    output[futureYear - maxYearUsed][groups[i]]['Rs'].append(results[i].rsquared) 
                    output[futureYear - maxYearUsed][groups[i]]['adjRs'].append(results[i].rsquared_adj) 
                    output[futureYear - maxYearUsed][groups[i]]['propSig'].append(float(len([p for p in results[i].pvalues[1:] if p < 0.05]))/len(results[i].params[1:])) 
                    output[futureYear - maxYearUsed][groups[i]]['paramSizesNormed'].append(np.mean(results[i].params[1:].abs())) 
                    '''
                    if np.isnan(np.mean( td[group]['paramSizesNormed'])).any():
                        print results[i].summary()
                        raise
                    '''
                    output[futureYear - maxYearUsed][groups[i]]['pvalues'].append(np.mean( results[i].pvalues[1:]))
                    output[futureYear - maxYearUsed][groups[i]]['numTotal'].append( 1 ) #divide by len of R^2 array to get a mean of variables estimated PER model                           
                    output[futureYear - maxYearUsed][groups[i]]['pvalues_CentralVars'].append(np.mean(results[i].pvalues[centralVars]))               
                    output[futureYear - maxYearUsed][groups[i]]['propSig_CentralVars'].append(float(len([p for p in results[i].pvalues[centralVars] if p < 0.05])) \
                                                            /len(results[i].params[centralVars])) 
                    output[futureYear - maxYearUsed][groups[i]]['paramSizesNormed_CentralVars'].append(np.mean(results[i].params[centralVars].abs()))                


  
    print 'TTests'

    for year in range(43):
        for outcome in outcomes:
            print year            
            print 'Means of group1 and group2:', np.mean(output[year][group1][outcome]), np.mean(output[year][group2][outcome]), 'Paired T-test of ' + outcome, ttest_rel(output[year][group1][outcome], output[year][group2][outcome])

    cp.dump(output, open('lastYearUsed_vs_x_Years_Into_Future.pickle', 'wb'))    