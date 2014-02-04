#
#	get_distribution_of_distances.py
#	
#	by: Misha Teplitskiy
# 	11-27-12
#	update: 12-24-2012
#		switched to using MultiDiGraph as the main data structure. Need to adjust the code to use this (because shortest distance is not well defined now)
#		plus, what about 
#	
#	update 1-17-2012: Treat situations in which a new node is as separate. (Previously, I had set the distance for these situations to 1)
#					Also, keep track of how many situations there are with no shortest-path. Treat these as separate as well.
#	
#
#


import networkx as nx
from cPickle import *

'''
g = load(open('graphG_with_dates.pickle'))
# Need to clean this data by getting rid of publication_year = 0 entries
print "Length of g before data-cleaning: ", len(g)

for n, nbrs in g.adjacency_iter():
	for nbr, edgeattr in nbrs.items():
		if 0 in edgeattr['years']: del edgeattr['years'][0]
		if edgeattr['years'] == {}: g.remove_edge(n, nbr) # if there is no YEAR OF PUBLICATION info, edge is useless so delete it
print "Length of g after data-cleaning: ", len(g)
'''

'''	
# need dictionary of networks
# the network in yearly_networks[year] answers the question: WHAT NETWORK EXISTED (was known) IN YEAR "YEAR"
# BIG ASSUMPTION TO MAKE HERE: should the pre-existing network be a DIRECTED one? Is it a big difference to know whether x-->y existed vs x--y?
# going to make the assumption that direction DOES NOT MATTER (because gonna have to calculate shortest paths...
yearly_networks = {}
edgeslists = {} # dict of lists of edges. I suspect this will make edges lookup later on easier.
for year in range(1979, 2005):
	yn = nx.Graph([(e[0], e[1]) for e in g.edges_iter(data=True) if e[2]['year'] <= year]) 
	yearly_networks[year] = yn
	edgeslists[year] = yn.edges()
	
# calculate distance distributions
yearly_distances = dict([(yr, []) for yr in range(1980, 2007)])
for e in g.edges_iter(data=True):
	fromNode, toNode, year = e[0], e[1], e[2]['year']
	
	# don't want to bother with calculating distance for edges that appeared too early
	if year < 1980 or year > 2006: continue
	
	# by default, set distance = 1 
	
	# if edge was not in previously, but both nodes aren't new, find shortest path between the nodes in network at year-1
	pn = yearly_networks[year-1]

	if fromNode in pn and toNode in pn :
	
		#if it's already in there, shortest path will be 1
		#try : dist = nx.shortest_path_length(pn, fromNode, toNode) # WHAT HAPPENED TO THE ISOLATES??? THERE WERE THERE BEFORE!!! that's why I added the try/except structure in the first place!
		
		dist = nx.shortest_path_length(pn, fromNode, toNode)
		
		# if there's an isolate, shortest path will be undefined. I'm  setting it to -1
		#except nx.NetworkXNoPath, e : dist = -1 

	#  at least one of the nodes is new
	else : dist = -2 
	
	yearly_distances[year].append(dist)
'''
	
# produce a graph showing 3 curves:
#	1) proportion of connections that year that involved new nodes, 2) proportion of connections that year that involved isolates,
#	3) prop either old or novel

'''
propNewNodes = []
propIsolates = []
propOldOrNovel = []
for yr in range(1980, 2006):
	propNewNodes.append( sum([1.0 for el in yearly_distances[yr] if el == -2])/len(yearly_distances[yr]) )
	propIsolates.append( sum([1.0 for el in yearly_distances[yr] if el == -1])/len(yearly_distances[yr]) )
	propOldOrNovel.append( sum([1.0 for el in yearly_distances[yr] if el > 0])/len(yearly_distances[yr]) )
plot(range(1980,2006), propNewNodes, label='NewNodes', range(1980, 2006), propIsolates, range(1980, 2006), propOldOrNovel)
'''

avgdistances=[]
import copy
ydcopy = copy.deepcopy(yearly_distances)

for yr in range(1980,2006):
	# this calculates the means without the connections using at least one novel node
	avgdistances.append(mean([e for e in yearly_distances[yr] if e>0]))
	
	'''
	# this calculates the means setting connections using at least one novel node to dist=1
	for i in range(len(ydcopy[yr])):
		if ydcopy[yr][i] == -2 :
			ydcopy[yr][i] = 1
	avgdistances.append(mean(ydcopy[yr]))
	'''