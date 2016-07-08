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
    
    articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=True, centralIVs=True, nextYearBound=3, yearPublished=True)            
    print 'len of articleClasses:', len(articlesToUse)
    raw_input('...')
    
    # define the storage containers for outputs
    group1 = 'onDataUsed'
    group2 = 'onNextYear'    
    output = defaultdict(dict)
    groups = [group1, group2]
    outcomes = ['propSig', 'paramSizesNormed', 'Rs', 'adjRs', 'pvalues', \
                'propSig_CentralVars', 'paramSizesNormed_CentralVars', 'pvalues_CentralVars']
    for year in range(1972,2014):
        for group in groups:
            output[group][year] = defaultdict(list)
            #for outcome in outcomes:
            #    output[year][group][outcome] = []
            
           
    #for article in random.sample(articlesToUse, 150):
    for article in articlesToUse:
    #for article in [a for a in articlesToUse if a.articleID == 6755]:
    
        print 'Processing article:', article.articleID
        
        RHS = article.IVs + article.controls
        
        for DV in article.DVs:
            print DV, '~', RHS
            maxYearUsed = max(article.GSSYearsUsed)
            futureYearsPossible = [yr for yr in article.GSSYearsPossible if yr > maxYearUsed]
            nextYear = min(futureYearsPossible) # the arguments of GU.filterArticles function ensure that there is a suitable future year (within bound)
            
            resOnDataUsed = GU.runModel(dataCont, maxYearUsed, DV, RHS) # models run on max year of data used
            if not resOnDataUsed: continue
            resOnNextYear = GU.runModel(dataCont, nextYear, DV, RHS) # models run on min year of future data
            if not resOnNextYear: continue
            
            # Checks on which results to record                
            if len(resOnDataUsed.params) != len(resOnNextYear.params):
                print 'The number of variables in original model is different from the number in model on future years. Skipping.'                    
                continue
            
            # the condition below means that i don't care about models in which orig var isn't stat. sig.
#            if results.pvalues[-1] > 0.05: continue
            results = [resOnDataUsed, resOnNextYear]
            
            # the lines below no longer work because i'm using both continuous and dummies!!
            centralVars = []            
            for civ in article.centralIVs:
                if 'standardize(%s, ddof=1)' % (civ) in results[0].params.index:
                    centralVars.append('standardize(%s, ddof=1)' % (civ))
                else: 
                    for col in results[0].params.index:
                        if 'C(' + civ + ')' in col:
                            centralVars.append(col)
 
            print 'IVs:', article.IVs
            print 'centralVas:', centralVars
#            raw_input('...')
            '''                
            centralVars = ['standardize(%s, ddof=1)' % (cv) for cv in article.centralIVs]
            centralVars = set(centralVars).intersection(results[0].params.index) # need this step because some central                                                                                            # var columns may be removed when running model
            '''
            
            for i in range(2):                 
                output[groups[i]][article.yearPublished]['Rs'].append(results[i].rsquared) 
                output[groups[i]][article.yearPublished]['adjRs'].append(results[i].rsquared_adj) 
                output[groups[i]][article.yearPublished]['propSig'].append(float(len([p for p in results[i].pvalues[1:] if p < 0.05]))/len(results[i].params[1:])) 
                output[groups[i]][article.yearPublished]['paramSizesNormed'].append(np.mean(results[i].params[1:].abs())) 
                output[groups[i]][article.yearPublished]['pvalues'].append(np.mean( results[i].pvalues[1:]))
                output[groups[i]][article.yearPublished]['numTotal'].append( 1 ) #divide by len of R^2 array to get a mean of variables estimated PER model                           
                
                output[groups[i]][article.yearPublished]['pvalues_CentralVars'].append(np.mean(results[i].pvalues[centralVars]))               
                output[groups[i]][article.yearPublished]['propSig_CentralVars'].append(float(len([p for p in results[i].pvalues[centralVars] if p < 0.05])) \
                                                        /len(results[i].params[centralVars])) 
                output[groups[i]][article.yearPublished]['paramSizesNormed_CentralVars'].append(np.mean(results[i].params[centralVars].abs()))                
                
   
    '''
    print 'TTests'
    for outcome in outcomes:
        print 'Means of group1 and group2:', np.mean(output[article.yearPublished][group1][article.yearPublished][outcome]), np.mean(output[article.yearPublished][group2][outcome]), 'Paired T-test of ' + outcome, ttest_rel(output[article.yearPublished][group1][outcome], output[article.yearPublished][group2][outcome])
    '''
    cp.dump(output, open(pathToData + 'modelsRunOnNextYear_vs_YearPublished.pickle', 'wb'))