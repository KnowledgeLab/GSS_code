# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import cPickle as cp
import pandas as pd
import networkx as nx
from itertools import combinations 

# <codecell>


# <codecell>

# GLOBALS
GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 
            1980, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 
            1990, 1991, 1993, 1994, 1996, 1998, 
            2000, 2002, 2004, 2006, 2008, 2010, 2012]

pathToData = '../Data/'  
   
# LOAD DATA ###########################
VARS_IN_ARTICLE = cp.load(open(pathToData + 'VARS_IN_ARTICLE-9-20-2013.pickle', 'rb')) # load the variables used

# <codecell>


# <codecell>

G = nx.Graph()

for variables in VARS_IN_ARTICLE.itervalues():
    dvs = variables['dvs']
    for combo in combinations(dvs, 2):
        if G.has_edge(*combo):
            G[combo[0]][combo[1]]['weight'] += 1
        else:
            G.add_edge(*combo, weight=1)    

# <codecell>

import community

dir(community)

# <codecell>

elarge=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] > 10]

G_large = nx.Graph(elarge)

nx.draw(G_large)
# pos=nx.spring_layout(G) # positions for all nodes

# # nodes
# nx.draw_networkx_nodes(G,pos,node_size=700)

# edges

# labels
# nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')

