# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 16:27:04 2013

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

	#Retrieve node and edge list, this is 56K results
	sql = '''
     SELECT true_article_id, gss_years FROM gss_corpus;
	'''
	
	cursor.execute(sql)	
	articleIDAndGSSYearsUsedUncleaned=cursor.fetchall()

	# save backup of query results (pickle format)
	dump(articleIDAndGSSYearsUsedUncleaned, open('articleIDAndGSSYearsUsed-uncleaned.pickle', 'w'))

except MySQLdb.Error, e:
     print "Error %d: %s" % (e.args[0], e.args[1])
     sys.exit (1)

conn.close ()
sys.exit (0)
