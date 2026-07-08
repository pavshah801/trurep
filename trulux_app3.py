# Commented out IPython magic to ensure Python compatibility.
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import sys
import pandas as pd
import requests
import pickle
from requests import get
import shutil
from bs4 import BeautifulSoup
import re
import json
import time
import xml.etree.ElementTree as ET
import logging
from tqdm import tqdm
from lxml import html
from time import sleep
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import MultiLabelBinarizer
from kmodes.kprototypes import KPrototypes
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
SCRNUM=2
MULTI=False
BRND='Longines'
BRND = os.getenv('ENV_BRND',BRND)
# %matplotlib inline
#logging.basicConfig(filename='chrono24_listing_download.log', level=logging.DEBUG, filemode='a')

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

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
opts = FirefoxOptions()
opts.add_argument("--headless")
browser = webdriver.Firefox(options=opts)

mo=BRND

BRND=re.sub('& ','',BRND)
BRND=re.sub('ö','',BRND)
BRND=re.sub('è','',BRND)
BRND=re.sub('ü','',BRND)

url=f'https://shop.getbezel.com/explore?searchQuery={mo}'

session = requests.Session()
# send a get request to the server
response = session.get(url)
# print the response dictionary
cookies=session.cookies.get_dict()
print(session.cookies.get_dict())

response = get(url,cookies=cookies)
if response.status_code != 200:
     warn('Request: {}; Status code: {}'.format(requests, response.status_code))

browser.get(url)
sleep(1)
browser.get(url)

while True:
        previous_scrollY = browser.execute_script( 'return window.scrollY' )
        browser.execute_script( 'window.scrollBy( 0, 230 )' )
        sleep( 0.4 )
        if previous_scrollY == browser.execute_script( 'return window.scrollY' ):
            print( 'job done, reached the bottom!' )
            break
page_modelsbezel_=browser.page_source
page_modelsbezel = BeautifulSoup(page_modelsbezel_, 'lxml')

for item in page_modelsbezel.find_all('a',class_='d-flex flex-column h-100'):
    print(item['href'])

cnt=0
models_urls1_=[]
for item in page_modelsbezel.find_all('a',class_='d-flex flex-column h-100'): 
    print('https://shop.getbezel.com'+item['href'])
    models_urls1_.append('https://shop.getbezel.com'+item['href'])
    cnt=cnt+1
print(cnt)

for item in page_modelsbezel.find_all('div',class_='text-primary riforma-regular fs-12px w-100 ModelCard_subtitle__Ya_z2'):
    print(item.string.split('/')[-1].split(' '))

_models_urls1_2=[]
delin1=[]
cnt=0
for item in page_modelsbezel.find_all('div',class_='text-primary riforma-regular fs-12px w-100 ModelCard_subtitle__Ya_z2'):
     if len(item.string.strip().split('/')[-1].strip().split(' '))>1:
         print(item.string.strip().split('/')[-1].strip().split(' ')[-1].split('-')[0].lower())
         _models_urls1_2.append(item.string.strip().split('/')[-1].strip().split(' ')[-1].split('-')[0].lower())
         cnt=cnt+1
     else:
         delin1.append(cnt)
         cnt=cnt+1
print(cnt)

print(delin1)
try:
   models_urls1_=np.delete(models_urls1_,delin1).tolist()
except:
   print('no deleted')
len(models_urls1_)

browser.close()
models_story=[]
cnt=0
for url_mod in models_urls1_:
   print(cnt)
   opts = FirefoxOptions()
   opts.add_argument("--headless")
   browser = webdriver.Firefox(options=opts)
   browser.get(url_mod)
   print(url_mod)
   try: 
     elem=browser.find_elements('tag name','div')[0].text.split('\n')[20]
     if elem!='Sell or trade yours':
        models_story.append(elem)
        cnt=cnt+1
     else:
        models_story.append('')
        cnt=cnt+1
   except:
     print('unsucess')
     models_story.append('')
     cnt=cnt+1   
   browser.close()

dict_modelsstory={}
for f in range(len(models_urls1_)):
  if models_story[f]!='':
    dict_modelsstory[_models_urls1_2[f]]=models_story[f]

cnt=0
for key,value in dict_modelsstory.items():
    if value=='':
        print(key)
        cnt=cnt+1
print(cnt)

len(dict_modelsstory)

json.dump(dict_modelsstory,open( f"data_trulux/dict1b{BRND.lower()}.json", 'w'))
dtsname_=f"dict1b{BRND.lower()}"
dtsin=dict_modelsstory.copy()
crud(dtsname=dtsname_,read=False,jsn=True,dtsin=dtsin)