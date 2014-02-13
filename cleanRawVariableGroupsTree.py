# -*- coding: utf-8 -*-
"""
name: createDictionaryOfVariableGroups.py

date: 2/12/2014

@author: Misha

description: Converts entries of rawVariableGroupsTree where {variableName:None} to variableName

"""



import numpy as np
import cPickle as cp

    
def parseTree(currentDict):
    
    if type(currentDict) == str: return
        
    # if all values are None
    if np.array([el is None for el in currentDict.values()]).all():
        return map(str.upper, map(str, currentDict.keys())) # convert elements to str and then to uppercase
    
    else:
    
        for k, v in currentDict.iteritems():            
            if type(v) == dict:                 
                currentDict[k] = parseTree(v)       
        return currentDict
    
    

if __name__ == "__main__":    
    
    # define variables
    pathToData = '../data/'
    rawTree = cp.load(open(pathToData + 'rawVariableGroupsTree.pickle'))

    # fill out cognateVariables dict
    for letter in rawTree:
        print 'processing letter', letter
        rawTree[letter] = parseTree(rawTree[letter])    
    
    cp.dump(rawTree, open(pathToData + 'rawVariableGroupsTree-cleaned.pickle', 'w'))