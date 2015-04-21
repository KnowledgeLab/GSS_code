
# coding: utf-8

# #UPDATE 2015-04-21:
# **This code is now in ``create_articleClasses``**
# 
# ### Explore gss_years (from gss_corpus)
# 
# ### update 9/3/2014: I'm abandoning work on this Notebook for now because the previous code did well enough (recovered ~4200), and it's a matter of cleaning up ~600 articles

# In[1]:

import pandas as pd
import seaborn
import MySQLdb


# In[3]:

db = MySQLdb.connect(host='klab.c3se0dtaabmj.us-west-2.rds.amazonaws.com', user='mteplitskiy', passwd="mteplitskiy", db="lanl")
c = db.cursor()


# In[4]:

c.execute('select true_article_id, gss_years from gss_corpus')
df = pd.DataFrame(list(c.fetchall()), columns=['article_id', 'gss_years'])
df.index = df.article_id
del df['article_id']


# In[5]:

df.head()


# In[6]:

GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 1980, 1982,  
                 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991,
                 1993, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010,
                 2012]


# In[42]:

for el in df.itertuples():
    print el
    break
    


# #Pre-process the years

# In[78]:

def f(x):  
    x = x.replace(' ', '')
    x = x.replace('"', '')
    x = x.replace('ISSP', '') # not sure if I should do this? but per 'http://publicdata.norc.org:41000/gssbeta/faqs.html#14' it seems ok
    x = x.strip()
    
    if len(x) < 4: return nan
    
#     x = ''.join([ch for ch in x if not ch.isalpha()])
    
    if x == '' or x == '0' or str(x).startswith('ACT'):
        return nan
    
    return x

df.gss_years = df.gss_years.map(f)


# In[79]:

for years in df.gss_years[df.gss_years.notnull()]:
    print years


# In[ ]:




# In[47]:

for articleID, yearsUncleaned in df.itertuples():
    
    yearsCleaned = []    # for each article, start with an empty list of GSS years used
 
    print 'yearsUncleaned:', yearsUncleaned
   
    yearsUncleaned = yearsUncleaned.lower().strip().replace('"', '') # lower-case, get rid of trailing spaces and get rid of quotes
    
    # CASE 1: beginning of yearsUncleaned is one of those rows where there's a textual explanation, which seems to always begin with "ACT:" 
    #treat it as if we have no info (don't even put it in the dictionary)
    if yearsUncleaned[:3] == 'act' : continue
   
   # CASE 2: the entire string is less than 4 characters
    if len(yearsUncleaned) < 4:
        print yearsUncleaned
        continue

    # Putting the commands below in a "try" statement because in some instances the GSS year given is 
    # mistaken, because that year doesn't exist. In such cases, the way the exception is handled
    # is simply with a "continue" statement -- the article is skipped (not added to the dictionary)
    # and we move on to the next one     
    try:         
        # split on commas and strip whitespaces
        yearsSplitOnCommas = [e.strip() for e in yearsUncleaned.split(',')]
        for rangeOfYears in yearsSplitOnCommas:
            # Is there a dash? Three formats: 1991-1992 OR 1991-92 OR 1991-2
            if '-' in rangeOfYears:
                yearsSplitOnDash = rangeOfYears.split('-')
    
                # error check:
                if len(yearsSplitOnDash[0]) != 4:
                    print yearsSplitOnDash
                    raise 
                    
                startOfRange = yearsSplitOnDash[0] # the first 4 numbers
                charsToAdd = 4 - len(yearsSplitOnDash[1]) 
                endOfRange = startOfRange[:charsToAdd] + yearsSplitOnDash[1] # characters from beginning of range added to end of range
                
                startIndex = GSS_YEARS.index(int(startOfRange))
                endIndex = GSS_YEARS.index(int(endOfRange))
                
                yearsCleaned.extend( GSS_YEARS[startIndex:endIndex+1] )
            else: # no dash
                # is the string in appropriate year range?
                if int(rangeOfYears) not in GSS_YEARS:
                    print 'rangeOfYears not in GSS_YEARS', rangeOfYears
                    raise 
                else:
                    yearsCleaned.append(int(rangeOfYears))                
    except ValueError: # if there is any kind of error regarding the year of the article not being in the available years (GSS_YEARS), skip this article
        print yearsUncleaned
    
    
    if articleID > 200:break


# In[46]:

yearsCleaned

