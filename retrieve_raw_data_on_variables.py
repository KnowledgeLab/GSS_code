#! /usr/bin/python

########################################
#
# 	name: retrieve_raw_data_on_variables.py
#
#	created: 7/8/2013
#
#	author: Misha Teplitskiy
#	
#	Description: Sends a MySQL query and saves the results to a pickle. The query is pump the
#       entire table gss_variable_ques_modal into the pickle.

#	Assumptions: Script is intended to be run on server, Rhodesx)
#
#
#
#	return: saves a pickle file "raw_data_on_variables_7-8-2013.pickle"
#       each row of the pickle file has the following columns:
#       (true_article_id, var_name, var_control, var_central, var_dependent, var_independent, var_dontknow)
#
########################################

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

	#Retrieve the nodes and info about them, this is 56K results
	sql = '''
	SELECT * FROM gss_variable_ques_modal;
	'''
	cursor.execute(sql)	
	nodesquery=cursor.fetchall()
 
     # Retrieve the EDGES  ~280K
	sql = '''
	SELECT A.true_article_id, A.var_name, B.var_name \
     FROM gss_variable_ques_modal A
     INNER JOIN gss_variable_ques_modal B
     ON A.true_article_id = B.true_article_id
     AND A.var_name < B.var_name;
     '''
	cursor.execute(sql)	
	edgesquery=cursor.fetchall()
     

	# save query results (pickle format)
     dump(nodesquery, open('raw_data_on_variables_7-8-2013.pickle', 'w'))	
     dump(edgesquery, open('raw_data_on_edges_7-8-2013.pickle', 'w'))


except MySQLdb.Error, e:
     print "Error %d: %s" % (e.args[0], e.args[1])
     sys.exit (1)

conn.close ()
sys.exit (0)

