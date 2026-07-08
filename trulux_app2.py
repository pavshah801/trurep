# Commented out IPython magic to ensure Python compatibility.
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import gower
import sys
import kmodes
import requests
import shutil
from bs4 import BeautifulSoup
import re
import json
import time
import xml.etree.ElementTree as ET
import logging
from tqdm import tqdm
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import MultiLabelBinarizer
from kmodes.kprototypes import KPrototypes
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
# %matplotlib inline
#logging.basicConfig(filename='chrono24_listing_download.log', level=logging.DEBUG, filemode='a')
SCRNUM=1
MULTI=False
VARIANT='Dial'
BRND='Longines'
BRND = os.getenv('ENV_BRND',BRND)
NODUPLSREF=False
UPDATE=False
MAXURLS=500

def crud(dtsname,read=True,jsn=True,dtsin=None):
    mongo_strin=os.getenv('MONGO_STRING','mongodb://mongoservice:27017/Trulux_catalogue')
    client = MongoClient(mongo_strin)
    dtsname=re.sub(' ','',dtsname)
    dtsname=re.sub('-','',dtsname)
    dtsname=re.sub('[.]','',dtsname)    
    # Connect with the portnumber and host
    mydatabase = client['Trulux_catalogue']
    if read:
        if jsn:
          dtsout=[]  
          if dtsname in mydatabase.list_collection_names():
            mycollection = mydatabase[dtsname]
            for i in mycollection.find():
                dtsout.append(i)
            client.close()                        
          else:
            print('collection is not in database')
            sys.exit('error')
        else:
          mnglst=[]  
          if dtsname in mydatabase.list_collection_names():
            mycollection = mydatabase[dtsname]    
            for i in mycollection.find():
                mnglst.append(i)
            client.close()  
            dtsout=pd.json_normalize(mnglst,max_level=0).drop('_id',axis=1)                                     
          else:  
             print('collection is not in database')
             sys.exit('error')   
        return dtsout        
    else:
        if jsn:
          if dtsname in mydatabase.list_collection_names():
             mycollection = mydatabase[dtsname]         
             mycollection.drop()
             mycollection = mydatabase[dtsname]                           
             if isinstance(dtsin, list):
                mycollection.insert_many(dtsin)
             else:
                mycollection.insert_one(dtsin)
             client.close()   
          else:
             mycollection = mydatabase[dtsname]                                 
             if isinstance(dtsin, list):
                mycollection.insert_many(dtsin)
             else:
                mycollection.insert_one(dtsin)
             client.close()   
        else:
          if dtsname in mydatabase.list_collection_names():
             file_data=[]
             mycollection = mydatabase[dtsname]         
             mycollection.drop()
             mycollection = mydatabase[dtsname]
             for jj in list(dtsin.index):                                                                                 
                  file_data.append(dtsin.loc[jj,:].to_dict())          
             if isinstance(file_data, list):
                mycollection.insert_many(file_data)
 #            else:
 #               mycollection.insert_one(file_data)
             client.close()
          else:
             file_data=[]
             mycollection = mydatabase[dtsname]             
             for jj in list(dtsin.index):                                                                                 
                 file_data.append(dtsin.loc[jj,:].to_dict())                                 
             if isinstance(file_data, list):
                mycollection.insert_many(file_data)
 #            else:
 #               mycollection.insert_one(file_data)
             client.close()

def conv_str_to_int(string_):
    if string_[0]=='0':
       integer_=int(string_[1])
    else:
       integer_=int(string_)
    return integer_

def firstcolnameendwith0(dtbs):
   for item in list(dtbs.columns):
    if item[-1]=='0':
        frst=item
        break
   return frst

table_of_brandsinloops=crud(dtsname='table_of_brandsinloops',read=True,jsn=False)
#table_of_brandsinloops=pd.read_excel('data_trulux/table_of_brandsinloops.xlsx',index_col=0)
if MULTI:
    lst_brn=list(table_of_brandsinloops[f'brands{SCRNUM}'])
    l=0
    if lst_brn[-1]!='Completed':
      for d in lst_brn:
       if d!='Completed':
         BRND=d
         table_of_brandsinloops.loc[l,f'brands{SCRNUM}']='Completed'
         table_of_brandsinloops.to_excel("data_trulux/table_of_brandsinloops.xlsx")
         dtsin=table_of_brandsinloops.copy()
         crud(dtsname='table_of_brandsinloops',read=False,jsn=False,dtsin=dtsin)
         break
       l=l+1
    else:
      lst_upd=list(crud(dtsname='table_of_brands',read=True,jsn=False)['brands'])
 #     lst_upd=list(pd.read_excel('data_trulux/table_of_brands.xlsx',index_col=0)['brands'])
      lst_upd.remove('Rolex')
      table_of_brandsinloops.loc[:,f'brands{SCRNUM}']=lst_upd
      table_of_brandsinloops.to_excel("data_trulux/table_of_brandsinloops.xlsx")
      dtsin=table_of_brandsinloops.copy()
      crud(dtsname='table_of_brandsinloops',read=False,jsn=False,dtsin=dtsin)
      print('all brands were completed,run script once more')
      sys.exit('exit')
else:
    _=0

models=crud(dtsname='model_links_listings',read=True,jsn=True)

##################

#a=0
#listings=[]
#for root, dirs, files in os.walk('/kaggle/input'):
# for name in files:
#  if re.search('info_',name):
#  path=os.path.join(root, name)
#   with open(path,encoding="utf-8") as f:
#    a=a+1
#    if a%100==0:
#      print(f'file: {a}')
#    file_data = json.load(f)
#    listings.append(file_data)

###############

"""# Upload data"""

listings=crud(dtsname='listings',read=True,jsn=True)

models[0:5]

"""# Models"""

dbmodels=pd.json_normalize(models,max_level=0).drop('_id',axis=1)
dbmodels=dbmodels.drop(['listing_urls'],axis=1)

maxvll=0
maxinlist=list(pd.json_normalize(models,max_level=0)['listing_urls'])
for rr in maxinlist:
    if len(rr)>maxvll:
        maxvll=len(rr)

dbmodels=pd.concat([dbmodels,pd.DataFrame(pd.json_normalize(models,max_level=0)['listing_urls'].to_list())],axis=1)

dbmodels=dbmodels.set_index('url')
dbmod=dbmodels.copy()

dbmodels=pd.DataFrame(np.array(dbmodels)[:,-maxvll::],columns=dbmodels.columns[-maxvll::],index=dbmodels.index)

dbmodels

dbmodels[dbmodels.reset_index().groupby('url')[0].count()==2]

dbmodels.reset_index().url.nunique()

dict_models=dbmodels.drop_duplicates().apply(list,axis=1).to_dict()
#dict_models

dbmod0=dbmod.loc[dbmodels.drop_duplicates().index].drop_duplicates()

dbmod0.isna().sum()

(dbmod0.groupby('refnum')['name'].count()>1).sum()

dbmod0.loc[:,'name']=[(re.sub(r'\W+',' ',x)).lower() for x in list(dbmod0['name'])]

dbmod0[dbmod0.brand==BRND].name.nunique()

dbmod0.name.unique()

dbmod0[['name','refnum']][dbmod0[['name','refnum']].duplicated(keep=False).replace({True:1})==1]

dbmod0[dbmod0[['name','refnum']].duplicated()]

dbmod0[dbmod0[['name','refnum']].duplicated()].index

dbmod0.drop(list(dbmod0[dbmod0[['name','refnum']].duplicated()].index),axis=0,inplace=True)

dbmod0[['name','refnum']].duplicated().sum()

dbmod0

dbmod0=dbmod0.reset_index().set_index('refnum')
dbmod0=dbmod0[dbmod0.reset_index().groupby('refnum')['name'].count()==1]
dbmod0=dbmod0.reset_index()
dbmod0=dbmod0.set_index('url')

dbmod0.refnum.nunique()

dbmod0

dict_hiercode_models={}
for bb in list(dbmod0.index):
  row=dbmod0.loc[bb,:]
  dict_hiercode_models[row.refnum]=row['brand']+"/" +row['name']+"/"+row['refnum']

row

dict_hiercode_models

"""# Listings"""

dbomega_listin=pd.json_normalize(listings,max_level=0).drop('_id',axis=1)
dbomega_listinmod=dbomega_listin['Basic Info'].apply(pd.Series)
_IDX_=(dbomega_listinmod[dbomega_listinmod.Brand==BRND]).index
dbomega_listings=dbomega_listin.loc[_IDX_]

BRND=re.sub('& ','',BRND)
BRND=re.sub('ö','',BRND)
BRND=re.sub('è','',BRND)
BRND=re.sub('ü','',BRND)

dbomega_listings.refnum.nunique()

dbomega_listings.columns

dbomegacol=dbomega_listings.columns

dbomega_listings['Basic Info'].apply(pd.Series)

dbomegalist_basic_info=dbomega_listings['Basic Info'].apply(pd.Series)

try:
  dbomegalist_basic_info.Model.nunique()
except:
  _=0

dbomegalist_basic_info.columns

dbomega_listings['Caliber'].apply(pd.Series)

#dbomega_listings['Caliber'].apply(pd.Series)[0].isna().sum()

dbomega_listings['Case'].apply(pd.Series)

#dbomega_listings['Case'].apply(pd.Series)[0].isna().sum()

dbomega_listings['Bracelet/strap'].apply(pd.Series)

#dbomega_listings['Bracelet/strap'].apply(pd.Series)[0].isna().sum()

dbomega_listings['Other'].apply(pd.Series)

#dbomega_listings['Other'].apply(pd.Series)[0].isna().sum()

dbomega_listings['Description'].apply(pd.Series)

#dbomega_listings['Description'].apply(pd.Series)[0].isna().sum()

dbomega_listings['IMG'].apply(pd.Series)

dbomega_listings['Functions'].apply(pd.Series)

#dbomega_listings['Functions'].apply(pd.Series)[0].isna().sum()

dbomega_listings['Seller INFO'].apply(pd.Series)

dbomega_listings_exp=dbomega_listings['URL'].apply(pd.Series)
dbomega_listings_exp=pd.concat([dbomega_listings_exp,dbomega_listings[['refnum']]],axis=1)
for  dt in dbomega_listings.columns[2::]:
  dbomega_listings_exp=pd.concat([dbomega_listings_exp,dbomega_listings[dt].apply(pd.Series).drop([0],axis=1,errors='ignore')],axis=1)

list_control=['Reference number','Model','Year of production','Caliber/movement','Base caliber','Price','Dial','Bracelet material','Bezel material','Dial numerals','Bracelet color','Clasp material','Clasp','Case material']
for q in list_control:
    if q not in list(dbomega_listings_exp.columns):
        sys.exit(f'critical column:{q} not in dataset,brand is not processed')

dbomega_listings_exp.Model.unique()

#dbomega_listings_exp[100:200]

dbomega_listings_exp.isna().sum()

dbomega_listings_exp=dbomega_listings_exp.fillna('Unknown')

lst_ind=list(dbomega_listings_exp.columns)

dic_ind0={}
dic_ind={}
other=list(dbomegacol).index('Other')
description=list(dbomegacol).index('Description')
functions=list(dbomegacol).index('Functions')
lst_ind0=[other,description,functions]
dic_ind0['1']=other
dic_ind0['2']=description
dic_ind0['3']=functions
if dic_ind0['1']==max(lst_ind0):
    dic_ind['1']=3
elif dic_ind0['1']==min(lst_ind0):
    dic_ind['1']=1
else:
    dic_ind['1']=2
if dic_ind0['2']==max(lst_ind0):
    dic_ind['2']=3
elif dic_ind0['2']==min(lst_ind0):
    dic_ind['2']=1
else:
    dic_ind['2']=2
if dic_ind0['3']==max(lst_ind0):
    dic_ind['3']=3
elif dic_ind0['3']==min(lst_ind0):
    dic_ind['3']=1
else:
    dic_ind['3']=2
dic_ind

cct0=0
cct=0
for vv in lst_ind:
  if vv=='data':
   cct=cct+1
   for key, value in dic_ind.items():
     if value == cct:
      lst_ind[cct0]='data'+key
  cct0=cct0+1

pd.Index(lst_ind)

dbomega_listings_exp=pd.DataFrame(np.array(dbomega_listings_exp),columns=pd.Index(lst_ind)).drop(['zoom'],axis=1,errors='ignore')

dbomega_listings_exp

dbomega_listings_exp.groupby('Model')['refnum'].count()

dbomega_listings_exp.groupby('Model')['refnum'].nunique()

(dbomega_listings_exp.groupby('url')['refnum'].nunique()==1).sum()

(dbomega_listings_exp['Price']=='Unknown').sum()

dbomega_listings_exp=dbomega_listings_exp.set_index('url')

dbomega_listings_exp

list(dbomega_listings_exp['Year of production'])

if 'Number of jewels' in list(dbomega_listings_exp.columns):
    _=0
else:
   dbomega_listings_exp['Number of jewels']='Unknown'

extn=list(dbomega_listings_exp.columns)[3:]
extn.remove('Model')
dbomega_listings_exp=dbomega_listings_exp[['refnum', 'Listing code', 'Brand','Model']+extn]

dbomega_listings_exp.loc[:,'Model']=[(re.sub(r'\W+',' ',x)).lower() if x!='Unknown' else x for x in list(dbomega_listings_exp['Model'])]

dbomelist_exp=dbomega_listings_exp.copy()

list(dbomelist_exp['Reference number'].values)

"""# Listings cont..."""

dbomega_listings_exp.reset_index().url.nunique()

dbomega_test=dbomega_listings_exp[dbomega_listings_exp.reset_index().groupby('url')['refnum'].count()==2].sort_index()
dbomega_test[0:2]

dbomega_test[0:1].to_dict()

dbomega_test[1:2].to_dict()

dbomega_listings_exp=dbomega_listings_exp.drop(['refnum'],axis=1)

dbomega_listings_exp=dbomega_listings_exp.drop_duplicates()#drop(['refnum'],axis=1)

dbomega_listings_exp.duplicated().sum()

dbomega_listings_exp.shape

dbomega_test=dbomega_listings_exp[dbomega_listings_exp.reset_index().groupby('url')['Model'].count()>1].sort_index()
dbomega_test[0:2]

dbomega_listings_exp=dbomega_listings_exp.drop(['Seller rating'],axis=1)

dbomega_listings_exp=dbomega_listings_exp.drop_duplicates()#drop(['refnum'],axis=1)

dbomega_listings_exp.shape

dbomega_test=dbomega_listings_exp[dbomega_listings_exp.reset_index().groupby('url')['Model'].count()>1].sort_index()
dbomega_test[0:2]

dbomega_test[0:1].to_dict()

dbomega_test[1:2].to_dict()

dbomega_listings_exp=dbomega_listings_exp.drop(['Price'],axis=1)

dbomega_listings_exp=dbomega_listings_exp.drop_duplicates()#drop(['refnum'],axis=1)

dbomega_listings_exp.shape

dbomega_test=dbomega_listings_exp[dbomega_listings_exp.reset_index().groupby('url')['Model'].count()>1].sort_index()
dbomega_test[0:1].to_dict()

dbomega_test[1:2].to_dict()

dbomega_listings_exp=dbomega_listings_exp.drop(['Availability'],axis=1)

dbomega_listings_exp=dbomega_listings_exp.drop_duplicates()#drop(['refnum'],axis=1)

dbomega_listings_exp.shape

dbomega_test=dbomega_listings_exp[dbomega_listings_exp.reset_index().groupby('url')['Model'].count()>1].sort_index()
dbomega_test[0:1].to_dict()

dbomega_test[1:2].to_dict()

dbomega_listings_exp=dbomega_listings_exp.drop(['data1'],axis=1)

dbomega_listings_exp=dbomega_listings_exp.drop_duplicates()#drop(['refnum'],axis=1)

dbomega_listings_exp.shape

dbomega_test=dbomega_listings_exp[dbomega_listings_exp.reset_index().groupby('url')['Model'].count()>1].sort_index()
dbomega_test[0:1].to_dict()

dbomega_test[1:2].to_dict()

dbomega_listings_exp=dbomega_listings_exp.drop(['Year of production'],axis=1)

dbomega_listings_exp=dbomega_listings_exp.drop(['data2'],axis=1)

dbomega_listings_exp=dbomega_listings_exp.drop_duplicates()#drop(['refnum'],axis=1)

dbomega_listings_exp.shape

dbomega_test=dbomelist_exp[dbomelist_exp.reset_index().groupby('url')['refnum'].count()==2].sort_index()
dbomega_test

dbomelist_exp=dbomelist_exp[dbomelist_exp.reset_index().groupby('url')['refnum'].count()==1]
dbomelist_exp

dbomelist_exp.loc[:,'Year of production']=[re.search(r'\d+',x).group() if re.search(r'\d+',x) else x for x in list(dbomelist_exp['Year of production'])]

dbomelist_exp['Caliber num digits']=''

dbomelist_exp.loc[:,'Caliber num digits']=[re.search(r'\d+',x).group() if re.search(r'\d+',x) else x for x in list(dbomelist_exp['Caliber/movement'])]

for hh in list(dbomelist_exp.index):
  if dbomelist_exp.loc[hh,'Base caliber']=='Unknown':
   if dbomelist_exp.loc[hh,'Caliber num digits']!='Unknown':
    dbomelist_exp.loc[hh,'Base caliber']=dbomelist_exp.loc[hh,'Brand']+' '+dbomelist_exp.loc[hh,'Caliber num digits']

dbomelist_exp.drop(['Caliber num digits'],axis=1,inplace=True)

for hh in list(dbomelist_exp.index):
  if dbomelist_exp.loc[hh,'Base caliber']!='Unknown':
    if re.search(r'\d{2,50}',dbomelist_exp.loc[hh,'Base caliber']):
       if  re.search(r'(\D{2,50})(\d{2,50})',dbomelist_exp.loc[hh,'Base caliber']):
         _=0
         #print('correct base caliber with high probability')
       elif  re.search(r'(\d{2,50})(\D{2,50})',dbomelist_exp.loc[hh,'Base caliber']):
        _=0
       elif dbomelist_exp.loc[hh,'Base caliber'].isdigit():
         dbomelist_exp.loc[hh,'Base caliber']=dbomelist_exp.loc[hh,'Brand']+' '+re.search(r'\d+',dbomelist_exp.loc[hh,'Base caliber']).group()
       else:
         print(dbomelist_exp.loc[hh,'Base caliber'])
         dbomelist_exp.drop(hh,axis=0,inplace=True)
    else:
       print(dbomelist_exp.loc[hh,'Base caliber'])
       dbomelist_exp.drop(hh,axis=0,inplace=True)

for hh in list(dbomelist_exp.index):
  if  re.search('cal',dbomelist_exp.loc[hh,'Base caliber'].lower()):
         print(dbomelist_exp.loc[hh,'Base caliber'])
         dbomelist_exp.loc[hh,'Base caliber']=dbomelist_exp.loc[hh,'Brand']+' '+re.search(r'\d+',dbomelist_exp.loc[hh,'Base caliber']).group()

for hh in list(dbomelist_exp.index):
  if  re.search('rolex',dbomelist_exp.loc[hh,'Base caliber'].lower()):
         print(dbomelist_exp.loc[hh,'Base caliber'])
         dbomelist_exp.drop(hh,axis=0,inplace=True)

#dbomelist_exp[['Base caliber']][50:100]

dbomelist_exp.loc[:,'Seller rating']=[re.search(r'\d+\.?\d+',x).group() if re.search(r'\d+\.?\d+',x) else x for x in list(dbomelist_exp['Seller rating'])]

dbomelist_exp=dbomelist_exp.drop(['Listing code','Seller','SellerID'],axis=1)

dbomelist_exp

dbomelist_exp['Price']

dbomelist_exp['PriceUSD']=[re.search(r'\$\d+(?:,(\d+))?',x).group() if re.search(r'\$\d+(?:,(\d+))?',x) else x for x in list(dbomelist_exp['Price'])]

dbomelist_exp

(pd.Series([1 if re.search(r'\$\d+(?:,(\d+))?',x) else x for x in list(dbomelist_exp['Price'])])==1).sum()

pd.Series([1 if re.search(r'\$\d+(?:,(\d+))?',x) else x for x in list(dbomelist_exp['Price'])]).unique()

dbomelist_exp.loc[:,'PriceUSD']=dbomelist_exp['PriceUSD'].replace('Price on request [Negotiable]', 'Unknown')

dbomelist_exp.loc[:,'PriceUSD']=dbomelist_exp['PriceUSD'].replace('Price on request', 'Unknown')

#dbomelist_exp[100:150]

dbomelist_exp['Seller rating'].unique()

(dbomelist_exp.PriceUSD=='Unknown').sum()

dbomelist_exp['NormalizedPrice']=0

dbomelist_exp['Hierarchy_code']=''

dbomelist_exp=dbomelist_exp.T.drop_duplicates().T

dbomelist_exp=dbomelist_exp.drop(['Dealer product code'],axis=1)

def hierarchy_mapold(variation='default'):
  hilst=[]
  hilst1=list(dbomelist_exp['Brand'])
  hilst2=list(dbomelist_exp['Model'])
  hilst3=list(dbomelist_exp['refnum'])
  hilst4=list(dbomelist_exp['Year of production'])
  if variation!='default':
      hilst5=list(dbomelist_exp[variation])
  for ii in range(0,dbomelist_exp.shape[0]):
    if variation=='default':
      hilst.append(hilst1[ii]+'/'+hilst2[ii]+'/'+hilst3[ii]+'/'+'default')
    else:
      hilst.append(hilst1[ii]+'/'+hilst2[ii]+'/'+hilst3[ii]+'/'+hilst5[ii])
  dbomelist_exp['Hierarchy_code']=hilst

def hierarchy_map(variation='default'):
  hilst=[]
  hilst1=list(dbomelist_exp['Brand'])
  hilst2=list(dbomelist_exp['Model'])
  hilst3=list(dbomelist_exp['refnum'])
  hilst4=list(dbomelist_exp['Year of production'])
  if variation!='default':
      hilst5=list(dbomelist_exp[variation])
  for ii in range(0,dbomelist_exp.shape[0]):
    if variation=='default':
      try:
        hilst.append(dict_hiercode_models[hilst3[ii]]+'/'+'default')
      except Exception as err:
        hilst.append(hilst1[ii]+'/'+hilst2[ii]+'/'+hilst3[ii]+'/'+'default')
    else:
      try:
        hilst.append(dict_hiercode_models[hilst3[ii]]+'/'+hilst5[ii])
      except Exception as err:
        hilst.append(hilst1[ii]+'/'+hilst2[ii]+'/'+hilst3[ii]+'/'+hilst5[ii])

  dbomelist_exp['Hierarchy_code']=hilst

hierarchy_map()

dbomelist_exp.Model.unique()

lstconv=['.'.join(x.split(',')) if x!='Unknown' else x for x in dbomelist_exp.PriceUSD]
dbomelist_exp.PriceUSD=lstconv

lstconv=[x[1:] for x in dbomelist_exp.PriceUSD]
dbomelist_exp.PriceUSD=lstconv

dbomelist_exp.loc[:,'PriceUSD']=dbomelist_exp.PriceUSD.replace('nknown','Unknown')

dbomelist_exp.rename(columns={'PriceUSD':'PriceUSDthou'},inplace=True)

dbeach_modlst=[]
scaler=MinMaxScaler()
cnt=dbomelist_exp.Model.unique()
for mm in cnt:
    print(mm)
    dbeach_mod=dbomelist_exp[dbomelist_exp.Model==mm]
    if len(np.array(dbeach_mod[dbeach_mod['PriceUSDthou']!='Unknown'].PriceUSDthou))!=0:
       meanprice=np.mean(np.array(dbeach_mod[dbeach_mod['PriceUSDthou']!='Unknown'].PriceUSDthou.astype(np.float32)))
       dbeach_mod.loc[:,'NormalizedPrice']=dbeach_mod['PriceUSDthou'].replace('Unknown',str(meanprice)).astype(np.float32)
       dbeach_mod.loc[:,'NormalizedPrice']=scaler.fit_transform(dbeach_mod[['NormalizedPrice']])
    else:
       dbeach_mod.loc[:,'NormalizedPrice']=0.5
    dbeach_modlst.append(dbeach_mod)
dbomelist_exp1=pd.concat(dbeach_modlst,axis=0)

dbomelist_expnorpr=dbomelist_exp1.copy()
dbomelist_expnorpr

##########

hierarchy_map()
dbeach_modlst=[]
scaler=MinMaxScaler()
cnt=dbomelist_exp.Model.unique()
for mm in cnt:
    print(mm)
    dbeach_mod=dbomelist_exp[dbomelist_exp.Model==mm]
    if len(np.array(dbeach_mod[dbeach_mod['PriceUSDthou']!='Unknown'].PriceUSDthou))!=0:
       meanprice=np.mean(np.array(dbeach_mod[dbeach_mod['PriceUSDthou']!='Unknown'].PriceUSDthou.astype(np.float32)))
       dbeach_mod.loc[:,'NormalizedPrice']=dbeach_mod['PriceUSDthou'].replace('Unknown',str(meanprice)).astype(np.float32)
       dbeach_mod.loc[:,'NormalizedPrice']=scaler.fit_transform(dbeach_mod[['NormalizedPrice']])
       dbeach_mod.loc[:,'PriceUSDthou']=dbeach_mod['PriceUSDthou'].replace('Unknown',str(meanprice))
    else:
       dbeach_mod.loc[:,'NormalizedPrice']=0.5
    dbeach_modlst.append(dbeach_mod)
dbomelist_exp1=pd.concat(dbeach_modlst,axis=0)
dbomelist_expnorpr0=dbomelist_exp1.copy()
#dbomelist_expnorpr0.reset_index().to_excel("listings def hierarchy.xlsx")

hierarchy_map(VARIANT)
dbeach_modlst=[]
scaler=MinMaxScaler()
cnt=dbomelist_exp.Model.unique()
for mm in cnt:
    print(mm)
    dbeach_mod=dbomelist_exp[dbomelist_exp.Model==mm]
    if len(np.array(dbeach_mod[dbeach_mod['PriceUSDthou']!='Unknown'].PriceUSDthou))!=0:
       meanprice=np.mean(np.array(dbeach_mod[dbeach_mod['PriceUSDthou']!='Unknown'].PriceUSDthou.astype(np.float32)))
       dbeach_mod.loc[:,'NormalizedPrice']=dbeach_mod['PriceUSDthou'].replace('Unknown',str(meanprice)).astype(np.float32)
       dbeach_mod.loc[:,'NormalizedPrice']=scaler.fit_transform(dbeach_mod[['NormalizedPrice']])
       dbeach_mod.loc[:,'PriceUSDthou']=dbeach_mod['PriceUSDthou'].replace('Unknown',str(meanprice))
    else:
       dbeach_mod.loc[:,'NormalizedPrice']=0.5
    dbeach_modlst.append(dbeach_mod)
dbomelist_exp1=pd.concat(dbeach_modlst,axis=0)
dbomelist_expnorpr1=dbomelist_exp1.copy()
#dbomelist_expnorpr1.reset_index().to_excel("listings with variant hierarchy.xlsx")

#########

dbmod0jsn=[]
dbmod0r=dbmod0.reset_index()
for jj in list(dbmod0r.index):
   dbmod0jsn.append(dbmod0r.loc[jj,:].to_dict())
#with open("mongopre_modelsv1.json", "w", encoding="utf-8") as file:
#    file.write(json.dumps(dbmod0jsn, indent=4))

dbomelist_expnorpr0jsn=[]
dbomelist_expnorpr0r=dbomelist_expnorpr0.reset_index()
for jj in list(dbomelist_expnorpr0r.index):
   dbomelist_expnorpr0jsn.append(dbomelist_expnorpr0r.loc[jj,:].to_dict())
#with open(f"mongopre_listingsdef{BRND.lower()}v1.json", "w", encoding="utf-8") as file:
#    file.write(json.dumps(dbomelist_expnorpr0jsn, indent=4))

dbomelist_expnorpr1jsn=[]
dbomelist_expnorpr1r=dbomelist_expnorpr1.reset_index()
for jj in list(dbomelist_expnorpr1r.index):
   dbomelist_expnorpr1jsn.append(dbomelist_expnorpr1r.loc[jj,:].to_dict())
dtsname_=f"mongopre_listingsonvar{BRND.lower()}{VARIANT.lower()}v1"
dtsin=dbomelist_expnorpr1jsn
crud(dtsname=dtsname_,read=False,jsn=True,dtsin=dtsin)

omega_example=dbomelist_expnorpr1.reset_index().set_index('Hierarchy_code').sort_index()

dbomelist_expnorpr1=dbomelist_expnorpr1.reset_index().set_index('Hierarchy_code').sort_index().drop(VARIANT,axis=1)

dbomelist_feamap=dbomelist_expnorpr1.drop(['refnum', 'Brand', 'Model', 'Reference number', 'data2','PriceUSDthou','Price','url'],axis=1)

dbomelist_feamap

dbomelist_feamap.fillna(0.5,inplace=True)

dbomelist_feamap[dbomelist_feamap['NormalizedPrice'].isna()]

kproto = KPrototypes(n_clusters=1, init='Cao',random_state=42)
clusters=kproto.fit_predict(dbomelist_feamap,categorical=list(range(0,(dbomelist_feamap.shape[1]-1))))

kproto.cluster_centroids_

lis=list(kproto.cluster_centroids_[0,1:])
lis.append(kproto.cluster_centroids_[0,0])
centr=np.array(lis).reshape(1,-1)
centrdb=pd.DataFrame(centr,columns=list(dbomelist_feamap.columns))
dbomelist_feamap=pd.concat([dbomelist_feamap,centrdb],axis=0)
dbomelist_feamap

gowsimm=gower.gower_matrix(dbomelist_feamap)

len(gowsimm[-1,:-1])

dbomelist_expnorpr1['Dissimilarity']=gowsimm[-1,:-1]

dbomelist_expnorpr1.reset_index(inplace=True)
dbomelist_expnorpr1['sub_idx']=dbomelist_expnorpr1.groupby("Hierarchy_code").cumcount()
dbomelist_expnorpr1=dbomelist_expnorpr1.set_index(['Hierarchy_code','sub_idx'])

##########

idxlev0=dbomelist_expnorpr1.index.get_level_values(0).to_series().unique()

dbomelist_expnorpr1.columns

lagg=[]
for ee in idxlev0:
    listagg=dbomelist_expnorpr1.loc[(ee,),:]
    listaggone=pd.DataFrame(listagg.loc[listagg['Dissimilarity'].idxmin()]).T
    listaggone['Hierarchy_code']=ee
    lagg.append(listaggone.set_index('Hierarchy_code'))

columnames=list(dbomelist_expnorpr1.columns[5:-3])

columnames.remove('Price')

columnames.remove('data2')

columnames

dagg={}
for xx in columnames:
   lagg1=[]
   for  ee in idxlev0:
    listagg1=dbomelist_expnorpr1.loc[(ee,),:]
    lagg1.append(pd.DataFrame(listagg1.groupby(xx)[xx].count()).to_dict())
   dagg[xx] =lagg1

dagg['Year of production']

daggmax={}
for xx in columnames:
   lagg2=[]
   for  ee in idxlev0:
    listagg2=dbomelist_expnorpr1.loc[(ee,),:]
    if listagg2.groupby(xx)[xx].count().drop(['Unknown'],errors='ignore').size!=0:
     lagg2.append((listagg2.groupby(xx)[xx].count().drop(['Unknown'],errors='ignore')).idxmax())
    else:
     lagg2.append('Unknown')
   daggmax[xx] =lagg2

(pd.Series(daggmax['data1'])=='Unknown').sum()

(pd.Series(daggmax['Movement'])=='Unknown').sum()

ome_catalog=pd.concat(lagg,axis=0)
#ome_catalog

for key0,value0 in dagg.items():
    ome_catalog[key0+'0']=value0

for key1,value1 in daggmax.items():
    ome_catalog[key1+'1']=value1

ome_catalog

(ome_catalog.data1=='Unknown').sum()

ome_catalog.refnum.nunique()

ome_catalog[ome_catalog['PriceUSDthou']=='Unknown']

ome_catalog.drop(['Price'],axis=1,inplace=True)

ome_catalog

idxcat=list(ome_catalog.index)
for xx in columnames:
    for yy in idxcat:
      if ome_catalog.loc[yy,xx]=='Unknown':
        xx1=xx+'1'
        cc=ome_catalog.loc[yy,xx1]
        ome_catalog.loc[[yy],[xx]]=cc

ome_catalog[ome_catalog['data3']=='Unknown']

idxcat=list(ome_catalog.index)
for xx in columnames:
  try:
    cc=(ome_catalog.groupby(xx)[xx].count().drop(['Unknown'],errors='ignore')).idxmax()
    for yy in idxcat:
      if ome_catalog.loc[yy,xx]=='Unknown':
        ome_catalog.loc[[yy],[xx]]=cc
  except:
    _=0
    print(f'in column {xx}-all Unknowns')

for xx in columnames:
   ome_catalog.drop([xx+'1'],axis=1,inplace=True)

ome_catalog

ome_catalog.refnum.nunique()

idxcat=list(ome_catalog.index)
for yy in idxcat:
    if (ome_catalog.loc[yy,'Model'])=='Unknown':
          ome_catalog.drop([yy],axis=0,inplace=True)

ome_catalog.shape

ome_catalog.refnum.nunique()

ome_catalog.refnum.nunique()

idxcat=list(ome_catalog.index)
for yy in idxcat:
    if (ome_catalog.loc[yy,'data2'])=='Unknown':
        ome_catalog.loc[yy,'data2']='No information in description'

ome_catalog

ome_catalog[ome_catalog['data2']=='Unknown']

ome_catalog['data2']

list(ome_catalog['data1'])

ome_catalog.drop(['NormalizedPrice','Dissimilarity'],axis=1,inplace=True)

ome_catalog.rename(columns={'data2':'Description'},inplace=True)

corr_lst=[x.split(', ')  for x in list(ome_catalog['data1'])]

ome_catalog['data1']=corr_lst

ome_catalog.loc[:,'data1']=[set(x)  for x in list(ome_catalog['data1'])]

setunion=set([])
for rr in list(ome_catalog['data1']):
    setunion=setunion.union(rr)

maxlen=0
maxset=set([])
for rr in list(ome_catalog['data1']):
    if len(rr)>maxlen:
        maxlen=len(rr)
        maxset=rr
print(maxlen)
print(maxset)

len(setunion)

ome_catalog[['data1']]

mlb = MultiLabelBinarizer()
data1_ext=mlb.fit_transform(list(ome_catalog['data1']))
data1_ext_=pd.DataFrame(data1_ext,columns=mlb.classes_,index=ome_catalog.index)
data1_ext_.apply('sum',axis=1)[0:50]

data1_ext_.replace({1:'Yes',0:'No'},inplace=True)

data1_ext_

list(ome_catalog.columns)

list(ome_catalog.columns)[:list(ome_catalog.columns).index('Movement0')]

ome_catalog_left=ome_catalog.drop(list(ome_catalog.columns)[list(ome_catalog.columns).index(firstcolnameendwith0(ome_catalog)):],axis=1)

ome_catalog_right=ome_catalog.drop(list(ome_catalog.columns)[:list(ome_catalog.columns).index(firstcolnameendwith0(ome_catalog))],axis=1)

ome_catalog=pd.concat([ome_catalog_left,data1_ext_,ome_catalog_right],axis=1)

ome_catalog.drop(['data1'],axis=1,inplace=True)

ome_catalog.drop([''],axis=1,errors='ignore',inplace=True)

ome_catalog.rename(columns={'data3':'Complications'},inplace=True)

for tt in list(ome_catalog.index):
   if tt.split('/')[-1]=='Unknown':
      ome_catalog.drop(tt,axis=0,inplace=True)

ome_catalog

ome_catalog.to_excel(f"data_trulux/withvar_{BRND.lower()}{VARIANT.lower()}_cataloguev1.xlsx")

ome_catalog=ome_catalog.reset_index()
dtsname_=f"withvar_{BRND.lower()}{VARIANT.lower()}_cataloguev1"
dtsin=ome_catalog.copy()
crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)

#######

if not UPDATE:

  r_exm=[]
  for a in ['Dial','Bracelet material',
   'Bezel material',
   'Dial numerals',
   'Bracelet color',
   'Clasp material',
   'Clasp','Case material']:
      r_exm.append(omega_example[a].unique())
  r_db_exm=[]
  for j in range(0,len(r_exm)):
   db_exm=pd.DataFrame(r_exm[j]).reset_index()
   db_exm=db_exm[db_exm[0]!='Unknown']
   db_exm['indexcol']=db_exm['index']+1
   indexcoln=[('0'+str(x)) if x<10 else str(x) for x in list(db_exm['indexcol'])]
   db_exm['indexcol']=indexcoln
   db_exm[0]=['Dia_','Brm_',
   'Bem_',
   'Din_',
   'Brc_',
   'Clm_',
   'Cla_','Cam_'][j]+db_exm[0]
   r_db_exm.append(db_exm)
  map_subrefnew=pd.concat(r_db_exm,axis=0).reset_index().drop(['index','level_0'],axis=1)
  crossmap_dic={}
  key_=['Dia_','Brm_',
   'Bem_',
   'Din_',
   'Brc_',
   'Clm_',
   'Cla_','Cam_']
  value_=['Dial','Bracelet material',
   'Bezel material',
   'Dial numerals',
   'Bracelet color',
   'Clasp material',
   'Clasp','Case material']
  for b in range(0,8):
      crossmap_dic[key_[b]]=value_[b]
  map_subrefnew['name']=''
  for t in list(map_subrefnew.index):
      map_subrefnew.loc[t,'name']=crossmap_dic[map_subrefnew.loc[t,0][0:4]]+' '+map_subrefnew.loc[t,0][4::]
  map_subrefnew=map_subrefnew[['name',0,'indexcol']]
  map_subrefnew.rename(columns={0:"0"},inplace=True)
  map_subrefnew.to_excel(f"data_trulux/map_subrefnew{BRND.lower()}v1.xlsx")   
  dtsname_=f"map_subrefnew{BRND.lower()}v1"
  dtsin=map_subrefnew.copy()
  crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)

if UPDATE:
  dtsname_=f'map_subrefnew{BRND.lower()}v1'
  map_subrefnew=crud(dtsname=dtsname_,read=True,jsn=False)
  map_subrefnew['indexcol']=map_subrefnew['indexcol'].astype('string')
  #map_subrefnew=pd.read_excel(f'/kaggle/input/map-subref/map_subrefnew{BRND.lower()}v1.xlsx',dtype={'indexcol': str},index_col=0)
  map_subrefnewupd=map_subrefnew.copy()
  zz=0
  map_var=[]
  while True:
    map_subrefnewupd.reset_index(drop=True,inplace=True)
    try:
      if (map_subrefnewupd.loc[zz+1,0]).split('_')[0]!=(map_subrefnewupd.loc[zz,0]).split('_')[0]:
         map_var.append(map_subrefnewupd[0:(zz+1)])
         map_subrefnewupd.drop(list(range(0,(zz+1))),axis=0,inplace=True)
         zz=0
         continue
    except:
         map_var.append(map_subrefnewupd[0:(zz+1)])
         map_subrefnewupd.drop(list(range(0,(zz+1))),axis=0,inplace=True)
         print('last variant table')
         break
    zz=zz+1
  cllistall=['Dial','Bracelet material',
   'Bezel material',
   'Dial numerals',
   'Bracelet color',
   'Clasp material',
   'Clasp','Case material']
  cllistc=['Dia_','Brm_',
   'Bem_',
   'Din_',
   'Brc_',
   'Clm_',
   'Cla_','Cam_']
  r=0
  map_varupdlst=[]
  for u in cllistall:
    map_varupd=map_var[r]
    old_featureuniq=list(map_varupd[0].unique())
    old_featureuniq_=['_'.join(s.split('_')[1:]) for s in old_featureuniq]
    new_featureuniq=list(omega_example[u].unique())
    new_featureuniq_=[x for x in new_featureuniq if x!='Unknown']
    add_featureuniq=[y for y in new_featureuniq_ if y not in old_featureuniq_]
    indexcolmax=conv_str_to_int(map_varupd['indexcol'].values[-1])
    cnt_=1
    for b in add_featureuniq:
        name_=u+' '+b
        cod_=cllistc[r]+b
        if (indexcolmax+cnt_)<10:
            indexcol_='0'+str(indexcolmax+cnt_)
        else:
            indexcol_=str(indexcolmax+cnt_)
        map_varupd=pd.concat([map_varupd,pd.DataFrame(np.array([[name_,cod_,indexcol_]]),columns=map_varupd.columns)],axis=0)
        cnt_=cnt_+1
    map_varupdlst.append(map_varupd)
    r=r+1
  map_subrefnew=pd.concat(map_varupdlst,axis=0)
  map_subrefnew.reset_index(drop=True,inplace=True)
  map_subrefnew.to_excel(f"data_trulux/map_subrefnew{BRND.lower()}v1.xlsx")
  dtsname_=f"map_subrefnew{BRND.lower()}v1"
  dtsin=map_subrefnew.copy()
  crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)

dtsname_=f'withvar_{BRND.lower()}{VARIANT.lower()}_cataloguev1'
withvar_example=crud(dtsname=dtsname_,read=True,jsn=False)
withvar_example=withvar_example.set_index('Hierarchy_code')
#withvar_example=pd.read_excel(f'/kaggle/input/withvar-example/withvar_{BRND.lower()}{VARIANT.lower()}_cataloguev1.xlsx').set_index('Hierarchy_code')

map_subrefnew_dic=map_subrefnew.drop('name',axis=1).set_index('0').to_dict()['indexcol']

map_subrefnew_dic

cllist=['Dial','Bracelet material',
 'Bezel material',
 'Dial numerals',
 'Bracelet color',
 'Clasp material',
 'Clasp','Case material']

clind=cllist.index(VARIANT)

cllist.remove(VARIANT)

cllist

withvar_example_sub=withvar_example[cllist]

clpref=['Dia','Brm', 'Bem','Din','Brc','Clm','Cla','Cam']
clpref.pop(clind)
withvar_example_sub_=pd.get_dummies(withvar_example_sub, prefix=clpref)

sub_refrea=[]
cllistall=['Dial','Bracelet material',
 'Bezel material',
 'Dial numerals',
 'Bracelet color',
 'Clasp material',
 'Clasp','Case material']
cllistc=['Dia_','Brm_',
 'Bem_',
 'Din_',
 'Brc_',
 'Clm_',
 'Cla_','Cam_']
for ww in list(withvar_example_sub_.index):
    sub_refv=[]
    sub_refva=''
    for vv in list(withvar_example_sub_.columns):
        if withvar_example_sub_.loc[ww,vv]==True:
            sub_refv.append(map_subrefnew_dic[vv])

    sub_refv.insert(cllistall.index(VARIANT),map_subrefnew_dic[cllistc[cllistall.index(VARIANT)]+ww.split('/')[-1]])
    sub_refva=''.join(sub_refv)
    sub_refrea.append(sub_refva)

withvar_example['sub_ref']=sub_refrea

extn=list(withvar_example.columns)[2:-1]

withvar_example=withvar_example[['refnum','sub_ref','url']+extn]

withvar_example

withvar_example.reset_index().set_index(['refnum','sub_ref']).sort_index().to_excel(f'data_trulux/subref_{BRND.lower()}{VARIANT.lower()}_cataloguev1.xlsx')

withvar_example=withvar_example.reset_index()
dtsname_=f"subref_{BRND.lower()}{VARIANT.lower()}_cataloguev1"
dtsin=withvar_example.copy()
crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)