#! /usr/bin/python

########################################
#
# 	create_network.py
#
#	12/14/2012
#
#	by Misha Teplitskiy
#	
#	Description: Creates a MultiDiGraph network from the edgesquery.pickle file
#
#	output: graphG.pickle
#
########################################

from cPickle import *
import networkx as nx

rawnodes = load(open('raw_data_on_variables_7-8-2013.pickle')) # ~20K entries
rawedges = load(open('raw_data_on_edges_7-8-2013.pickle')) # ~20K entries

#  A.true_article_id, A.var_name, B.var_name

# build network (NetworkX format)
G = nx.MultiDiGraph()


for count, line in enumerate(rawedges):
	# each line in raw, which is a tuple of tuples, looks like this: 
     # (true_article_id, var_name, var_control, var_central, var_dependent, var_independent, var_dontknow)
	# so, the TO node (dep variable) comes first, and the FROM node (indep var) comes second
	# yearPublished and monthPublished may be NULL?
	
	# get nodes 
	articleID, toNode, fromNode = line 
	
	G.add_edge(fromNode, toNode)
	
	''' THIS IS THE OLD WAY OF DOING IT, IN AN UNDIRECTED NETWORK
	# IF NODE(s) NOT IN NETWORK YET
	if node1 not in G:
		G.add_node(node1, freq=1, types={node1type : 1, list(nodetypes-set([node1type]))[0]:0, list(nodetypes-set([node1type]))[1]:0})	
	else: 
		G.node[node1]['freq'] = G.node[node1]['freq'] + 1
		G.node[node1]['types'][node1type] = G.node[node1]['types'][node1type] + 1  # The variable is used as a "control/IV/DV" one more time
	
	if node2 not in G:
		G.add_node(node2, freq=1, types={node2type : 1, list(nodetypes-set([node2type]))[0]:0, list(nodetypes-set([node2type]))[1]:0})	
	else:
		G.node[node2]['freq'] = G.node[node2]['freq'] + 1
		G.node[node2]['types'][node2type] = G.node[node2]['types'][node2type] + 1  # The variable is used as a "control/IV/DV" one more time
			
	# EDGE attributes
	year = line[8] # year_published
	if (node1, node2) in G.edges() : # if edge is already in network 
		G[node1][node2]['weight'] = G[node1][node2]['weight'] + 1  # increase edge weight if edge already in network # are edges stored symmetrically??
		years = G[node1][node2]['years']
		if year in years : years[year] = years[year]+1
		else : years[year] = 1
	else : # if edge is not in network
		G.add_edge(node1, node2, weight=1, years={year : 1}) # set the default edge weight at 1, year to 1 (edge published in this year 1 time)
	'''
	
	if count%10000 == 0 : print(str(line) + '\n')

dump(G, open('graphG.pickle', 'w'))


