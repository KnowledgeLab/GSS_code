"""
Created on Thu Aug 29 15:26:35 2013

@author: Misha

filename: load_variables_from_yearly_stata_files.py

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
import pandas as pd
import cPickle as cp

directory = '../Data/GSS Dataset/stata/'
filenames = os.listdir(directory)

VARS_BY_YEAR = {}

for filename in filenames:

    print 'Processing', filename
    
    year = int(filename[3:7])  # filenames are GSSxxxx.dta, and I only want the xxxx   
    stataFile = pd.read_stata(directory + filename)
    variables = set(map(str.upper, stataFile.columns))
    
    VARS_BY_YEAR[year] = variables
    
cp.dump(VARS_BY_YEAR, open('C:/Users/Misha/Dropbox/GSS Project/Data/VARS_BY_YEAR.pickle', 'wb'))

       
    