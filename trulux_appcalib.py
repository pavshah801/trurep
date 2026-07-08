import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import gower
import sys
from warnings import warn
import kmodes
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
# %matplotlib inline
MULTI=False
CALNUMONLY=False
BRND='Rolex'
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
opts = FirefoxOptions()
opts.add_argument("--headless")
browser = webdriver.Firefox(options=opts)
url='https://calibercorner.com/shop/'
session = requests.Session()
# send a get request to the server
response = session.get(url)
# print the response dictionary
cookies=session.cookies.get_dict()
print(session.cookies.get_dict())
response = get(url)
if response.status_code != 200:
     warn('Request: {}; Status code: {}'.format(requests, response.status_code))
        
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

pd.options.mode.copy_on_write = True

browser.get(url)
page_brandscaliber_=browser.page_source
page_brandscaliber = BeautifulSoup(page_brandscaliber_, 'lxml')

brands=[]
for j in page_brandscaliber.find_all('div',class_='menu-wrap menu-wrap-minus-10')[1].find_all('li'):
    print(j.a['href'].split('/')[-1])
    brands.append(j.a['href'].split('/')[-1])

brands

br=brands[-1]

url_caliber=f'https://calibercorner.com/tag/{br}/?filtered=atoz'

url_caliber

browser.get(url_caliber)
page_caliber_=browser.page_source
page_caliber = BeautifulSoup(page_caliber_, 'lxml')

page_caliber.find('div',class_='block block-26 tipi-flex').find_all('div',class_='title-wrap')

for t in  page_caliber.find('div',class_='block block-26 tipi-flex').find_all('div',class_='title-wrap'):
  if re.search(r'\d+',t.h3.a['href']) :
    print(t.h3.a['href'])
    print(t.string)

url_caliberadd=f'https://calibercorner.com/tag/{br}/page/2/?filtered=atoz'

browser.get(url_caliberadd)
page_caliberadd_=browser.page_source
page_caliberadd = BeautifulSoup(page_caliberadd_, 'lxml')

for t in  page_caliberadd.find('div',class_='block block-26 tipi-flex').find_all('div',class_='title-wrap'):
  if re.search(r'\d+',t.h3.a['href']) :
    print(t.h3.a['href'])
    print(t.string)

caliber_url=[]
caliber_name=[]
caliber_brand=[]
for br in brands:
    print(br)
    url_caliber=f'https://calibercorner.com/tag/{br}/?filtered=atoz'
    browser.get(url_caliber)
    page_caliber_=browser.page_source
    page_caliber = BeautifulSoup(page_caliber_, 'lxml')
    for t in  page_caliber.find('div',class_='block block-26 tipi-flex').find_all('div',class_='title-wrap'):
       if re.search(r'\d+',t.h3.a['href']) :
         caliber_url.append(t.h3.a['href'])
         caliber_name.append(t.string)
         caliber_brand.append(br)
    try:
      url_caliberadd=f'https://calibercorner.com/tag/{br}/page/2/?filtered=atoz'
      browser.get(url_caliberadd)
      page_caliberadd_=browser.page_source
      page_caliberadd = BeautifulSoup(page_caliberadd_, 'lxml')
      for t in  page_caliberadd.find('div',class_='block block-26 tipi-flex').find_all('div',class_='title-wrap'):
         if re.search(r'\d+',t.h3.a['href']) :
           caliber_url.append(t.h3.a['href'])
           caliber_name.append(t.string)
           caliber_brand.append(br)
    except:
        print('no page 2')

allbrands=list(pd.read_excel(f'/kaggle/input/allbrands/table_of_brands.xlsx').brands)#for all brands

#allbrands=['Omega','Longines']#for test brands

for br in allbrands:
    print(br)
    url_caliber=f'https://calibercorner.com/?s={br}'
    browser.get(url_caliber)
    page_caliber_=browser.page_source
    page_caliber = BeautifulSoup(page_caliber_, 'lxml')
    for t in  page_caliber.find('div',class_='block block-27 tipi-flex').find_all('div',class_='title-wrap'):
       if re.search(r'\d+',t.h3.a['href']) :
         caliber_url.append(t.h3.a['href'])
         caliber_name.append(t.string)
         caliber_brand.append(br.lower())
    try:
      url_caliberadd=f'https://calibercorner.com/page/2/?s={br}'
      browser.get(url_caliberadd)
      page_caliberadd_=browser.page_source
      page_caliberadd = BeautifulSoup(page_caliberadd_, 'lxml')
      for t in  page_caliberadd.find('div',class_='block block-27 tipi-flex').find_all('div',class_='title-wrap'):
         if re.search(r'\d+',t.h3.a['href']) :
           caliber_url.append(t.h3.a['href'])
           caliber_name.append(t.string)
           caliber_brand.append(br.lower())
    except:
        print('no page 2')

caliber_base=pd.DataFrame()

caliber_base['caliber_url']=caliber_url
caliber_base['caliber_brand']=caliber_brand
caliber_base['caliber_name']=caliber_name
caliber_base

url_cal='https://calibercorner.com/ball-caliber-rr1103/'
browser.get(url_cal)
page_cal_=browser.page_source
page_cal = BeautifulSoup(page_cal_, 'lxml')

page_cal.find('div',class_='entry-content body-color clearfix link-color-wrap progresson').table.tbody.find_all('tr')

cal_features=[]
for u in page_cal.find('div',class_='entry-content body-color clearfix link-color-wrap progresson').table.tbody.find_all('tr'):
    for v in u.find_all('td'):
      if v.string==None:
        try:
            print(v.a.text)
        except:
           try:
            print(v.find('strong').text)
           except:
            try:
              print(v.find('span').text)
            except:
                print('err')
      else:
        print(v.string)

cal_features=[]
for u in page_cal.find('div',class_='entry-content body-color clearfix link-color-wrap progresson').table.tbody.find_all('tr'):
    for v in u.find_all('td'):
      if v.string==None:
        try:
            cal_features.append(v.a.text)
        except:
           try:
            cal_features.append(v.find('strong').text)
           except:
             try:
               cal_features.append(v.find('span').text)
             except:
               cal_features.append('Unknown')
      else:
        cal_features.append(v.string)

cal_dict={}
cnt=0
for cnt in range(0,len(cal_features),2):
    cal_dict[cal_features[cnt].split('\n')[0]]=cal_features[cnt+1].split('\n')[0]

cal_dict

counter=0
delin1=[]
list_cal_dict=[]
for s in list(caliber_base['caliber_url']):
    print(f'caliber:{counter}')
    cal_features=[]
    url_cal=s
    browser.close()
    sleep(0.5)
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    browser = webdriver.Firefox(options=opts)
    try:
      browser.get(url_cal)
      page_cal_=browser.page_source
      page_cal = BeautifulSoup(page_cal_, 'lxml')
      for u in page_cal.find('div',class_='entry-content body-color clearfix link-color-wrap progresson').table.tbody.find_all('tr'):
        for v in u.find_all('td'):
          if v.string==None:
            try:
                cal_features.append(v.a.text)
            except:
              try:
                cal_features.append(v.find('strong').text)
              except:
               try:
                 cal_features.append(v.find('span').text)
               except:
                 cal_features.append('Unknown')
          else:
            cal_features.append(v.string)
      cal_dict={}
      cnt=0
      for cnt in range(0,len(cal_features),2):
         cal_dict[cal_features[cnt].split('\n')[0]]=cal_features[cnt+1].split('\n')[0]
      list_cal_dict.append(cal_dict)
      counter=counter+1
    except:
        print('no caliber info')
        delin1.append(counter)
        counter=counter+1
len(list_cal_dict)

delin1

caliber_base_=caliber_base.drop(delin1,axis=0).reset_index(drop=True)

caliber_base_['info']=list_cal_dict

caliber_base_

caliber_base_new=pd.concat([caliber_base_,caliber_base_['info'].apply(pd.Series)],axis=1)

caliber_base_new

for k in  list(caliber_base_new.index):
   if re.search(' vs. ' ,caliber_base_new.loc[k,'caliber_name'].lower()):
      caliber_base_new.drop(k,axis=0,inplace=True)

for f in  list(caliber_base_new.columns):
    if caliber_base_new[f].isna().sum()==len(caliber_base_new[f]):
        caliber_base_new.drop(f,axis=1,inplace=True)

print(list(caliber_base_new.columns))

#for x in caliber_base_new.index:
#    if x not in caliber_base_new[caliber_base_new['Base Caliber:'].isna()].index:
#        print(x)

list(caliber_base_new.isna().sum().sort_values()[0:30].index)

caliber_base_new=caliber_base_new[list(caliber_base_new.isna().sum().sort_values()[0:50].index)]
caliber_base_new

caliber_base_new.isna().sum().sort_values()

#caliber_base_new.to_excel("caliber_base_new.xlsx")

######

#caliber_base_new=pd.read_excel('/kaggle/input/caliber-base/caliber_base_new.xlsx',index_col=0)
caliber_base_new=caliber_base_new.reset_index(drop=True)
caliber_base_new

caliber_base_new.isna().sum()

caliber_base_new[caliber_base_new[['Manufacturer','Brand']].isna().sum(axis=1)!=1][['Manufacturer','Brand']]

caliber_base_new_=caliber_base_new[['Manufacturer','Brand']].fillna('')

caliber_base_new_['Manufacturer/Brand']=[list(caliber_base_new_.Manufacturer)[i]+' '+list(caliber_base_new_.Brand)[i] for i in range(0,caliber_base_new_.shape[0])]

caliber_base_new_

#caliber_base_new_.loc[133]

caliber_base_new['Manufacturer/Brand']=caliber_base_new_['Manufacturer/Brand']

caliber_base_new.drop(['Manufacturer','Brand'],axis=1,inplace=True)

caliber_base_new.columns

caliber_base_new=caliber_base_new[['caliber_url', 'caliber_brand', 'caliber_name', 'info', 'Manufacturer/Brand']+list(caliber_base_new.columns)[4:-1]]

pd.Series([re.search(r'\D+',y).group() for y in list(caliber_base_new.caliber_name)]).unique()

caliber_base_new.loc[:,'textual_caliber']=[re.search(r'\D+',y).group() for y in list(caliber_base_new.caliber_name)]

pd.Series([re.search(r'\d+',y).group() for y in list(caliber_base_new.caliber_name)]).nunique()

caliber_base_new.loc[:,'digital_caliber']=[re.search(r'\d+',y).group() for y in list(caliber_base_new.caliber_name)]

caliber_base_new

for v in list(caliber_base_new.index):
    ref=' '.join([y for y in caliber_base_new.loc[v,'textual_caliber'].split(' ') if y.lower()!='caliber'])
    caliber_base_new.loc[v,'textual_caliber']=ref

caliber_base_new

for g in list(caliber_base_new.columns)[5:-3] :
  cnt=0
  for h in list(caliber_base_new.index):
     if caliber_base_new.loc[h,g]=='Unknown':
       cnt=cnt+1
  print(f'({g}:{cnt}')

caliber_base_new.textual_caliber.unique()

cal_uniq_num=caliber_base_new.groupby('digital_caliber')['digital_caliber'].count()

cal_uniq_num

cal_notrep_num=list((pd.DataFrame(cal_uniq_num).rename_axis('index')[pd.DataFrame(cal_uniq_num).rename_axis('index')['digital_caliber']==1]).index)

cal_notrep_num

caliber_base_new['code_caliber']=''
for u in list(caliber_base_new.index):
  caliber_base_new.loc[u,'code_caliber']=caliber_base_new.loc[u,'textual_caliber']+':'+caliber_base_new.loc[u,'digital_caliber']

caliber_base_new.fillna('Unknown',inplace=True)

caliber_base_new

caliber_base_new.columns[4:-3]

#caliber_base_new.loc[100,list(caliber_base_new.columns[4:-3])].to_dict()

caliber_columns=caliber_base_new.columns[4:-3]

caliber_referdic={}
for s in list(caliber_base_new.index):
    caliber_referdic[caliber_base_new.loc[s,'code_caliber']]=caliber_base_new.loc[s,caliber_columns].to_dict()

caliber_referdic

##add caliber stories

browser.close()
opts = FirefoxOptions()
opts.add_argument("--headless")
browser = webdriver.Firefox(options=opts)
url_cal='https://calibercorner.com/eta-caliber-256-041/'
browser.get(url_cal)
page_cal_=browser.page_source
page_cal = BeautifulSoup(page_cal_, 'lxml')

caliber_story=[]
for item in page_cal.find_all('p'):
    print(item.text)

caliber_story=[]
for item in page_cal.find_all('p'):
    caliber_story.append(item.text)
    if item.text=='For off topic or general watch questions, post in the Caliber Corner Forum.':
        break

''.join(''.join(caliber_story[0:-1]).split('\n'))

counter=0
caliber_stories=[]
browser.close()
opts = FirefoxOptions()
opts.add_argument("--headless")
browser = webdriver.Firefox(options=opts)
for b in caliber_base_new.caliber_url:
    print(counter+1)
#    browser.close()
#    sleep(0.5)
#    opts = FirefoxOptions()
#    opts.add_argument("--headless")
#    browser = webdriver.Firefox(options=opts)
    url_cal=b
    browser.get(url_cal)
    page_cal_=browser.page_source
    page_cal = BeautifulSoup(page_cal_, 'lxml')
    caliber_story=[]
    for item in page_cal.find_all('p'):
      caliber_story.append(item.text)
      if item.text=='For off topic or general watch questions, post in the Caliber Corner Forum.':
        counter=counter+1
        break
    caliber_stories.append(''.join(''.join(caliber_story[0:-1]).split('\n')))

caliber_base_new['caliber_stories']=caliber_stories

caliber_base_new

caliber_referdicst={}
for s in list(caliber_base_new.index):
    caliber_referdicst[caliber_base_new.loc[s,'code_caliber']]=caliber_base_new.loc[s,'caliber_stories']

dtsname_="caliber_base_new"
dtsin=caliber_base_new.copy()
crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)
#caliber_base_new.to_excel("caliber_base_new.xlsx")