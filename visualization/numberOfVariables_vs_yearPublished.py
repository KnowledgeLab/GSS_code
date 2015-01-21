# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 14:33:43 2014

@author: Misha
"""

import pandas as pd
import cPickle as cp
import sys
sys.path.append('../')
import GSSUtility
import numpy as np

path_to_data = 'C:\Users\Misha\Dropbox\GSS Project\Data/'
articleToUse = cp.load(open(path_to_data + 'articleClasses.pickle'))
articleClasses = pd.DataFrame(columns=['aid', 'yearpublished', 'dvs', 'ivs', 'controls'])
for a in articleClasses:
    df.loc[a.articleID, :] = np.array([a.articleID, a.yearPublished, a.DVs, a.IVs, a.controls], dtype=object)

df.yearpublished = df.yearpublished.astype(int)
df.aid = df.aid.astype(int)
df.index = df.aid
    
df.dvs = [len(v) for k, v in df.dvs.iteritems()]
df.ivs = [len(v) for k, v in df.ivs.iteritems()]
df.controls = [len(v) for k, v in df.controls.iteritems()]

grouped = df.groupby('yearpublished')
grouped.mean()[['dvs', 'ivs', 'controls']].plot()

