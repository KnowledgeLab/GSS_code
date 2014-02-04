#! /usr/bin/python

########################################
#
# 	retrieve_variable_definitions.py
#
#	12/28/2012
#
#	by Misha Teplitskiy
#	
#	
#
#	return: a dict where key = variable, value = definition
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

	#Retrieve variable names and definitions
	sql = '''
	SELECT variable, variable_label
	FROM gss_variables
	'''
	
	cursor.execute(sql)	
	query=cursor.fetchall()

	# convert to dictionary
	varsDict = dict(query)
	dump(varsDict, open('varsDict.pickle', 'w'))


except MySQLdb.Error, e:
     print "Error %d: %s" % (e.args[0], e.args[1])
     sys.exit (1)

conn.close ()
sys.exit (0)

