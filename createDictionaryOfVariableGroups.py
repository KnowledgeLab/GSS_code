# -*- coding: utf-8 -*-
"""
name: createDictionaryOfVariableGroups.py

date: 2/12/2014

@author: Misha

description: This script goes through rawVariableGroupsTree.pickle and replaces
all situations where there is {varName : None} with varName.
"""
import numpy as np
import cPickle as cp
from collections import defaultdict

def parseTree(currentDict):
    
#   if type(currentDict) == str: return
  
    # if all values are unicode (the variable names)
    if np.array([type(el)==unicode for el in currentDict.values()]).all():
        currVarGroup = set(currentDict.values())
        for v in currVarGroup:
            v = v.upper()
            currVarGroup = set(map(unicode.upper, currVarGroup))            
            varGroups[v].update(currVarGroup - set([v])) # convert everything to uppercase

    else:    
        for k, v in currentDict.iteritems():    
            # with the if statement below, i am skipping all branches in the variable
            # tree which end at an intermediate level (where there are other deeper branches)
            # for OTHER variables on the same level
            if type(v) == dict:   
                parseTree(v)       
 
    


if __name__ == "__main__":    
    
    # define variables
    pathToData = '../data/'
    rawTree = cp.load(open(pathToData + 'rawVariableGroupsTree-cleaned.pickle'))
    varGroups = defaultdict(set)

    # fill out cognateVariables dict
    for letter in rawTree:
        print 'processing letter', letter
        if rawTree[letter] is None or len(rawTree[letter]) < 1:
            print 'No data for this letter. Skipping...'
            continue
        else: parseTree(rawTree[letter])    
    
    # get rid of situations where {variable : empty set}. There are ~30 cases like this.
    varGroups = dict([(k, v) for k, v in varGroups.iteritems() if len(v) > 0])    
    
    cp.dump(varGroups, open(pathToData + 'dictOfVariableGroups.pickle', 'wb'))