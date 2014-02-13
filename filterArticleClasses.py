# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 13:46:35 2014

@author: Misha

name: filterArticleClasses.py

description: This module contains a functil filterArticleClasses which goes through the 
  articleClasses.pickle (list of Classes) created by create_articleClasses and filters that list 
  further according to specified criteria (central variables, etc.)
  It is to be used to set up the data, before running the actual models.

returns: list of articleClasses that have passed the filters


"""
import sys
sys.path.append('../Code/')
from articleClass import *


def filterArticleClasses(oldGSSYearsLegit=True, newGSSYears=True, noIVs=True, noDVs=True, centralIV=False):
    '''
    This function filters the articleClasses list according to the following criteria.
    arguments:
     - noIVs: skip if no IVs specified
     - noDVs: skip if no DVs specified
     - oldGSSYearsLegit: confirm that the GSS years which the article allegedly used actually include
             the variables the article allegedly used
     - newGSSYears: skip if there are no GSS years possible besides the ones the article used
     - centralIV: skip if there is no IV(s) designated as "central"
    '''
    indicesToKeep = []
    
    for ind, article in enumerate(articleClasses):

        skip = False # this is the flag that determines whether the article fails to meet
                    # some criterion

        if oldGSSYearsLegit:    
        # check to make SURE that the GSS years the article allegedly used contain all the VARIABLES
        # the article allegedly used
            oldGSSYears = [year for year in oldGSSYears if set(IVs + DVs + controls).issubset(VARS_BY_YEAR[year])]   
            if len(oldGSSYears) == 0: skip = True # if no years used are left, skip
    	
        # skip article if there is no info on DVs or IVs
        # Should we change this to skip only if BOTH controls AND IVs are not there?
        if noDVs and not skip:
            if len(DVs) < 1: skip=True
        
        if noIVs and not skip: 
            if len(IVs) < 1: skip=True

        if newGSSYears and not skip:         
            # if there is no un-used years of GSS possible to run the data on, then just skip this article
            if len(newGSSYears) < 1: skip=True
            
        if centralIVs and not skip:    
            # if GSS is not the central dataset used then skip
            if len(centralIVs) < 1: skip=True
                   
        # if the article survived all of the checks above add it to the list
        if not skip: indicesToKeep.append(ind)
    
    return [articleClasses[ind] for ind in indicesToKeep] # return elements that have survived
                                                            # the filtering
