#! /usr/bin/python

########################################
#
# 	create_network.py
#
#	11/21/2012
#
#	by Misha Teplitskiy
#	
#	Description: Sends a MySQL query and saves the results to a pickle. This gets all results matching the following pattern:
#		(DEP variable name, INDEP or CTRL variable name, YEAR published, MONTH published)
#	Assumptions: A few, noted in the lab notebook for entry under 12-14-12
#
#
#	PROBLEM!!!!! : 12-30-12: THIS QUERY SEEMS TO ONLY GET RESULTS WHICH ARE HAVE YEAR (AND MONTH) AS NOT NULL???
#					THIS IS A PROBLEM BECAUSE THERE IS NO YEAR DATA FOR MOST OF THE EDGES!!! (BUT NOT A PROBLEM FOR DISTANCE DISTR, WHERE YEAR
#					IS NECESSARY
#
#	return: saves a pickle file "edgesquery.pickle"
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

	#Retrieve node and edge list, this is 56K results
	sql = '''
	SELECT A.var_name, 
		   B.var_name,
		   C.year_published, C.month_published  
	FROM gss_variable_ques AS A
	INNER JOIN gss_variable_ques AS B
	ON A.true_article_id = B.true_article_id
	INNER JOIN gss_corpus C
	ON B.true_article_id = C.true_article_id
	WHERE A.posterior_Model = 0 AND (B.posterior_Model = 2 OR B.posterior_Position = 2)
	GROUP BY A.true_article_id, A.var_name, B.true_article_id, B.var_name;
	'''
	
	cursor.execute(sql)	
	edgesquery=cursor.fetchall()

	# save backup of query results (pickle format)
	dump(edgesquery, open('edgesquery.pickle', 'w'))


except MySQLdb.Error, e:
     print "Error %d: %s" % (e.args[0], e.args[1])
     sys.exit (1)

conn.close ()
sys.exit (0)

