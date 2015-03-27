from __future__ import division

"""

filename: main_analysis.py

description:
    The codes has two parts. 
    The first constructs articleClass instances, where each instance contains all the important information
    for each article. 
    The second loops through the set of articles (articleClass classes) and estimates the models in each one.

inputs:

outputs:

notes:
 - Need to run the apprporiate models for different variable types
     - For binary dependent, do logistic
     - Split categorical IVs into dummies
     - Don't need to make any changes to ordinal IVs?
 - Need to speed up the code. Currently data accessing takes very long.
     - Try using data = data.all() instead?
         - Yes, this seems to do the trick!
 - Coefficient sizes
    - Evans wants to center the variables and normalize them, to see coefficient size       

Created on Sun Sep 01 15:55:48 2013

@author: Misha

"""

import cPickle as cp
import savReaderWriter as srw
import numpy as np
import statsmodels.api as sm 
import random, sys

# global variables
# i am taking out year 1984 for now because i don't have variables data on it! need to log in to commander.uchicago.edu
# and create a text file from variable view from that year's GSS...
GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 
			1980, 1982, 1983, 1985, 1986, 1987, 1988, 1989, 
			1990, 1991, 1993, 1994, 1996, 1998, 
			2000, 2002, 2004, 2006, 2008, 2010, 2012]
# NOTE TO SELF: ADD '1984' ABOVE ONCE YOU GET THE TEXT FILE FOR IT!


# LOAD FILES ########################################################################
sys.path.append('../Code/')
from articleClass import *
pathToData = '../Data/'
ALL_VARIABLE_NAMES = cp.load(open(pathToData + 'ALL_VARIABLE_NAMES.pickle'))
MISSING_VALUES_DICT = cp.load(open(pathToData + 'MISSING_VALUES_DICT.pickle', 'rb'))
articleIDAndGSSYearsUsed = cp.load(open(pathToData + 'articleIDAndGssYearsUsed-cleaned.pickle')) # load the years used
VARS_BY_YEAR = cp.load(open(pathToData + 'VARS_BY_YEAR.pickle'))
# structure of the dictionary above: { year (int) : [ set of variable names (strs), [variable_i, metadata_i] ] } 
YEAR_INDICES = cp.load(open(pathToData + 'YEAR_INDICES.pickle'))
VAR_INDICES = cp.load(open(pathToData + 'VAR_INDICES_binary.pickle', 'rb'))
articleClasses = cp.load(open(pathToData + 'articleClasses.pickle', 'rb'))
# Part 1 complete.

    
def removeMissingValues(variables, dataMat):    
    ''' 
    variables = list of variable names, potentially of length 1
    data = numpy matrix, potentially just a column, with data
    
    APPROACH: Want to remove rows after finishing going through the column data for each variable, because that
    will make the matrix smaller for when identifying missing values for next variable (column)
    Now I'm trying to figure out the best way to do this...
    1. Start with an array of indices, rowIndicesToUse = range(len(matOfIVsAndControls.shape[0]))
    2. Go through each variable
        2.1. figure out which row-indices of *current matrix* to remove 
        2.2. remove those indices from rowIndicesToUse
    
    '''
    # To start, assume that we'll be using all the rows (and the code below evaluates whether any of these should be removed)
    indicesUsed = range(dataMat.shape[0])
    
    for j, variable in enumerate(variables): # for each variable (column)
        
        misVals = MISSING_VALUES_DICT[variable]
        
        # If a variable has no missing values, then move on to the next variable
        if misVals == {}: continue
       
        # for each variable there's a unique set of rows I don't want to use (missing values)
        indicesToRemove = []            
    
        for i in range(dataMat.shape[0]): # for each row in the current table
            
            cellValue = dataMat[i, j]
            misVals = MISSING_VALUES_DICT[variable]
            
            # If the missing values are of the discrete type    
            if 'values' in misVals.keys():
                if cellValue in misVals['values']:
                    indicesToRemove.append(i)
            elif 'value' in misVals.keys():
                if cellValue == misVals['value']:
                    indicesToRemove.append(i)                                        
            elif 'lower' in misVals.keys():
                lowerBound = misVals[variable]['lower']
                upperBound = misVals[variable]['upper']
                if (cellValue >= lowerBound and cellValue) <= upperBound:
                    indicesToRemove.append(i)                
            else: # if it's not one of the 3 cases described above, what is it??
                print MISSING_VALUES_DICT[variable]
                raise 

        dataMat = np.delete(dataMat, indicesToRemove, axis=0)
        indicesUsed = np.delete(indicesUsed, indicesToRemove, axis=0)

        if len(indicesUsed) == 0:
            return [], dataMat
            
    return indicesUsed, dataMat

def center(mat):
    '''
    For each column in numpy array called mat, subtract the column's mean from each value and divide by sd.
    '''
    centeredMat = np.zeros(mat.shape)
    for j in range(mat.shape[1]):
        col = mat[:,j]
        centeredMat[:,j] = (col - np.mean(col)) / np.std(col)
    return centeredMat
        
### PART 2: ANALYSIS ####################################################
# Load GSS data create data 
allPropsForYearsUsed = []
allPropsForYearsPossible =[]
allParamSizesForYearsUsed = []
allParamSizesForYearsPossible = []

GSSFilename = 'GSS Dataset/GSS7212_R2.sav'
#data = srw.SavReader(pathToData + GSSFilename)
#with data:  # this makes sure the file will be closed, memory cleaned up after the program is run
#data = np.array(data.all()) # this makes sure the entire dataset is loaded into RAM, which makes accessing much faster
   
# NEED TO PUT A SECTION/FUNCTION HERE THAT DOES ALL THE FILTERING IN ONE PLACE, SO THAT BY THE TIME
# THE CODE GETS TO articleClasses, it only works on a subset it can actually process
#for article in random.sample(articleClasses, 50):
for article in articleClasses:

    print 'Processing article:', article.articleID
    
    if len(article.centralIVs) < 1: 
        print 'No "central" IVs. Skipping'
        continue 
    
    # coefficients significant
    coeffsTotalForYearsUsed = 0
    coeffsSigForYearsUsed = []
    coeffsSigForYearsPossible = []
    coeffsTotalForYearsPossible = 0
    
    # proportions of significant coeffs
    propSigForYearsUsed = 0
    propSigForYearsPossible = 0

    # parameter sizes
    paramSizesForYearsUsed = []
    paramSizesForYearsPossible = []
    avgParamSizeForYearsUsed = 0.0
    avgParamSizeForYearsPossible = 0.0
           
    for year in (article.GSSYearsUsed + article.GSSYearsPossible): # for each GSS year the article used or could've used          
        
        # Indices for this year
        startInd, endInd = YEAR_INDICES[year]['startInd'], YEAR_INDICES[year]['endInd']
                    
        # construct the matrix of IV and controls data
        listOfVars = article.IVs + article.controls # Might be better to do "set" because it would avoid the situation where there's an IV and control that's the same variable. Does this ever happen?!
        IVsAndControlsIndices = [VAR_INDICES[variable] for variable in listOfVars]
        matOfIVsAndControls = data[startInd:endInd, IVsAndControlsIndices] # without data = data.all(), this would be extremely slow
        
        # REMOVE MISSING VALUES
        IVsAndControlsRowsUsed, matOfIVsAndControls = removeMissingValues(listOfVars, matOfIVsAndControls)                                            
        if len(IVsAndControlsRowsUsed) == 0: 
            print 'No suitable IV or control data' 
            continue
        
        for DV in article.DVs: # for each model
            # construct DV column
            DVInd = VAR_INDICES[DV]
            DVCol = data[startInd + IVsAndControlsRowsUsed, DVInd]  # put into DVCol only those rows which has non-missing values in IVs and controls
            DVCol = np.reshape(DVCol, (len(DVCol),1))
            
            # Remove rows from DVCol which have missing values for the DV
            DVRowsUsed, DVCol = removeMissingValues([DV], DVCol)                
            
            if len(DVRowsUsed)==0:
                print 'All DV data missing/removed'
                continue
 
            # Remove rows from matOfIVsAndControls which have missing values for DV           
            matOfIVsAndControls_trimmed = np.delete(matOfIVsAndControls, list(set(range(len(matOfIVsAndControls))) - set(DVRowsUsed)), axis=0)
            
            # remove any columns that are constants
            constCols = []
            for i in range(matOfIVsAndControls_trimmed.shape[1]): # for every column
                if np.var(matOfIVsAndControls_trimmed[:,i]) == 0.0:
                    constCols.append(i)
            nonConstIVsAndControls = np.delete(listOfVars, constCols).tolist()
            matOfIVsAndControls_trimmed = np.delete(matOfIVsAndControls_trimmed, constCols, axis=1)
            
            # sm.add_constant does NOT add a column of 1's if the matrix already has a column of 1's, which can happen
            # if 1 is a code for an answer that everyone gives. If no constant is added, set the flag noConstant to True            
            if matOfIVsAndControls_trimmed.shape[1] == matOfIVsAndControls.shape[1]:
                noConstant = True
                
            # Do a check on data matrix dimensions. If #rows < #cols, then not enough data, and skip
            # This should skip situations where there is 12 variables and only 1 row of data
            if matOfIVsAndControls_trimmed.shape[0] < matOfIVsAndControls_trimmed.shape[1]:
                print 'Dimensions of DVCol:', DVCol.shape, ' Dimensions of matOf...', matOfIVsAndControls_trimmed.shape
                print 'Skipping this year...'
                continue
                
            # Estimate the model and put the sig p-values in an array results.pvalues
            # QUESTION: WHAT IF THERE ARE MORE COEFFICIENTS TO ESTIMATE THAN THERE IS DATA?
            # this DOES happen sometimes. Do I get a len() of unsized objects error? Where is the check
            # on dimensions performed?!
            results = sm.OLS(center(DVCol), sm.add_constant(center(matOfIVsAndControls_trimmed), prepend=False)).fit()

            indicesOfCentralIVs = np.array([i for i in range(len(nonConstIVsAndControls)) if nonConstIVsAndControls[i] in article.centralIVs], dtype=int)
        
            if year in article.GSSYearsUsed:                
                # Which coefficients do we care about? If all of them except constant, 
                # use the thing below (the first coeff is for the constant).                
                #coeffsSigForYearsUsed.extend([p for p in results.pvalues[1:] if p < 0.05]) # start at 1 because don't want to count the constant
                #coeffsTotalForYearsUsed += len(article.IVs + article.controls)   # want to count controls too??
                
                # If only care about IVs, comment out the 2 line above and use the line below
                coeffsSigForYearsUsed.extend([el for el in results.pvalues[:(len(article.IVs)-len(constCols))] if el < 0.05]) # start at 1 because don't want to count the constant
                coeffsTotalForYearsUsed += len(article.IVs)  
                paramSizesForYearsUsed.extend(results.params[:(len(article.IVs)-len(constCols))])
                
                '''
                #only count CENTRAL IVs
                coeffsSigForYearsUsed.extend([el for el in results.pvalues[indicesOfCentralIVs] if el < 0.05]) # start at 1 because don't want to count the constant
                coeffsTotalForYearsUsed += len(article.centralIVs)
                paramSizesForYearsUsed.extend(results.params[indicesOfCentralIVs])
                '''
            elif year in article.GSSYearsPossible: # the GSS year the models were run on is a "new" year, (wasn't used in article)
                # Which coefficients do we care about? If all of them except constant, 
                # use the thing below (the first coeff is for the constant).                
                #coeffsSigForYearsPossible.extend([el for el in results.pvalues[1:] if el < 0.05]) # start at 1 because don't want to count the constant
                #coeffsTotalForYearsPossible += len(article.IVs + article.controls)   # want to count controls too??
                # If only care about IVs, comment out the 2 line above and use the line below
                
                coeffsSigForYearsPossible.extend([el for el in results.pvalues[:(len(article.IVs)-len(constCols))] if el < 0.05]) # start at 1 because don't want to count the constant
                coeffsTotalForYearsPossible += len(article.IVs)  
                paramSizesForYearsPossible.extend(results.params[:(len(article.IVs)-len(constCols))])
                
                '''
                #only count CENTRAL IVs
                coeffsSigForYearsPossible.extend([el for el in results.pvalues[indicesOfCentralIVs] if el < 0.05]) # start at 1 because don't want to count the constant
                coeffsTotalForYearsPossible += len(article.centralIVs)  
                paramSizesForYearsPossible.extend(results.params[indicesOfCentralIVs])
                '''
                
    if coeffsTotalForYearsUsed != 0:
        propSigForYearsUsed = float(len(coeffsSigForYearsUsed)) / coeffsTotalForYearsUsed
        allPropsForYearsUsed.append(propSigForYearsUsed)
        allParamSizesForYearsUsed.append( np.mean(paramSizesForYearsUsed))
    if coeffsTotalForYearsPossible != 0:
        propSigForYearsPossible = float(len(coeffsSigForYearsPossible)) / coeffsTotalForYearsPossible
        allPropsForYearsPossible.append(propSigForYearsPossible)
        allParamSizesForYearsPossible.append( np.mean(paramSizesForYearsPossible))

# should i put a delete command for data here?
            
cp.dump(allPropsForYearsPossible, open(pathToData + 'allPropsForYearsPossible.pickle', 'wb'))
cp.dump(allPropsForYearsUsed, open(pathToData + 'allPropsForYearsUsed.pickle', 'wb'))
