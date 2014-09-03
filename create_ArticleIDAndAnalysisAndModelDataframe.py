# -*- coding: utf-8 -*-
"""

filename: create_ArticleIDAndAnalysisAndModelDataframe.py
Created on Thu Jun 12 13:32:03 2014

description:
 1. open the dump from the mysql query: 
     mysql -u misha -p -P3307 --socket=/mnt/ide1/mysql/var/mysql.sock1 lanl --execute='select true_article_id, analysis, model, userid, author_id from gss_question' > ARTICLEID_AND_ANALYSIS_AND_MODEL_USED_query.txt
 2. Get the majority code for mode of analysis
 
@author: Misha
"""

import cPickle as cp
import pandas as pd

# mysql command used to get the relevant columns of gss_question:
#
# output is stored in:

pathToData = 'C:/Users/Misha/Dropbox/GSS Project/Data/'
queryFile = open(pathToData + 'ARTICLEID_AND_ANALYSIS_AND_MODEL_USED_query.txt')
# the format of this file is:
# first line: names of the columns 
# second line and on: true_article_id, analysis, model, userid, author_id
# (user id is the student coder's id and author_id, i assume, is the actual paper's author)
queryLines = queryFile.readlines()[1:]
queryFile.close()

queryLines = [line.strip().split('\t') for line in queryLines]
df = pd.DataFrame(data=queryLines, columns=['articleID', 'analysis', 'model', 'userid', 'author_id'])
df.articleID = df.articleID.astype(int)
df.index = df.articleID

dfmajority = pd.Series(data=False, index=df.articleID.unique())
'''
df = pd.DataFrame(columns=['articleID', 'analysis', 'mode', 'userid', 'author_id'])
for line in queryLines:
    lineEls = line.strip().split('\t')    
    #df.loc[int(lineEls[0]), :] = [int(lineEls[0])] + lineEls[1:]
    df.append([int(lineEls[0])] + lineEls[1:])
'''

grouped = df.groupby('articleID')
groupedcount = grouped.model.value_counts()
#df['majority'][df['model'][grouped.count().model==1] == 'Linear_NonLinear'] = 'Linear_NonLinear'

for aid in groupedcount.index.levels[0]: #aid = articleID   
    if len(groupedcount.loc[aid]) == 1 or groupedcount.loc[aid][0] > groupedcount.loc[aid][1]:
        if groupedcount.loc[aid].index[0] == 'Linear_NonLinear':            
            dfmajority[aid] = True 

dfmajority = dfmajority[dfmajority == True]            
cp.dump(dfmajority, open(pathToData + 'ARTICLEID_AND_TRUE_IF_LINEAR_NONLINEAR.pickle', 'wb'))



