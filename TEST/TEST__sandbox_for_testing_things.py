
# coding: utf-8

# In[12]:

get_ipython().magic(u'matplotlib inline')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
sys.path.append('../')    
import GSSUtility as GU
import statsmodels.formula.api as smf


# In[3]:

pathToData = '../../Data/'
dataCont = GU.dataContainer(pathToData)


# In[6]:

# import pandas as pd
# import numpy as np
# import rpy2.robjects as robjects
# r = robjects.r
# from rpy2.robjects import pandas2ri
# pandas2ri.activate()
# import pandas.rpy.common as com
# # import GSSUtility as GU
# from rpy2.robjects.packages import importr
# # R's "base" package
# amelia = importr('Amelia')
df = pd.read_csv('../../Data/test_collinear.csv', index_col=0)
# df.index = range(len(df))


# In[7]:

articlesToUse = GU.filterArticles(dataCont.articleClasses, GSSYearsUsed=True, GSSYearsPossible=False, centralIVs=True)
article = [a for a in articlesToUse if a.articleID == 7746][0]


# In[9]:

article.IVs, article.GSSYearsUsed


# In[11]:

GU.runModel(dataCont, 1989, 'SATJOB', article.IVs)


# In[17]:




# In[21]:

design = dataCont.df.loc[1989, ['SATJOB'] + article.IVs]
formula = GU.createFormula(dataCont, design)
results = smf.ols(formula, data=design.dropna()).fit()
results.summary()


# In[30]:

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


# In[4]:

import pandas as pd
import numpy as np
df = pd.read_csv('../Data/test_collinear.csv', index_col=0)
from scipy.stats import pearsonr


# In[5]:

df.head()


# In[176]:




# In[177]:



