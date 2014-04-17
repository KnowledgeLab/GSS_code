# -*- coding: utf-8 -*-
"""
Created on Fri Apr 11 14:42:21 2014
filename: createDictOfVariableTypesFromCSV.py
@author: Misha

input: topxxxivs_CODED.csv
    this csv files has the following structure
    first 2 lines are column names and legend
    lines 3 and on are:
        VAR NAME, number of times used, TYPE, NOTES
    TYPE = {C = CONTINUOUS, CL=CONTINUOUS-LIKE, CAT?=CATEGORICAL AND I DON'T KNOW HOW MANY LEVELS,
            # = CATEGORICAL WITH THAT MANY LEVELS}
    NOTES = sometimes there'll be a note of the form NUM=adfsdf.. and what that specifies is 
            usually the "other" category, which is not missing, but which screws up the 
            continuous-like-ness of the variable. Ex: levels 1-5 are ordinal, 6=other.


output:  = {varname:type}
"""
import cPickle as cp

pathToData = 'C:\Users\Misha\Dropbox\GSS Project\Data/'
fileName = 'top300ivs_CODED.csv'

lines = open(pathToData + fileName).readlines()
lines = lines[2:]

variableTypes = {}

for line in lines:
    if len(line.split(',')) == 4:
        varname, numused, vartype, notes = line.split(',')
    else:
        varname, numused, vartype = line.split(',')
        notes = ''       
    
    # in the types, include a type called 'DONOTUSE' which will be assigned to all variables
    # of type 'CAT?' and those where the "notes" field includes the characters "#=...."    
    if notes[0].isdigit() and notes[1]=='=': vartype = 'DONOTUSE'
    if vartype == 'CAT?': vartype = 'DONOTUSE'    
    
    # convert integer variable types (where int = how many levels) to actual ints
    if vartype[0].isdigit(): vartype = int(vartype)    

    variableTypes[varname] = vartype
    
cp.dump(variableTypes, open(pathToData + 'variableTypes.pickle', 'wb'))

