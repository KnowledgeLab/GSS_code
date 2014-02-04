# -*- coding: utf-8 -*-
"""
Created on Sat Sep 07 17:12:58 2013

@author: Misha

description: This utility program creates the data structures VAR_INDICES and YEAR_INDICES.
YEAR_INDICES is a dictionary (of dictionaries) where {key=year : value = {key='startInd' : value, key='endInd' : value]}, where startInd and
endInd are (row) indices in the entire GSS where each year's rows (in the full matrix) start and end.

inputs:
- 'ALL_VARIABLE_NAMES.pickle'
- 'YEARS_COLUMN.pickle'


outputs:
YEAR_INDICES = {}
VAR_INDICES={}

"""

import cPickle as cp

pathToData = '../Data/'  # setting this to nothing because it will be run from the server from the data directory. if running on local machine, will need to change

yearsCol = cp.load(open(pathToData + 'YEARS_COLUMN.pickle'))
varNames = cp.load(open(pathToData + 'ALL_VARIABLE_NAMES.pickle'))
GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 
			1980, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 
			1990, 1991, 1993, 1994, 1996, 1998, 
			2000, 2002, 2004, 2006, 2008, 2010, 2012]
   
   

VARIABLE_COLUMNS={}
YEAR_INDICES = {}
VAR_INDICES={}

# CREATE YEAR_INDICES
# create a dictionary with indices for where each year's row starts and ends
startInd, endInd = 0, 0
for year in GSS_YEARS:
    startInd = endInd
    endInd = startInd + yearsCol.count(year)
    YEAR_INDICES[year] = {'startInd':startInd, 'endInd':endInd}
cp.dump(YEAR_INDICES, open(pathToData + 'YEAR_INDICES.pickle', 'w'))

# CREATE VAR_INDICES
for i, var in enumerate(varNames):
    VAR_INDICES[var.upper()] = i
    
cp.dump(VAR_INDICES, open(pathToData + 'VAR_INDICES.pickle', 'w'))
