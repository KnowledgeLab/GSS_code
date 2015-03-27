article = [a for a in articleClasses if a.articleID == 1994][0]

if len(article.centralIVs) < 1: 
    print 'No "central" IVs. Skipping'
    raise Exception
    
variables = article.IVs + article.DVs 
yearsToTry = random.sample(GSS_YEARS, 10)
#design = df.loc[1978:1988, variables].copy(deep=True)  # Need to make a deep copy so that original df isn't changed
design = pd.concat([df1978, df1988]).copy(deep=True)  # Need to make a deep copy so that original df isn't changed


for col in design.columns:
    if len(design[col].unique()) == 1:
        print col # if any IVs or controls constant, drop 'em
        design.drop(col, axis=1)

# remove missing values
for col in design.columns:
    mv = MISSING_VALUES_DICT[col]
    if 'values' in mv:
        design[col].replace(mv['values'], [np.nan]*len(mv['values']), inplace=True) # it's important to have inPlace=True
    # !!! need to insert the other case heer, where the missing values are in a RANGE with 'higher' and 'lower' bounds
    print design.shape
design = design.dropna(axis=0) # drop all rows with any missing values (np.nan)        
            
# skip if there's not enough data after deleting rows
if design.shape[0] < design.shape[1]: # if number of rows is less than number of columns
    print 'Not enough IV/control data. Skipping...'
    raise Exception

'''      
# recode -- THE RECODING IS NOT WORKING FOR SOME REAOSN!!!!
design['XNORCSIZ'].replace([2,3,4,5,6], [1,1,1,1,1], inplace=True) 
design['XNORCSIZ'].replace([7,8,9,10], [0,0,0,0], inplace=True) 
#design['CHURCH'].replace([2], [0], inplace=True)
design['SEX'].replace([2], [0], inplace=True)
design['RACE'][design['RACE'] != 1] = 0
design['MARITAL'][design['MARITAL'] != 1] = 0
'''

#* NEED VARIABLE FOR AGE OF RESIDENCE AT 16!!!

# create index
#wellbeing = design['HAPPY']+design['SATCITY']+design['SATHOBBY']+design['SATFAM']+design['SATFIN']+design['SATFRND']+design['SATHEALT']            
#design['WELLBEING'] = pd.Series(wellbeing, index=design.index)

'''
# create formula
formula = 'WELLBEING ~ C(SEX) + C(RACE) + C(MARITAL) + C(XNORCSIZ)  \
           + EDUC + FINRELA + ATTEND'

# estimate and print results
results = smf.ols(formula, data=design).fit()
print results.summary()
'''