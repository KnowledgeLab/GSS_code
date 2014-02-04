#
# 	name: get_descriptives_of_network.py
# 	author: Misha Teplitskiy
#	date: 12-24-12
#
#	description: Calculate varous descirptions of the network
#
#	12-28-12
#		- working on descriptives of bi-directional links in network
#


g = load(open('graphG.pickle'))

'''
# degree distribution of nodes
degrees = sorted(g.degree().items(), key=lambda elem: elem[1], reverse=True)
'''

numberOfEdges = []
for node, nbrsdict in g.adjacency_iter():
	for nbr in nbrsdict.keys():
		numberOfEdges.append( (g.number_of_edges(node, nbr), node, nbr ))

print 'About to generate undirNumberOfEdges list'
edgesList = g.edges()[:]
undirNumberOfEdges = [] # this list will include only bi-directional edges, the number of edges will be total in both directions
for e in numberOfEdges.__iter__():
	if (e[2], e[1]) in edgesList: # if the edge in the other direction exists as well
		totalEdges = e[0] + g.number_of_edges(e[2], e[1])
		undirNumberOfEdges.append((totalEdges, e[1], e[2])) 


##############################
# bidirectionals analysis 

print 'About to sort and create listForAnalysis'		
# sort and create list for analysis
nOfESorted = sorted(undirNumberOfEdges, reverse=True)
indexToStop = [e[0] for e in nOfESorted].index(9) # edges that appear a TOTAL of XXX or more times
listForAnalysis_withDoubles = nOfESorted[:indexToStop] 

# drop doubles, which WILL be in there for every node pair
listForAnalysis = []
for e in listForAnalysis_withDoubles:
	if (e[0], e[2], e[1]) in listForAnalysis or (e[0], e[1], e[2]) in listForAnalysis : continue
	else: listForAnalysis.append(e)
	
# n(-->)/total > x%  means that 
bidirectionals = []
for e in listForAnalysis: # e's are tuples (number of edges, fromNode, toNode)
	if g.number_of_edges(e[2], e[1]) >= 2 and g.number_of_edges(e[1], e[2]) >= 2: # this is a condition that requires the proportion of links that are in a given direction
		bidirectionals.append(e)
		
for e in bidirectionals:
	print  e[1], '-->', e[2], ':', g.number_of_edges(e[1], e[2]), '\t\t', e[2], '-->', e[1], ': ', g.number_of_edges(e[2], e[1])