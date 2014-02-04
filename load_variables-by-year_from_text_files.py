"""
Created on Thu Aug 29 15:26:35 2013

@author: Misha

filename: load_variables-by-year_from_text_files.py

description: This program goes through a directory containing text files with GSS variable names and variable metadata and 
loads them into a dictionary {year : list of variables, etc.}

input: directory name that contains file names of format "19xxvariables.txt"
Each of these text files contains information on the variables in that GSS dataset from year xxxx and
some other info on each variable

output: pickle file containing the dictionary described above
	currently, the dictionary looks like this:
	{ year (int) : [ set of variable names (strs), [variable_i, metadata_i] ] } 

"""

import os
import numpy as np

directory = '../Data/variables_by_year/'
filenames = os.listdir(directory)

VARS_BY_YEAR = {}

for filename in filenames:
    year = int(filename[:4])  # first 4 characters of the filename are the year of the GSS   
    varsAndMetadata = []

    rawfile = open(directory + filename)
    rawlines = rawfile.readlines()
    rawfile.close()
    
   
    for line in rawlines:
        columns = line.strip().split('\t')  # strip the newline character from the end and split on tab 
        variable = columns[0]
        varType = columns[-1].lower() # data type of the variable. make sure it's lower case
        varsAndMetadata.append([variable, varType])
        
    setOfVariableNames = set( np.array(varsAndMetadata)[:,0] )
    VARS_BY_YEAR[int(year)] = [setOfVariableNames, varsAndMetadata]
    
import cPickle as cp
cp.dump(VARS_BY_YEAR, open('C:/Users/Misha/Dropbox/GSS Project/Data/VARS_BY_YEAR.pickle', 'wb'))

       
    