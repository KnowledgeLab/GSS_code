# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 16:27:04 2013

@author: Misha

outputs:
articleIDAndGSSYearsUsed - dictionary where the key is the article id and value is a string of integers of the GSS years used.
Dictionary includes ONLY those items for which there were very clear GSS years used. Articles with uclear gss years are not included.
"""

import cPickle as cp

GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 1980, 1982,  
                 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991,
                 1993, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010,
                 2012]

pathToData = 'C:/Users/Misha/Dropbox/GSS Project/Data/'
articleIDAndGSSYearsUsedUncleaned = cp.load(open(pathToData + 'articleIDAndGSSYearsUsed-uncleaned.pickle'))

articleIDAndGSSYearsUsed = {}

for row in articleIDAndGSSYearsUsedUncleaned:
    
    articleID, yearsUncleaned = row[0], row[1]
    yearsCleaned = []    # for each article, start with an empty list of GSS years used
 
    print 'yearsUncleaned:', yearsUncleaned
   
    yearsUncleaned = yearsUncleaned.lower().strip().replace('"', '') # lower-case, get rid of trailing spaces and get rid of quotes
    
    # CASE 1: beginning of yearsUncleaned is one of those rows where there's a textual explanation, which seems to always begin with "ACT:" 
    #treat it as if we have no info (don't even put it in the dictionary)
    if yearsUncleaned[:3] == 'act' : continue
   
   # CASE 2: the entire string is less than 4 characters
    if len(yearsUncleaned) < 4:
        print yearsUncleaned
        continue

    # Putting the commands below in a "try" statement because in some instances the GSS year given is 
    # mistaken, because that year doesn't exist. In such cases, the way the exception is handled
    # is simply with a "continue" statement -- the article is skipped (not added to the dictionary)
    # and we move on to the next one     
    try:         
        # split on commas and strip whitespaces
        yearsSplitOnCommas = [e.strip() for e in yearsUncleaned.split(',')]
        for rangeOfYears in yearsSplitOnCommas:
            # Is there a dash? Three formats: 1991-1992 OR 1991-92 OR 1991-2
            if '-' in rangeOfYears:
                yearsSplitOnDash = rangeOfYears.split('-')
    
                # error check:
                if len(yearsSplitOnDash[0]) != 4:
                    print yearsSplitOnDash
                    raise 
                    
                startOfRange = yearsSplitOnDash[0] # the first 4 numbers
                charsToAdd = 4 - len(yearsSplitOnDash[1]) 
                endOfRange = startOfRange[:charsToAdd] + yearsSplitOnDash[1] # characters from beginning of range added to end of range
                
                startIndex = GSS_YEARS.index(int(startOfRange))
                endIndex = GSS_YEARS.index(int(endOfRange))
                
                yearsCleaned.extend( GSS_YEARS[startIndex:endIndex+1] )
            else: # no dash
                # is the string in appropriate year range?
                if int(rangeOfYears) not in GSS_YEARS:
                    print 'rangeOfYears not in GSS_YEARS', rangeOfYears
                    raise 
                else:
                    yearsCleaned.append(int(rangeOfYears))                
    except ValueError: # if there is any kind of error regarding the year of the article not being in the available years (GSS_YEARS), skip this article
        continue
    
    # finally add the parsed years to the dictionary                    
    articleIDAndGSSYearsUsed[int(articleID)] = yearsCleaned 

    
cp.dump(articleIDAndGSSYearsUsed, open(pathToData + 'articleIDAndGssYearsUsed-cleaned.pickle', 'w'))