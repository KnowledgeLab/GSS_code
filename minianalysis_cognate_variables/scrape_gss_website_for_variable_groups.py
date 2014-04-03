# -*- coding: utf-8 -*-
"""
Created on Thu Dec 05 17:44:56 2013

@author: Misha
"""

import re, urllib2
from bs4 import BeautifulSoup as bs

indextext='''
	  <li>
    <a href="/webview/velocity?study=http%3A%2F%2Fpublicdata.norc.org%3A80%2Fobj%2FfStudy%2F4697&amp;v=2&amp;mode=documentation&amp;submode=section&amp;section=http%3A%2F%2Fpublicdata.norc.org%3A80%2Fobj%2FfSection%2F4697_VG5116">Z</a>
'''
topics = dict()

# indextext is the webpage with each letter (starting letter of topic names)
indexsoup = bs(indextext)

# problem is i can't predict how many levels there are to the tree!
# some topics, like abortion, have like 3 levels!!!

absolutePath = 'http://publicdata.norc.org'

from collections import defaultdict
def tree(): return defaultdict(tree)

myTree = dict()
currentDict = dict()
currentList = list()        

def parseTree(address, level):
    # categorize the current page
    # if there's more after it, get the name of the thing and parse again
    currentNode = bs(urllib2.urlopen(address).read())
    leaves = currentNode.select('ul li a') # for each topic name
    
    # if have reached ultimate leaf    
    if len(leaves) == 0:    
            
        # get variable name
        try: varLine = currentNode.select(".variable")[0].text
        except:
            print address
            return 'ERROR: NO VARIABLE ENTRY FOR THIS TOPIC'
            
        varName = varLine.split()[1] # the first element should be the word 'Variable'
        print 'varname:', varName        
        return varName.lower()
    
    else: # if have not reached end of tree
        currentDict = dict()

        for leaf in leaves:
            if 'See' in leaf.text: 
                print 'whoaaaaaa SKIPPING', leaf # what to do with this case??               
                continue
            
            elif leaf.text.isupper() and level > 2: # next page will be the variable
                print 'next page should be for the variable'
                print leaf.text
                currentDict[parseTree(absolutePath + leaf['href'], level)] = None # this should return the variable name
            
            else:
                currentDict[leaf.text.lower()] = parseTree(absolutePath + leaf['href'], level=level+1) # this sometimes returns the variable name!?                
        
        return currentDict



for letter in indexsoup.find_all('a'): # for each letter
    #letterPage = bs(urllib2.urlopen(absolutePath + letter['href']).read()) # page for that letter
    myTree[letter.text] = parseTree(absolutePath + letter['href'], 1)   

'''
for letter in indexsoup.find_all('a'): # for each letter
    
    letterPage = bs(urllib2.urlopen(absolutePath + letter['href']).read()) # page for that letter

    for topic in letterPage.select('ul li a'): # for each topic name

        # get the topic name
        topicName = topic.text 

        # now to get the variables associated with that topic..
        topicPage = bs(urllib2.urlopen(absolutePath + topic['href']).read())
        print topicPage.select('ul li a')

        break
    break
'''