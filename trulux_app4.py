# Commented out IPython magic to ensure Python compatibility.
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import gower
import sys
import kmodes
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
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
SCRNUM=3
MULTI=False
BRND='Longines'
BRND = os.getenv('ENV_BRND',BRND)
MAXURLS=500
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
#pip show selenium

#!wget https://github.com/mozilla/geckodriver/releases/download/v0.19.1/geckodriver-v0.19.1-linux64.tar.gz
#!tar xvfz geckodriver-v0.19.1-linux64.tar.gz
#!mv geckodriver ~/.local/bin

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
opts = FirefoxOptions()
opts.add_argument("--headless")
browser = webdriver.Firefox(options=opts)

url="https://shop.hodinkee.com/pages/brands"

session = requests.Session()
# send a get request to the server
response = session.get(url)
# print the response dictionary
cookies=session.cookies.get_dict()
print(session.cookies.get_dict())

response = get(url,cookies=cookies)
if response.status_code != 200:
     warn('Request: {}; Status code: {}'.format(requests, response.status_code))

#######Omega and others

mo=BRND
BRND=re.sub('& ','',BRND)
BRND=re.sub('ö','',BRND)
BRND=re.sub('è','',BRND)
BRND=re.sub('ü','',BRND)
num_ofmodels1=0
while num_ofmodels1<=24:
  ins=re.sub(' ','',mo)
  browser.close()
  opts = FirefoxOptions()
  opts.add_argument("--headless")
  browser = webdriver.Firefox(options=opts)
  browser.get(f'https://www.hodinkee.com/search?q={ins}')
  sleep(0.5)
  browser.get(f'https://www.hodinkee.com/search?q={ins}')
  while True:
          previous_scrollY = browser.execute_script( 'return window.scrollY' )
          browser.execute_script( 'window.scrollBy( 0, 230 )' )
          sleep( 0.4 )
          if previous_scrollY == browser.execute_script( 'return window.scrollY' ):
              print( 'job done, reached the bottom!' )
              break
  page_modelshodinkee_=browser.page_source
  page_modelshodinkee = BeautifulSoup(page_modelshodinkee_, 'lxml')
  pg1=page_modelshodinkee
  pg2=pg1.find('div',class_='product-search-container')
  pg3=pg2.find('div',class_='block-shop')
  cnt=0
  models_urls=[]
  for item in pg3.find_all('div',class_='product-card'):
   #   models_urls.append(item)
          cnt=cnt+1
  print(f'number of models:{cnt}')
  num_ofmodels1=cnt

ins=re.sub(' ','',mo)
browser.close()
opts = FirefoxOptions()
opts.add_argument("--headless")
browser = webdriver.Firefox(options=opts)
models_urls1_=[]
cnt=0
browser.get(f'https://shop.hodinkee.com/search?q={ins}')
page_=browser.page_source
page = BeautifulSoup(page_, 'lxml')
for link in browser.find_elements('tag name','a'):
 if link.get_attribute('href')!=None:
  if link.get_attribute('href').split('/')[-2]=='products':
    if cnt>11:
      models_urls1_.append(link.get_attribute('href'))
    cnt=cnt+1
if num_ofmodels1>24:
 for h in range(2,((num_ofmodels1//24)+2)):
  browser.close()
  opts = FirefoxOptions()
  opts.add_argument("--headless")
  browser = webdriver.Firefox(options=opts)
  browser.get(f'https://shop.hodinkee.com/search?q={ins}&page={h}')
  page_=browser.page_source
  page = BeautifulSoup(page_, 'lxml')
  cnt=0
  for link in browser.find_elements('tag name','a'):
   if link.get_attribute('href')!=None:
    if link.get_attribute('href').split('/')[-2]=='products':
        if cnt>11:
          models_urls1_.append(link.get_attribute('href'))
        cnt=cnt+1

len(models_urls1_)

cnt=0
_models_urls1_=[]
delin4=[]
#browser.close()
#opts = FirefoxOptions()
#opts.add_argument("--headless")
#browser = webdriver.Firefox(options=opts)
for s in models_urls1_:
     browser.close()
     opts = FirefoxOptions()
     opts.add_argument("--headless")
     browser = webdriver.Firefox(options=opts)
     browser.get(s)
     page_refn_=browser.page_source
     page_refn = BeautifulSoup(page_refn_, 'lxml')
     idx=''
     counter=0
     print(cnt)
     try:
       for item in page_refn.find_all('div',class_='functional-metadata-title mb-2 text-gray-95'):
         if item.string=='Reference':
           idx=counter
         counter=counter+1
       if idx!='':
          _models_urls1_.append(page_refn.find_all('div',class_='functional-metadata text-gray-95')[idx].string)
          print('success with reference: '+s)
       else:
         if re.search(r'\d+',page_refn.select('div.key-info h1')[0].text.split(' ')[-1]):
           _models_urls1_.append(page_refn.select('div.key-info h1')[0].text.split(' ')[-1])
           print('success with title: '+s)
         else:
            delin4.append(cnt)
            print('unsuccess: '+s)
     except:
            delin4.append(cnt)
            print('unsuccess: '+s)
     cnt=cnt+1

pd.Series(_models_urls1_).nunique()

len(delin4)
try:
  models_urls1_=np.delete(models_urls1_,delin4).tolist()
except:
  print('no deleted')  

_models_urls1_2=[re.sub(r'\W+', "", x.lower()) for x in _models_urls1_]

cnt=0
models_story=[]
for r1 in range(0,((len(models_urls1_)//15)+1)):
  browser.close()
  sleep(0.1)
  opts = FirefoxOptions()
  opts.add_argument("--headless")
  browser = webdriver.Firefox(options=opts)
  r2=min((r1+1)*15,len(models_urls1_))
  for cnt in  range(r1*15,r2):
       print(cnt)
       loopurl=models_urls1_[cnt]
       try:
         browser.get(loopurl)
         browser.find_element(By.CSS_SELECTOR, "span.inline-flex.items-center.gap-2.text-gray-95").click()
         page_refn_=browser.page_source
         page_refn = BeautifulSoup(page_refn_, 'lxml')
         model_story=[]
         for p in page_refn.select('div.flex.flex-col.items-start p'):
             model_story.append((p.string))
         print('success:'+loopurl)
       except:
         model_story=[]
         print('unsuccess:'+loopurl)
       models_story.append(model_story)

dict_modelsstory={}
for f in range(len(models_urls1_)):
    dict_modelsstory[_models_urls1_2[f]]=models_story[f]
json.dump(dict_modelsstory,open(f"data_trulux/dict1{BRND.lower()}.json",'w'))    
dtsname_=f"dict1{BRND.lower()}"
dtsin=dict_modelsstory.copy()
crud(dtsname=dtsname_,read=False,jsn=True,dtsin=dtsin)    
ins=re.sub(' ','',mo)
table_of_models=crud(dtsname='table_of_models',read=True,jsn=False).set_index('brand')
#table_of_models=pd.read_excel('data_trulux/table_of_models.xlsx',index_col=0)
list_of_models_=list(table_of_models.loc[mo,:])
#print(list_of_models_)
list_of_models=[re.sub(' ','',x.lower()) for x in list_of_models_ if x!='Unknown']
#list_of_models=['constellation','deville','seamaster','speedmaster','geneve','vintage','aquaterra']
#mo=BRND
cntr=2
cntr_=0
for k in list_of_models:
  browser.close()
  opts = FirefoxOptions()
  opts.add_argument("--headless")
  browser = webdriver.Firefox(options=opts)
  browser.get(f'https://www.hodinkee.com/search?q={ins} {k}')
  sleep(0.5)
  browser.get(f'https://www.hodinkee.com/search?q={ins} {k}')
  while True:
          previous_scrollY = browser.execute_script( 'return window.scrollY' )
          browser.execute_script( 'window.scrollBy( 0, 230 )' )
          sleep( 0.4 )
          if previous_scrollY == browser.execute_script( 'return window.scrollY' ):
              print( 'job done, reached the bottom!' )
              break
  page_modelshodinkee_=browser.page_source
  page_modelshodinkee = BeautifulSoup(page_modelshodinkee_, 'lxml')
  pg1=page_modelshodinkee
  pg2=pg1.find('div',class_='product-search-container')
  pg3=pg2.find('div',class_='block-shop')
  cnt=0
  models_urls=[]
  for item in pg3.find_all('div',class_='product-card'):
 #   models_urls.append(item)
          cnt=cnt+1
  print(f'number of models:{cnt}')
  num_ofmodels=cnt
  if num_ofmodels>=(num_ofmodels1-3):
    cntr_=cntr_+1
    print('continue')
    continue
  models_urls1_=[]
  cnt=0
  browser.close()
  opts = FirefoxOptions()
  opts.add_argument("--headless")
  browser = webdriver.Firefox(options=opts)
  browser.get(f'https://shop.hodinkee.com/search?q={ins}+{k}')
  sleep(0.5)
  browser.get(f'https://shop.hodinkee.com/search?q={ins}+{k}')
  page_=browser.page_source
  page = BeautifulSoup(page_, 'lxml')
  for link in browser.find_elements('tag name','a'):
   if link.get_attribute('href')!=None:
    if link.get_attribute('href').split('/')[-2]=='products':
      if cnt>11:
        models_urls1_.append(link.get_attribute('href'))
      cnt=cnt+1
  if num_ofmodels>24:
   for h in range(2,((num_ofmodels//24)+2)):
    browser.close()
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    browser = webdriver.Firefox(options=opts)
    browser.get(f'https://shop.hodinkee.com/search?q={ins}+{k}&page={h}')
    sleep(0.5)
    browser.get(f'https://shop.hodinkee.com/search?q={ins}+{k}&page={h}')
    page_=browser.page_source
    page = BeautifulSoup(page_, 'lxml')
    cnt=0
    for link in browser.find_elements('tag name','a'):
     if link.get_attribute('href')!=None:
      if link.get_attribute('href').split('/')[-2]=='products':
          if cnt>11:
            models_urls1_.append(link.get_attribute('href'))
          cnt=cnt+1
  cnt=0
  _models_urls1_=[]
  delin4=[]
  #browser.close()
  #opts = FirefoxOptions()
  #opts.add_argument("--headless")
  #browser = webdriver.Firefox(options=opts)
  for s in models_urls1_:
       browser.close()
       opts = FirefoxOptions()
       opts.add_argument("--headless")
       browser = webdriver.Firefox(options=opts)
       browser.get(s)
       page_refn_=browser.page_source
       page_refn = BeautifulSoup(page_refn_, 'lxml')
       idx=''
       counter=0
       print(cnt)
       try:
         for item in page_refn.find_all('div',class_='functional-metadata-title mb-2 text-gray-95'):
           if item.string=='Reference':
             idx=counter
           counter=counter+1
         if idx!='':
            _models_urls1_.append(page_refn.find_all('div',class_='functional-metadata text-gray-95')[idx].string)
 #         print('success with reference: '+s)
         else:
           if re.search(r'\d+',page_refn.select('div.key-info h1')[0].text.split(' ')[-1]):
             _models_urls1_.append(page_refn.select('div.key-info h1')[0].text.split(' ')[-1])
 #          print('success with title: '+s)
           else:
              delin4.append(cnt)
 #           print('unsuccess: '+s)
       except:
              delin4.append(cnt)
  #          print('unsuccess: '+s)
       cnt=cnt+1
  try: 
     models_urls1_=np.delete(models_urls1_,delin4).tolist()
  except:
     print('no deleted')
  _models_urls1_2=[re.sub(r'\W+', "", x.lower()) for x in _models_urls1_]
  cnt=0
  models_story=[]
  for r1 in range(0,((len(models_urls1_)//15)+1)):
    browser.close()
    sleep(1)
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    browser = webdriver.Firefox(options=opts)
    r2=min((r1+1)*15,len(models_urls1_))
    for cnt in  range(r1*15,r2):
         print(cnt)
         loopurl=models_urls1_[cnt]
         try:
           browser.get(loopurl)
           browser.find_element(By.CSS_SELECTOR, "span.inline-flex.items-center.gap-2.text-gray-95").click()
           page_refn_=browser.page_source
           page_refn = BeautifulSoup(page_refn_, 'lxml')
           model_story=[]
           for p in page_refn.select('div.flex.flex-col.items-start p'):
               model_story.append((p.string))
           print('success:'+loopurl)
         except:
           model_story=[]
           print('unsuccess:'+loopurl)
         models_story.append(model_story)
  dict_modelsstory={}
  for f in range(len(models_urls1_)):
      dict_modelsstory[_models_urls1_2[f]]=models_story[f]
  json.dump(dict_modelsstory , open( f"data_trulux/dict{cntr}{BRND.lower()}.json", 'w' ) )  
  dtsname_=f"dict{cntr}{BRND.lower()}"
  dtsin=dict_modelsstory.copy()
  crud(dtsname=dtsname_,read=False,jsn=True,dtsin=dtsin)     
  cntr=cntr+1

###
dtsname_=f'dict1{BRND.lower()}'
dic_moddd=crud(dtsname=dtsname_,read=True,jsn=True)
dic_moddd[0].pop('_id')
dic_mod=dic_moddd[0]
#dic_mod = json.load(open(f'data_trulux/dict1{BRND.lower()}.json'))
ccc=0
mongo_strext=os.getenv('MONGO_STRING','mongodb://mongoservice:27017/Trulux_catalogue')
client = MongoClient(mongo_strext)
mydatabase = client['Trulux_catalogue']
#for root, dirs, files in os.walk('data_trulux'):
for name in mydatabase.list_collection_names():
  if re.search(r'dict',name): 
   if re.search(rf'{BRND.lower()}',name):
    print(name)
    ccc=ccc+1
print(f'number of models:{ccc-1}')
for t in range(2,ccc):
    dic_mod_={}
    dtsname_=f'dict{t}{BRND.lower()}'
    dct=crud(dtsname=dtsname_,read=True,jsn=True)
    dct[0].pop('_id')
    dct_=dct[0]
    for key,value in dct_.items():
      if value!=[]:
        dic_mod_[key]=value
    dic_mod.update(dic_mod_)

cnt=0
for key,values in dic_mod.items():
    if value!=[]:
        cnt=cnt+1
print(cnt)
dtsname_=f'dict1b{BRND.lower()}'
dic_mod1bbb=crud(dtsname=dtsname_,read=True,jsn=True)
dic_mod1bbb[0].pop('_id')
dic_mod1b=dic_mod1bbb[0]
#dic_mod1b=json.load(open(f'data_trulux/dict1b{BRND.lower()}.json'))

dic_mod1bn={}
for key,value in dic_mod1b.items():
    dic_mod1bn[re.sub(r'\W+', "",key)]=value
dic_mod1bn_={}
for keyn,valuen in dic_mod1bn.items():
    if len(valuen.split(' '))>5:
        dic_mod1bn_[keyn]=valuen
len(dic_mod1bn_)
dtsname_=f'{BRND.lower()}_cataloguev1'
omega_example=crud(dtsname=dtsname_,read=True,jsn=False)
#omega_example=pd.read_excel(f'data_trulux/{BRND.lower()}_cataloguev1.xlsx')

omega_example

omega_example['hodinkee+bezel model description']=''

omega_example['refnum']=omega_example['refnum'].astype('string')

cnt=0
for ss in list(omega_example.index):
 if omega_example.loc[ss,'hodinkee+bezel model description']=='':
    for key,value in dic_mod.items():
       if re.search(omega_example.loc[ss,'refnum'],key):
         dd=','.join(dic_mod[key])
         omega_example.loc[ss,'hodinkee+bezel model description']=dd
         cnt=cnt+1
         break
print(f'found:{cnt}')

cnt=0
for ss in list(omega_example.index):
 if omega_example.loc[ss,'hodinkee+bezel model description']=='':
    for key,value in dic_mod1bn_.items():
       if re.search(omega_example.loc[ss,'refnum'],key):
         dd=dic_mod1bn_[key]
         omega_example.loc[ss,'hodinkee+bezel model description']=dd
         cnt=cnt+1
         break
print(f'found:{cnt}')

omega_example2=omega_example.copy()

for ss in list(omega_example.index):
  if omega_example.loc[ss,'hodinkee+bezel model description']!='':
    if not re.search(omega_example.loc[ss,'refnum'],re.sub(r'\W+',"",omega_example.loc[ss,'hodinkee+bezel model description']).lower()):
      for ff in list(omega_example2.index):
        if omega_example.loc[ss,'Model']==omega_example2.loc[ff,'Model']:
          if omega_example2.loc[ff,'hodinkee+bezel model description']=='':
            omega_example2.loc[ff,'hodinkee+bezel model description']=omega_example.loc[ss,'hodinkee+bezel model description']

sum(omega_example2['hodinkee+bezel model description']=='')

colendwith0=[y for y in list(omega_example2.columns) if y[-1]=='0']
omega_example3=omega_example2[omega_example2['hodinkee+bezel model description']!=''].reset_index(drop=True).drop(colendwith0,axis=1)
omega_example3.to_excel(f"data_trulux/{BRND.lower()}_cataloguev2.xlsx")
dtsname_=f"{BRND.lower()}_cataloguev2"
dtsin=omega_example3.copy()
crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)