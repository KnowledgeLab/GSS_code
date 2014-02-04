# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 16:27:04 2013

name: retrieve_article_id_model_and_gss_central_varialbe_from_database.py
@author: Misha
"""


# hoursWorked: started at 3:20


from cPickle import dump
import MySQLdb
import sys
#import networkx as nx

# connect to the MySQL server
try:
	conn=MySQLdb.connect(port=3007, unix_socket="/mnt/ide1/mysql/var/mysql.sock1", user="misha", passwd="p0ly4",db="lanl")

except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit (1)

try:
	cursor = conn.cursor ()

     # the result of this query will have multiple coder's answers for each article
	sql = '''
     SELECT true_article_id, model, gss_central_variable FROM gss_question;
	'''
	cursor.execute(sql)	
	articleIdModelGssCentralVariable=cursor.fetchall()

	# save backup of query results (pickle format)
	dump(articleIdModelGssCentralVariable, open('articleIdModelGssCentralVariable.pickle', 'w'))
 
     #-------------------------------

	sql = '''
     SELECT true_article_id, other_datasets FROM gss_corpus;
	'''
	cursor.execute(sql)	
	articleIdOtherDatasets=cursor.fetchall()

	# save backup of query results (pickle format)
	dump(articleIdOtherDatasets, open('articleIdOtherDatasets.pickle', 'w'))
 
 

except MySQLdb.Error, e:
     print "Error %d: %s" % (e.args[0], e.args[1])
     sys.exit (1)

conn.close ()
sys.exit (0)
