# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Descriptives for GSS Reproducibility Project
# 
# Notes
# --
# 
# - Command used to dump tables from lanl database on Rhodes to be put on OSDC:
#         mysqldump -p -P3307 -u misha --socket=/mnt/ide1/mysql/var/mysql.sock1  lanl gss_question > gss_question.sql
#         
# # Tables
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

# <codecell>


# <codecell>


# <codecell>

import pandas as pd
import cPickle as cp
import sys
sys.path.append('../')
import GSSUtility
import seaborn
import MySQLdb

# <codecell>

# db = MySQLdb.connect(host='54.187.104.183', user='mteplitskiy', passwd="mteplitskiy", db="lanl")
# c = db.cursor()

# <codecell>

c.execute('select gss_years from gss_corpus')
df = pd.Series([el[0] for el in c.fetchall()])

# <markdowncell>

# # Number of variables over time

# <codecell>

path_to_data = 'c:/users/misha/dropbox/GSS Project/data/'
articleClasses = cp.load(open(path_to_data + 'articleClasses.pickle'))
df = pd.DataFrame(columns=['aid', 'yearpublished', 'dvs', 'ivs', 'controls', 'total'])
for a in articleClasses:
    df.loc[a.articleID, :] = np.array([a.articleID, a.yearPublished, a.DVs, a.IVs, a.controls, 0], dtype=object)

df = df[df.yearpublished.notnull()]
df.yearpublished = df.yearpublished.astype(int)
df.aid = df.aid.astype(int)
df.index = df.aid
    
df.dvs = [len(v) for k, v in df.dvs.iteritems()]
df.ivs = [len(v) for k, v in df.ivs.iteritems()]
df.controls = [len(v) for k, v in df.controls.iteritems()]
df.total = df.dvs + df.ivs + df.controls

grouped = df.groupby('yearpublished')

# <markdowncell>

# # Number of articles per year in our data

# <codecell>


# <codecell>

df.controls

# <codecell>

grouped['aid'].count().plot(style='s-')
# legend(fontsize=15)
xlim((1973, 2005))
title('Articles per Year', fontsize=18)
xlabel('Year published', fontsize=15)
ylabel('Number of articles', fontsize=15)
savefig('../../images/9-4-2014--articles-per-year.jpg')

# <codecell>


# grouped.mean()[['dvs', 'ivs', 'controls', 'total']].plot()
means = grouped.mean()

# figsize(())
pd.rolling_mean(means.dvs, window=3).plot(label="Dependent var's", style='s--') 
pd.rolling_mean(means.ivs, window=3).plot( label="Independent var's", style='s--')
# plot(means.index, means['total'], '--', linewidth=1, label="All var's")
legend(fontsize=15)
xlim((1974, 2005))
title('Variables per Article over Time', fontsize=18)
xlabel('Year published', fontsize=15)
ylabel('Variables per article', fontsize=15)
# savefig('../../images/variables_per_article_over_time.jpg')

