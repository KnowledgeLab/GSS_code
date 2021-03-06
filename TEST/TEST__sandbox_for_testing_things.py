
# coding: utf-8

# In[1]:

get_ipython().magic(u'matplotlib inline')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
sys.path.append('../')    
import GSSUtility as GU
import statsmodels.formula.api as smf
from pandas.rpy import common as com


# In[2]:

get_ipython().magic(u'rm ../GSSUtility.pyc # remove this file because otherwise it will be used instead of the updated .py file')
reload(GU)


# In[3]:

pathToData = '../../Data/'
dataCont = GU.dataContainer(pathToData)


# In[3]:

def independent_columns(A, tol = 1e-05):
    """
    Return an array composed of independent columns of A.

    Note the answer may not be unique; this function returns one of many
    possible answers.

    http://stackoverflow.com/q/13312498/190597 (user1812712)
    http://math.stackexchange.com/a/199132/1140 (Gerry Myerson)
    http://mail.scipy.org/pipermail/numpy-discussion/2008-November/038705.html
        (Anne Archibald)

    >>> A = np.array([(2,4,1,3),(-1,-2,1,0),(0,0,2,2),(3,6,2,5)])
    >>> independent_columns(A)
    np.array([[1, 4],
              [2, 5],
              [3, 6]])
    """
    Q, R = np.linalg.qr(A.dropna())
    independent = np.where(np.abs(R.diagonal()) > tol)[0]
    print independent
    return A.iloc[:, independent]


# In[3]:

import pandas as pd
import numpy as np
import rpy2.robjects as robjects
r = robjects.r
from rpy2.robjects import pandas2ri
pandas2ri.activate()
import pandas.rpy.common as com
# import GSSUtility as GU
from rpy2.robjects.packages import importr
# R's "base" package
amelia = importr('Amelia')
mi = importr('mi')
mi = r['mi']
df = pd.read_csv('../../Data/test_collinear.csv', index_col=0)
# df.index = range(len(df))


# In[36]:

articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, centralIVs=True)
article = [a for a in articlesToUse if a.articleID == 7449][0]


# In[37]:

import random
print [a.articleID for a in random.sample(articlesToUse, 20)]


# In[38]:

article.IVs, article.DVs, article.centralIVs, article.GSSYearsUsed


# In[14]:

formula2 = '''
standardize(FUND, ddof=1) ~ C(RELIG)'''
DV = article.DVs[0]


# In[42]:

design = dataCont.df.loc[1973, [DV] + article.IVs]
design.index = range(len(design))
design.head()


# In[17]:

# mi(com.convert_to_r_dataframe(design))


# In[30]:

# summary = r['summary']


# In[18]:

# print r('summary(imp$imp)')


# In[19]:

# print com.convert_robj(r['imp1']).DEGREE.value_counts()
# print
# print design.DEGREE.value_counts()


# In[20]:

# rcode='''
#     library(mi)
#     mydf = %s
#     IMP = mi(mydf, n.imp=2, n.iter=6, max.minutes=1)
#     imp1 <- mi.data.frame(IMP, m = 1)
# ''' % com.convert_to_r_dataframe(design).r_repr()
# r(rcode)
# com.convert_robj(r['imp1'])


# In[45]:

res=GU.runModel(dataCont, 1973, DV, article.IVs)


# In[46]:

res.summary()


# In[43]:

for year in article.GSSYearsUsed:
    design = dataCont.df.loc[year, [DV] + article.IVs]
#     design = design.fillna(design.mean())
    formula = GU.createFormula(dataCont, design)
#     results = smf.ols(formula2, data=design.dropna()).fit()

    if len(design.dropna()) <= design.shape[1]: 
        nominals = GU.createFormula(dataCont, design, return_nominals=True)
        non_nominals = list(set(design.columns) - set(nominals)) # list because sets are unhashable and cant be used for indices
        if len(non_nominals)>0: 
            design[non_nominals] = design[non_nominals].fillna(design[non_nominals].mean()) # the naive way
        if len(nominals)>0:
            design[nominals] = design[nominals].fillna(design[nominals].mode())
    
    design = GU.removeConstantColumns(design.dropna())
    print smf.ols(formula, data=design.dropna()).fit().summary()
    break


# In[49]:

print formula
design.head()


# In[68]:

DV = 'GRASS'
for year in article.GSSYearsUsed:
    design = dataCont.df.loc[year, [DV] + article.IVs]
    design = design.fillna(design.mean())
    formula = GU.createFormula(dataCont, design)
#     results = smf.ols(formula2, data=design.dropna()).fit()
    
           
    print smf.ols(formula, data=design.dropna()).fit().summary()
# 


# In[ ]:




# In[76]:

import pandas as pd
import numpy as np
df = pd.read_csv('../../Data/test_collinear.csv', index_col=0)
from scipy.stats import pearsonr


# In[5]:

df.head()


# #Imputing with GLRM

# In[4]:

from glrm import GLRM
from glrm.loss import QuadraticLoss, HingeLoss
from glrm.reg import QuadraticReg
from glrm.convergence import Convergence


# In[80]:

get_ipython().magic(u'pinfo GLRM')


# In[5]:

regX, regY = QuadraticReg(0.01), QuadraticReg(0.01)

converge = Convergence(TOL = 1e-5, max_iters = 100)

model = GLRM(df.values, QuadraticLoss, regX, regY, k=2, converge=converge)
model.fit()

X, Y = model.factors()
A_hat = model.predict() # a horizontally concatenated matrix, not a list

norm(A_hat - hstack(A_list)) # by hand


# In[ ]:



