# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 16:41:57 2013

important notes and to-do's
 - 9/20/2013
 - currently i'm  skipping all variables that have a modal code of "don't know". . but should I be skipping ARTICLES where at least
 one variable is "don't know"? because it seems even worse to include only SOME of the variables from those articles, which is what
 i'm doing now. hmmmmm.
    - let me try that now (9/20/2013), to include all variables, regardless of "don'tknow" and see how results change..
 
 
modified: 9/20/2013
  - amended code so that it also retrieves from the database whether a variable is coded as "central" or not
  - includes in the resulting dictionary, for each article, the dict returned now has a new key "centralIVs"
  
@author: Misha Teplitskiy

filename: build_database_of_articles_and_variables.py

description: accesses the GSS mysql database, queries gss_variable_ques_modal table to get info on each article's variables
creates a dictionary (pickled at the end) where key=article ID : value={ key=variable type : list of such variables}

input: 

output: pickle file containing the dictionary described above

"""
import sys
import MySQLdb
import cPickle as cp


#connect to MySQL database lanl
try:
	conn=MySQLdb.connect(port=3007, unix_socket="/mnt/ide1/mysql/var/mysql.sock1", user="misha", passwd="p0ly4",db="lanl")

except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit (1)
    
try:
    cursor = conn.cursor ()

    #Retrieve node and edge list, this is 56K results
    query = '''
    SELECT true_article_id, var_name, var_dependent, var_independent, var_control, var_central, var_dontknow 
    FROM gss_variable_ques_modal;
    	'''
    cursor.execute(query)	
    results=cursor.fetchall()
     
    # save the results
    cp.dump(results, open('../Data/gss_variable_ques_modal_rows.pickle', 'w'))
     
    #process the results and store them in varsInArticle
    varsInArticle = {}     
    
    listOfDVs, listOfIVs, listOfControls, listOfCentralIVs = [], [], [], []
    i = 0
    
    while True:
        
        row = results[i]
        articleID, varName, varDependent, varIndependent, varControl, varCentral, varDontknow = tuple(row)
        
        # for each suitable line
        #if varDontknow == '':
        if varDependent == 'True':
            listOfDVs.append(varName)
        elif varIndependent == 'True':
            listOfIVs.append(varName)          
            if varCentral == 'True': listOfCentralIVs.append(varName)
        elif varControl == 'True':
            listOfControls.append(varName)       
 
        if i+1 < len(results) and results[i+1][0] != articleID: # if next row deals with a new true_article_id
            varsInArticle[articleID] = {'dvs':listOfDVs, 'ivs':listOfIVs, 'centralIVs':listOfCentralIVs, 'controls':listOfControls} # do i need to make deep copies here??
            listOfDVs, listOfIVs, listOfCentralIVs, listOfControls = [], [], [], []
            
        if  i == len(results)-1: # if finished processing the results, quit
            break
        
        i+=1
    
    cp.dump(varsInArticle, open('../Data/VARS_IN_ARTICLE-9-20-2013.pickle', 'wb'))
        
    # for each new true_article_id
        
            
  



except MySQLdb.Error, e:
     print "Error %d: %s" % (e.args[0], e.args[1])
     sys.exit (1)

conn.close ()
sys.exit (0)    
