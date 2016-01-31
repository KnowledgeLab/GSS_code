
# coding: utf-8

# #Pull down data from ``lanl`` MySQL database and create ``articleClasses``
# 
# ##Description
# 
# Two dataframes are created
# - df_years -- (true_article_id, list of gss years)
# - df_variables -- (true_article_id, variable, variable_type)
# 
# Notes
# --
# - db is currently sitting on AWS
# 
# - Command used to dump tables from lanl database on Rhodes to be put on OSDC:
#         mysqldump -p -P3307 -u misha --socket=/mnt/ide1/mysql/var/mysql.sock1  lanl gss_question > gss_question.sql
#         
# # Tables in the ``lanl`` db
# 
# gss_corpus
# --
# This is the core table and contains information about all of the articles linked to GSS variables. Some of these are book chapters and things didn't have access to, but most we do. It also has variables that correspond to other datasets used.
# 
# Core variables:
# 
# - true_article_id
# - author_[variables]
# - title
# - publication_title
# - volume
# - year_published
# - file name (the PDF, html and/or texts associated with each of the articles examined as it exists in a file: gss_files) 
# - 'doc_type',
# - 'citation_type',
# - 'author_1_prefix',
# - 'author_1_last_name',
# - 'author_1_first_name',
# - 'author_1_middle_name',
#  'author_1_suffix',
#  'author_2_prefix',
#  'author_2_first_name',
#  'author_2_last_name',
#  'author_2_middle_name',
#  'author_2_suffix',
#  'author_3_prefix',
#  'author_3_first_name',
#  'author_3_last_name',
#  'author_3_middle_name',
#  'author_3_suffix',
# - 'title',
#  'pages',
#  'pub_id',
# - 'publication_title',
#  'publisher',
#  'volume',
# - 'year_published',
#  'month_published',
#  'publisher_country',
#  'publisher_city',
#  'state',
#  'document_name',
#  'conference',
#  'editor_first_name',
#  'editor_mi',
#  'editor_last_name',
#  'editor_2_first_name',
#  'editor_2_mi',
#  'editor_2_last_name',
# - 'gss_years',
# - 'other_datasets',
# - 'abstract',
#  'citation',
#  'brief_type',
#  'docket_number',
#  'chapter_name',
#  'edition',
#  'isbn',
# - 'variables',
#  'report_no',
# - 'file_name',
#  'file_url',
#  'file_id',
#  'unique_pub_id',
#  'round',
#  'batch',
#  'coder1',
#  'coder2',
#  'coder3',
#  'coder4',
#  'coder5',
#  'coder6',
#  'posterior_PaperCorrect',
#  'posterior_Central',
#  'posterior_Analysis',
#  'posterior_Approach'
# 
# gss_variables
# --
# gss_variable_codes
# --
# These describe the variables (and all of the answers/codes associated with each questions and their individual meanings).
# 
# gss_variable_links
# --
# This links the articles in gss_corpus with the variables used within them.
# 
# Core variables:
# 		
# - true_article_id
# - variable
# 
# gss_question
# --
# These are responses to the survey about each article
# 
# gss_variable_ques
# --
# These are responses to the survey about each variable (in each article)

# In[210]:

import pandas as pd
import cPickle as cp
import sys
sys.path.append('../')
import GSSUtility as GU
import seaborn as sns
import MySQLdb
import numpy as np
from numpy import nan
from random import sample # numpy has its own np.random.sample which works differently and overwrites "random.sample"


# In[83]:

db = MySQLdb.connect(host='klab.c3se0dtaabmj.us-west-2.rds.amazonaws.com', user='mteplitskiy', passwd="mteplitskiy", db="lanl")
c = db.cursor()


# #Old approach - weighted majority vote
# ###Get The Variables

# In[147]:

# OLD APPROACH
c.execute('select * from gss_variable_ques')
# c.fetchall()
df = pd.DataFrame([el for el in c.fetchall()], columns=('userid', 'author_id', 'article_id', 'var_name', 'var_control',                                                         'var_central', 'var_dependent', 'var_independent', 'var_dontknow',                                                         'var_type_majority'))
del df['author_id']
del df['var_type_majority']
df = df.drop_duplicates() # because some rows seem to be repeated, e.g. article 703, var_name INCOME
# del df['userid']
# df.head()


# In[149]:

# OLD APPROACH
# convert datatypes so that I can add them to get majority
df.var_central = df.var_central.astype(bool).astype(float)
df.var_control = df.var_control.astype(bool).astype(float)
df.var_dependent = df.var_dependent.astype(bool).astype(float)
df.var_independent = df.var_independent.astype(bool).astype(float)
df.var_dontknow = df.var_dontknow.astype(bool).astype(float)
df.head()


# In[60]:

# weights for each coding task
# these weights are from weighting coders' responses only on those items that do not include the codes of User 0
# User 0 breaks the estimates because he has so few responses (nothing to compare him to).
user_id_weights_dev = {1:0.984, 2:0.988, 3:0.696, 4:0.867, 5:0.97, 6:0.933, 7:0.798}
user_id_weights_ind = {1:0.656, 2:0.962, 3:0.869, 4:0.888, 5:0.936, 6:0.529, 7:0.934}
user_id_weights_central = {1:0.993, 2:0.892, 3:0.68, 4:0.593, 5:0.785, 6:0.952, 7:0.613}
user_id_weights_control = {1:0.654, 2:0.962, 3:0.868, 4:0.887, 5:0.936, 6:0.528, 7:0.935}

df['var_dep_weighted'] = df.var_dependent * df.userid.map(user_id_weights_dep)
df['var_indep_weighted'] = df.var_independent * df.userid.map(user_id_weights_indep)
df['var_control_weighted'] = df.var_control * df.userid.map(user_id_weights_control)
df['var_central_weighted'] = df.var_central * df.userid.map(user_id_weights_central)

# cols_to_weight = ['var_control', 'var_central', 'var_dependent', 'var_independent', 'var_dontknow']
# df[cols_to_weight] = df[cols_to_weight] * df.weights 


# In[61]:

# TALLY THE VOTES FOR EACH VARIABLE TYPE
df_variables = df.groupby(('article_id', 'var_name')).sum()
df_variables.head(5)


# ###Create majority vote for whether variable is indep or dep

# In[62]:

# create a custom max function
# def custom_max(s): # s is a series
#     if s['var_dependent'] > s['var_independent'] + s['var_control']:
#         return 'var_dependent'
#     elif s['var_dependent'] < s['var_independent'] + s['var_control']:
#         return 'var_independent'
#     else: 
#         return nan 
    
def custom_max_weighted(s): # s is a series
    if s['var_dep_weighted'] > s['var_indep_weighted'] + s['var_control_weighted']:
        return 'var_dependent'
    elif s['var_dep_weighted'] < s['var_indep_weighted'] + s['var_control_weighted']:
        return 'var_independent'
    else: 
        return nan 

# df_variables['majority_vote_type'] = df_variables.apply(custom_max, axis=1)
df_variables['majority_vote_type'] = df_variables.apply(custom_max_weighted, axis=1)


# ###Create vote for whether variable is central, ``majority_vote_central``

# In[63]:

#If at least one person thinks it's central, then it's central
df_variables['majority_vote_central'] = df_variables.var_central.astype(bool)


# ###Check how many "ties" there are on variable codes

# In[170]:

# there is ~1600 articles but ~22,000 rows in df_variables because each article has many variables.
# So it appears nearly every article has a tie.
# def is_there_a_tie(s):
#     # if there is a legitimate tie
#     if s['var_dependent'] > 0 and (s['var_dependent'] == s['var_independent'] 
#                                    or s['var_dependent'] == s['var_independent']+s['var_control']):
#         return 'tie: dependent == independent'
#     elif s['var_dependent'] > s['var_independent']:
#         return 'dep > indep'
#     elif s['var_dependent'] < s['var_independent']:
#         return 'dep < indep'
#     elif s['var_dependent'] < s['var_independent'] + s['var_control']:
#         return 'dependent < ind + control'
#     elif s['var_dependent'] > s['var_independent'] + s['var_control']:
#         return 'dependent > ind + control'
#     else: 
#         return nan     
#unweighted output
# dep < indep                      9625
# dep > indep                      7392
# tie: dependent == independent    1602
# dependent < ind + control          33
# dtype: int64


def is_there_a_tie_weighted(s):
    # if there is a legitimate tie
    if s['var_dep_weighted'] > 0 and (s['var_dep_weighted'] == s['var_indep_weighted'] 
                                   or s['var_dep_weighted'] == s['var_indep_weighted']+s['var_control_weighted']):
        return 'tie: dependent == independent'
    elif s['var_dep_weighted'] > s['var_indep_weighted']:
        return 'dep > indep'
    elif s['var_dep_weighted'] < s['var_indep_weighted']:
        return 'dep < indep'
    elif s['var_dep_weighted'] < s['var_indep_weighted'] + s['var_control_weighted']:
        return 'dependent < ind + control'
    elif s['var_dep_weighted'] > s['var_indep_weighted'] + s['var_control_weighted']:
        return 'dependent > ind + control'
    else: 
        return nan     
    
df_variables['is_there_a_tie'] = df_variables.apply(is_there_a_tie_weighted, axis=1)
# df_variables['is_there_a_tie'] = df_variables.apply(is_there_a_tie, axis=1)

print df_variables.is_there_a_tie.value_counts()

# How many UNIQUE ARTICLES have at least one tie?
df_var_copy = df_variables.copy()
df_var_copy['article_id'] = df_var_copy.index.get_level_values(0)
df_var_copy['tie'] = df_var_copy.apply(is_there_a_tie_weighted, axis=1)
ids_with_tie = df_var_copy[df_var_copy.tie == 'tie: dependent == independent'].article_id.unique()
print 'Unique articles with at least one tie:', len(ids_with_tie)



# #New approach using posteriors

# In[211]:

df_posterior = pd.read_csv('../Data/posterior_estimates_of_variable_types.csv', index_col=0)
df_posterior.head(20)


# In[212]:

# get the majority type
type_dict = {0:'var_dependent', 1:'var_independent', 2:'var_control'}
df_posterior['posterior_type'] = [type_dict[el] for el in np.argmax(df_posterior[['dep_var_true', 'ind_var_true', 'control_var_true']].values, axis=1)]

# get central
df_posterior['posterior_central'] = df_posterior.central_var_true >= 0.5

# there are 455 cases where posterior_central==True and posterior_type==var_control. df_posterior.loc[(df_posterior.posterior_central==True) & (df_posterior.posterior_type=='var_control')]
# We are going to assume that "central" status trumps "control vs. IV" status.

df_posterior.head()


# In[ ]:




# In[213]:

### COMPARE DISTRIBUTION OF VARIABLES BY METHOD

print 'Old (Weighted Majority Vote) method'
print '-----------------------------------'
print df_variables.majority_vote_type.value_counts()
print
print 'Central?'
print df_variables.majority_vote_central.value_counts()
print
print
print 'New (Posterior) Method'
print '--------------------------------------'
print df_posterior.posterior_type.value_counts()
print
print 'Central?'
print df_posterior.posterior_central.value_counts()


# ##Compare User 0's codes and Posterior codes

# In[215]:

combined_dfs = df[df.userid==0].merge(df_posterior, left_on=('article_id', 'var_name'), right_on=('true_article_id', 'var_name'))
# combined_dfs.head()

# from scipy.stats import pearsonr

# print 'Correlations between User 0 and Posterior Estimates'
# print '----------------------------------------------'
# print 'Dependent correlation:', pearsonr(combined_dfs.var_dependent, combined_dfs.posterior_type == 'var_dependent')[0]
# print 'Independent correlation:', pearsonr(combined_dfs.var_independent, combined_dfs.posterior_type == 'var_independent')[0]
# print 'Control correlation:', pearsonr(combined_dfs.var_control, combined_dfs.posterior_type == 'var_control')[0]
# print 'Central correlation:', pearsonr(combined_dfs.var_central, combined_dfs.posterior_central == True)[0]

# output
'''
Correlations between User 0 and Posterior Estimates
----------------------------------------------
Dependent correlation: 0.644396551724
Independent correlation: 0.426704807965
Control correlation: 0.630871934624
Central correlation: 0.424640648454
'''

# The correlations are high enough and the user0 has coded few enough items that we're going to ingore his ratings.


# In[ ]:




# In[216]:

#How many articles will be *gained* by resolving ties?
#df_var_copy[df_var_copy.article_id.isin(ids_with_tie)].majority_vote_type == 'var_dependent'


# #Get the GSS Years

# In[217]:

c.execute('select true_article_id, gss_years, year_published from gss_corpus')
df_years = pd.DataFrame([el for el in c.fetchall()], columns=['article_id', 'gss_years', 'year_published'])
df_years.index = df_years.article_id
df_years.gss_years = df_years.gss_years.astype(str)

del df_years['article_id']

df_years.sort('year_published', ascending=False).head()


# ###Pre-process

# In[218]:

GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 1980, 1982,  
                 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991,
                 1993, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010,
                 2012]


# In[219]:

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

df_years.gss_years = df_years.gss_years.map(f)


# ###Now parse the years strings

# In[220]:

def clean_years(x):
    
    # skip all the nans
    if x is np.nan: return np.nan
    
    # for articleID, yearsUncleaned in df[df.gss_years.notnull()].itertuples(): # the "notnull()" should avoid all the nan's
    yearsUncleaned = x

    yearsCleaned = []    # for each article, start with an empty list of GSS years used
 
    print 'yearsUncleaned:', yearsUncleaned
   
    yearsUncleaned = yearsUncleaned.lower().strip().replace('"', '') # lower-case, get rid of trailing spaces and get rid of quotes
    
    # CASE 1: beginning of yearsUncleaned is one of those rows where there's a textual explanation, which seems to always begin with "ACT:" 
    #treat it as if we have no info (don't even put it in the dictionary)
    if yearsUncleaned[:3] == 'act' : return np.nan
   
   # CASE 2: the entire string is less than 4 characters
    if len(yearsUncleaned) < 4:
        print yearsUncleaned
        return np.nan

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
                    return np.nan 
                    
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
                    return np.nan 
                else:
                    yearsCleaned.append(int(rangeOfYears))                
        
        return yearsCleaned
    
    except ValueError: # if there is any kind of error regarding the year of the article not being in the available years (GSS_YEARS), skip this article
        print 'This year not in legitimate GSS years', yearsUncleaned
        return np.nan
    
df_years['years_cleaned'] = df_years.gss_years.apply(clean_years)    


# ##Now create articleClasses list

# In[ ]:




# In[229]:

'''
description: 
 - This script constructs a list of articleClass instances, where each articleClass contains an article's metadata
 - the filtering of the articles is done mostly by filterArticleClasses.py,
 - But I do make the following filters/selections here:
   
     NOT DOING THIS --> 1. gss_central_variable field must be == 'Yes'
     1. Skip articles with no GSS years used (or if they can't be imputed)
     2. make sure the stated GSS years the article used actually contain the variables
         the article allegedly used

- the other filter criteria are performed by filterArticleClasses.py    
 
 
inputs:
 - I pull things from the lanl database, but also use VARS_BY_YEAR.pickle

outputs:
 - articleClasses.pickle -- this is a list of articleClass instances

'''

# IMPORTS #############################
# add GSS Project/Code directory to module search path, just in case
import sys
sys.path.append('../Code/')
from GSSUtility import articleClass
import cPickle as cp

# GLOBALS
GSS_YEARS = [1972, 1973, 1974, 1975, 1976, 1977, 1978, 
            1980, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 
            1990, 1991, 1993, 1994, 1996, 1998, 
            2000, 2002, 2004, 2006, 2008, 2010, 2012]

pathToData = '../Data/'  
   
# LOAD DATA ###########################
VARS_BY_YEAR = cp.load(open(pathToData + 'VARS_BY_YEAR.pickle', 'rb')) # key=year, value=set('VAR1', 'VAR2', ...)

maxYearPublished = 0
countOfNoGSSYearsUsed = 0
countImputed = 0

# CONSTRUCT articleCLasses LIST
articleClasses = []
# article_ids = df_variables.index.levels[0]

for article_id in df_posterior.true_article_id.unique(): # for each article for which we have information on its variables...
    
#     # if articleID not in GSS_CENTRAL_VARIABLE or not GSS_CENTRAL_VARIABLE[articleID]:continue
    
#     # sub-dataframe just for this article (original is a multiindex (article, variable name)). 
#     # article_df has rows like (var name, metadata columns)
#     article_df = df_variables.loc[article_id]  
    article_df = df_posterior[df_posterior.true_article_id == article_id]
    
#     ### VARIABLES
#     # get all variable types for the article 
#     IVs =  article_df[article_df.majority_vote_type == 'var_independent'].index
#     DVs =  article_df[article_df.majority_vote_type == 'var_dependent'].index
#     # currently the line below is uesless, because majority_vote_type is never var_control
#     controls =  article_df[article_df.majority_vote_type == 'var_control'].index
#     centralIVs =  article_df[np.array(article_df.majority_vote_type == 'var_independent') \
#                              & np.array(article_df.majority_vote_central == True)].index
    # uncomment later!
    
    # VARIABLES
    IVs = article_df.loc[article_df.posterior_type == 'var_independent', 'var_name'].tolist()
    DVs = article_df.loc[article_df.posterior_type == 'var_dependent', 'var_name'].tolist()
    controls = article_df.loc[article_df.posterior_type == 'var_control', 'var_name'].tolist()
    # Note: "central" status trumps "control" status. So a control that's central becomes a central.
    centralIVs = article_df.loc[(article_df.posterior_central==True) &                                 ((article_df.posterior_type == 'var_independent') |                                 (article_df.posterior_type == 'var_control')), 'var_name'].tolist()   
    
    # make sure there is at least one DV and at least one IV
    if len(DVs) == 0 or len(IVs) == 0: continue
        
    # convert all variable names to upper case
    IVs = map(str.upper, IVs)
    DVs = map(str.upper, DVs)
    controls = map(str.upper, controls)
    centralIVs = map(str.upper, centralIVs)
        
    ### YEARS
    # this function is used to impute GSSYearsUsed for articles for which we have variable information but not 
    # GSS_years_used information
    def impute_GSS_years_used(variables, publication_year):
        candidate_years = [yr for yr in GSS_YEARS if yr <= (publication_year-2)]
        return [yr for yr in candidate_years if set(IVs + DVs + controls + centralIVs).issubset(VARS_BY_YEAR[yr])]

    yearPublished = df_years.loc[article_id, 'year_published']
    if yearPublished < 1972 or yearPublished > 2014: yearPublished=nan

    # what is this for??
    if yearPublished > maxYearPublished:
        maxYearPublished = yearPublished


    oldGSSYears = df_years.loc[article_id, 'years_cleaned']

    # impute years
    if oldGSSYears is nan:
        if yearPublished is nan:
            countOfNoGSSYearsUsed+=1
            continue
        else:
            # impute GSS years
            oldGSSYears = impute_GSS_years_used(set(IVs + DVs + controls + centralIVs), yearPublished)
            countImputed+=1
            if len(oldGSSYears) == 0: 
                countOfNoGSSYearsUsed+=1
                continue

    # check to make SURE that the GSS years the article allegedly used contain all the VARIABLES
    # the article allegedly used
    oldGSSYears = [yr for yr in oldGSSYears if set(IVs + DVs + controls + centralIVs).issubset(VARS_BY_YEAR[yr])]   

    unusedGSSYears = set(GSS_YEARS) - set(oldGSSYears) # whether the variables are in that year or not..
    newGSSYears = [yr for yr in sorted(unusedGSSYears) if set(IVs + DVs + controls + centralIVs).issubset(VARS_BY_YEAR[yr])]  

    currentArticle = articleClass(article_id, IVs, DVs, controls, centralIVs, oldGSSYears, newGSSYears, yearPublished=yearPublished)
    articleClasses.append(currentArticle)


# In[230]:

# save the list    
cp.dump(articleClasses, open(pathToData + 'articleClasses.pickle', 'wb'))


# In[228]:

centralIVs.tolist()


# #Let's examine articleClasses to see how much of it is usable!

# In[224]:

print 'Total instances:', len(articleClasses)
print 'Skipped articles:', countOfNoGSSYearsUsed
print 'Imputed GSS years:', countImputed
print 'Max year published:', maxYearPublished


# ##Why no years above 2005, even when imputing?
# 
# This analysis is in a different notebook but basically the problem is we don't have information on variables or years.

# In[74]:

# we don't have variables information on any of them!!!
# (or year information, either)
articles_above_2005 = list(df_years[df_years.year_published > 2005].index)
print articles_above_2005

for a in articles_above_2005:
    try:
        print df_variables.loc[a]
    except:
        pass


# ###How many articles don't have a DV and at least one IV?

# In[225]:

countNoDvs = 0
countNoIvs = 0
no_dvs = []
no_ivs = []
for a in articleClasses:
    if len(a.DVs) == 0: 
        countNoDvs+=1
        no_dvs.append(a.articleID)
    if len(a.IVs) == 0: 
        countNoIvs+=1
        no_ivs.append(a.articleID)
print 'no IVs', countNoIvs
print 'no DVs', countNoDvs 


# In[ ]:



