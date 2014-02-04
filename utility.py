#! /usr/bin/python

########################################
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
#	return: saves a pickle file ".........pickle"
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
	sql = '''
	SELECT true_article_id, variable
     FROM gss_varialbe_links;
	'''
	
	cursor.execute(sql)	
	edgesquery=cursor.fetchall()

	# save backup of query results (pickle format)
	dump(edgesquery, open('gss_variable_links_article_id_variable.pickle', 'w'))


except MySQLdb.Error, e:
     print "Error %d: %s" % (e.args[0], e.args[1])
     sys.exit (1)

conn.close ()
sys.exit (0)

