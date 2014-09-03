# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 14:33:43 2014

@author: Misha
"""

df = pd.DataFrame(columns=['aid', 'yearpublished', 'dvs', 'ivs', 'controls'])
for a in articlesToUse:
    df.loc[a.articleID, :] = np.array([a.articleID, a.yearPublished, a.DVs, a.IVs, a.controls], dtype=object)

df.yearpublished = df.yearpublished.astype(int)
df.aid = df.aid.astype(int)
df.index = df.aid
    
df.dvs = [len(v) for k, v in df.dvs.iteritems()]
df.ivs = [len(v) for k, v in df.ivs.iteritems()]
df.controls = [len(v) for k, v in df.controls.iteritems()]

grouped = df.groupby('yearpublished')
grouped.mean()[['dvs', 'ivs', 'controls']].plot()

