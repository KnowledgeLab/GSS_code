
# coding: utf-8

# #Why we don't have data beyond >2005
# 
# 1. We don't have information on GSS years used (which is fine because this we can guess) if we had variables
# 
# 2. **We don't have variables information!!!**
# 
# ---
# 
# **Old notes:the gss-years-cleaning part**
# 
# - UPDATE 2015-04-21: This code is now in ``create_articleClasses``**
# 
# - update 9/3/2014: I'm abandoning work on this Notebook for now because the previous code did well enough (recovered ~4200), and it's a matter of cleaning up ~600 articles

# In[7]:

import pandas as pd
import seaborn
import MySQLdb


# In[9]:

db = MySQLdb.connect(host='klab.c3se0dtaabmj.us-west-2.rds.amazonaws.com', user='mteplitskiy', passwd="mteplitskiy", db="lanl")
c = db.cursor()


# In[10]:

c.execute('select true_article_id, gss_years from gss_corpus')
df = pd.DataFrame(list(c.fetchall()), columns=['article_id', 'gss_years'])
df.index = df.article_id
del df['article_id']


# In[11]:

df.head()


# In[12]:

GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 1980, 1982,  
                 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991,
                 1993, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010,
                 2012]


# In[16]:

c.execute('select true_article_id, gss_years, year_published from gss_corpus')
df_years = pd.DataFrame([el for el in c.fetchall()], columns=['article_id', 'gss_years', 'year_published'])
df_years.index = df_years.article_id
df_years.gss_years = df_years.gss_years.astype(str)

# del df_years['article_id']

df_years.sort('year_published', ascending=False).head()


# In[17]:

c.execute('select * from gss_variable_ques')
# c.fetchall()
df_vars = pd.DataFrame([el for el in c.fetchall()], columns=('userid', 'author_id', 'article_id', 'var_name', 'var_control',                                                         'var_central', 'var_dependent', 'var_independent', 'var_dontknow',                                                         'var_type_majority'))
del df_vars['author_id']
del df_vars['var_type_majority']
del df_vars['userid']
df_vars.head()


# In[19]:

pd.merge(df_vars, df_years, on='article_id').sort('year_published', ascending=False)


# In[ ]:



