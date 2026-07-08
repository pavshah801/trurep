import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os

from datetime import date
import json
import re
from pymongo import MongoClient
from pymongo.server_api import ServerApi

MXSCR=10
UPDATE=False

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
            dtsout=pd.json_normalize(mnglst).drop('_id',axis=1)                                     
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

today = date.today()

if UPDATE:
    dtsname_='model_links_listingsold'
    links_listingsold=crud(dtsname=dtsname_,read=True,jsn=False)
    #links_listingsold=pd.read_json('/kaggle/input/testmodels0-1/model_links_listingsold.json')
dtsname_='model_links_listings'
links_listings=crud(dtsname=dtsname_,read=True,jsn=False)
#links_listings=pd.read_json('/kaggle/input/testmodels0-1/model_links_listings.json')

urls_listnew=[]
for jj in list(pd.DataFrame(links_listings['listing_urls']).index):
    urls_listnew.extend(pd.DataFrame(links_listings['listing_urls']).loc[jj].values[-1])
#pd.DataFrame(urls_listnew).to_csv('urls_listnew.csv')
dtsname_="urls_listnew"
dtsin=pd.DataFrame(urls_listnew,columns=['0'])
crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)

refnum_list=list(links_listings.refnum.unique())
#pd.DataFrame(refnum_list).to_csv('refnum_list.csv')
dtsname_="refnum_list"
dtsin=pd.DataFrame(refnum_list,columns=['0'])
crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)

dtsname_='listings'
db_listingsmod=crud(dtsname=dtsname_,read=True,jsn=False)
listingsmod=db_listingsmod['Basic Info'].apply(pd.Series)
print(listingsmod.isna().sum())
print('success')
urls_listold=list(db_listingsmod['URL'].apply(pd.Series)['url'])

urls_listnew_=[('https://www.chrono24.com'+y.strip()) for y in urls_listnew]

urls_drop=[x for x in urls_listold if x not in urls_listnew_]

dicurls_drop={}
for tt in urls_drop:
  dicurls_drop[tt]=today
json.dump(dicurls_drop,open("data_trulux/urls_dropped.json",'w' ))
dtsname_="urls_dropped"
dtsin=dicurls_drop.copy()
crud(dtsname=dtsname_,read=False,jsn=True,dtsin=dtsin)   

refnum_drop=[]
if UPDATE:
  refnum_drop=[x for x in list(links_listingsold.refnum.unique()) if x not in refnum_list]

refnum_listnewadd=[]
if UPDATE:
    refnum_listnewadd=[y for y in refnum_list if y not in list(links_listingsold.refnum.unique())]

if UPDATE:
  dtsname_='dicrefnum_drop'
  dicrefnum_dropp=crud(dtsname=dtsname_,read=True,jsn=True)
  dicrefnum_dropp[0].pop('_id')
  dicrefnum_drop=dicrefnum_dropp[0]  
#  dicrefnum_drop=json.load(open(f'/kaggle/input/dicrefnum_drop/dicrefnum_drop.json'))
  for kk in refnum_drop:
   if kk in dicrefnum_drop.keys():
    if kk in refnum_listnewadd:
      dicrefnum_drop[kk][today]='used'
    else:
      dicrefnum_drop[kk][today]='unused'
   else:
    dicrefnum_drop[kk]={today:'unused'}
else:
  dicrefnum_drop={}
  for kk in refnum_drop:
    dicrefnum_drop[kk]={today:'unused'}
with open("data_trulux/dicrefnum_drop.json", "w", encoding="utf-8") as file:
    file.write(json.dumps(dicrefnum_drop, indent=4))
dtsname_="dicrefnum_drop"
dtsin=dicrefnum_drop.copy()
crud(dtsname=dtsname_,read=False,jsn=True,dtsin=dtsin)   
    
if UPDATE:
  refnum_drop_=[]
  for key,value in dicrefnum_drop.items():
      for key_,value_ in value.items():
          lastvalue=value_
      if lastvalue=='used':
         refnum_drop_.append(key)

  listlinks_listingsold=[]
  for rr in refnum_drop_:
    listlinks_listingsold.append(links_listingsold[links_listingsold.refnum==rr])
  links_listingsoldadd=pd.concat(listlinks_listingsold,axis=0)
  links_listings1=pd.concat([links_listings,links_listingsoldadd],axis=0)
  links_listings1=links_listings1.reset_index(drop=True)

#index_nodrop=list(pd.read_json('/kaggle/input/listings1/listings')['URL'].apply(pd.Series).reset_index().set_index('url').drop(urls_drop,axis=0)['index'])

#if len(urls_drop)==0:
#    _=0
#else:
#  listingsmod=listingsmod.loc[index_nodrop]

listingsmod['Brand'].unique()

listingsmod['Brand'].nunique()

br=list(listingsmod.groupby('Brand')['Brand'].count().sort_values(ascending=False)[0:50].index)

br

lst_modelsinbrand=[]
for vv in br:
     modelsinbrand=pd.DataFrame(listingsmod[listingsmod['Brand']==vv].groupby('Model')['Model'].count().sort_values(ascending=False)[0:15].index).T
     modelsinbrand['brand']=vv
     lst_modelsinbrand.append(modelsinbrand)

table_of_models=pd.concat(lst_modelsinbrand,axis=0).sort_values(by='brand').fillna('Unknown')
table_of_models=pd.DataFrame(np.array(table_of_models),columns=list(table_of_models.columns.astype('string')))
table_of_models

dtsname_="table_of_models"
dtsin=table_of_models.copy()
crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)
#table_of_models.to_excel("table_of_models.xlsx")

lst_=[]
maxscript=MXSCR
for s in range(0,maxscript):
  lst_.append(pd.DataFrame(br,columns=[f'brands{s}']))
table_of_brandsinloops=pd.concat(lst_,axis=1)

table_of_brandsinloops.drop(br.index('Rolex'),axis=0,inplace=True)

table_of_brandsinloops.reset_index(drop=True,inplace=True)

table_of_brandsinloops

dtsname_="table_of_brandsinloops"
dtsin=table_of_brandsinloops.copy()
crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)
#table_of_brandsinloops.to_excel("table_of_brandsinloops.xlsx")

dtsname_="table_of_brands"
dtsin=pd.DataFrame(br,columns=['brands'])
crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)
#(pd.DataFrame(br,columns=['brands'])).to_excel("table_of_brands.xlsx")
print('success')
#listings=pd.read_json('/kaggle/input/listings1/listings')
#if len(urls_drop)==0:
#    _=0
#else:
#  listings=listings.loc[index_nodrop]
#for BRND in br:
#  a=0
#  listings_exm=[]
#  print(f'brand:{BRND}')
#  for jj in list(listingsmod[listingsmod.Brand==BRND].index):
#   a=a+1
#   if a%100==0:
#        print(f'file: {a}')
#   listings_exm.append(listings.loc[jj,:].to_dict())
#  BRND=re.sub('& ','',BRND)
#  BRND=re.sub('ö','',BRND)
#  BRND=re.sub('ü','',BRND)
#  ins=re.sub('è','',BRND)
#  with open(f"{ins.lower()}_listings", "w", encoding="utf-8") as file:
#      file.write(json.dumps(listings_exm, indent=4))
if UPDATE:
  links_listings1jsn=[]
  for jj in list(links_listings1.index):
     links_listings1jsn.append(links_listings1.loc[jj,:].to_dict())
  dtsname_="model_links_listings"
  dtsin=links_listings1jsn
  crud(dtsname=dtsname_,read=False,jsn=True,dtsin=dtsin)  
#  with open("model_links_listings.json", "w", encoding="utf-8") as file:
#      file.write(json.dumps(links_listings1jsn, indent=4))