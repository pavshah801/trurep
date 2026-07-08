# Commented out IPython magic to ensure Python compatibility.
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import gower
import sys
from warnings import warn
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
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pymongo import MongoClient
from pymongo.server_api import ServerApi
# %matplotlib inline
#logging.basicConfig(filename='chrono24_listing_download.log', level=logging.DEBUG, filemode='a')
SCRNUM=4
MULTI=False
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
BRND='Longines'
BRND = os.getenv('ENV_BRND',BRND)
response = get(url)
if response.status_code != 200:
     warn('Request: {}; Status code: {}'.format(requests, response.status_code))

import nltk
#nltk.download(['punkt', 'stopwords', 'brown', 'gutenberg'])

def crud(dtsname,read=True,jsn=True,dtsin=None):
    mongo_strin=os.getenv('MONGO_STRING','mongodb://mongoservice:27017/Trulux_catalogue')
    client = MongoClient(mongo_strin)
    dtsname=re.sub(' ','',dtsname)
    dtsname=re.sub(r'\W+','',dtsname)
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

BRND=re.sub('& ','',BRND)
BRND=re.sub('ö','',BRND)
BRND=re.sub('è','',BRND)
BRND=re.sub('ü','',BRND)
pd.options.mode.copy_on_write = True

######

dtsname_='caliber_base_new'
caliber_base_new=crud(dtsname=dtsname_,read=True,jsn=False)
#caliber_base_new=pd.read_excel('/kaggle/input/caliber-base/caliber_base_new.xlsx',index_col=0)

caliber_base_new

caliber_columns=caliber_base_new.columns[4:-4]

caliber_referdic={}
for s in list(caliber_base_new.index):
    caliber_referdic[caliber_base_new.loc[s,'code_caliber']]=caliber_base_new.loc[s,caliber_columns].to_dict()

caliber_referdic

dtsname_=f'{BRND.lower()}_cataloguev2'
omega_example=crud(dtsname=dtsname_,read=True,jsn=False)
#omega_example=pd.read_excel(f'/kaggle/input/omega-exm-caliber/{BRND.lower()}_cataloguev2.xlsx')

omega_example['caliber_info']=''

list_qq=[]
list_value=[]
for qq in list(omega_example.index):
 if omega_example.loc[qq,'caliber_info']=='':
  pat=omega_example.loc[qq,'Base caliber']
  for key,value in caliber_referdic.items():
    mask=key.split(':')[-2].split(' ')
    mask.append(key.split(':')[-1])
    if re.search(mask[-3].lower(),pat.lower()):
      if re.search(mask[-2].lower(),pat.lower()):
        if re.search(r'\d+',pat.lower()).group()==mask[-1]:
          if omega_example.loc[qq,'caliber_info']=='':
            list_qq.append(qq)
            list_value.append(value)
 #           print(f'pattern{pat}-mask{mask}-value{value}')
omega_example.loc[list_qq,'caliber_info']=list_value

omega_example

#omega_example[['Base caliber']]

cal_uniq_num=caliber_base_new.groupby('digital_caliber')['digital_caliber'].count()

cal_notrep_num=list((pd.DataFrame(cal_uniq_num).rename_axis('index')[pd.DataFrame(cal_uniq_num).rename_axis('index')['digital_caliber']==1]).index)

cal_notrep_num

list_qq=[]
list_value=[]
for qq in list(omega_example.index):
 if omega_example.loc[qq,'caliber_info']=='':
  pat=str(omega_example.loc[qq,'Caliber/movement'])
  for key,value in caliber_referdic.items():
    mask=key.split(':')[-2].split(' ')
    mask.append(key.split(':')[-1])
    if mask[-2]!='':
      if re.search(mask[-2].lower(),pat.lower()):
       if re.search(r'\d+',pat.lower()):
        if re.search(r'\d+',pat.lower()).group()==mask[-1]:
          if omega_example.loc[qq,'caliber_info']=='':
            list_qq.append(qq)
            list_value.append(value)
 #           print(f'pattern{pat}-mask{mask}-value{value}')
omega_example.loc[list_qq,'caliber_info']=list_value

list_qq=[]
list_value=[]
for qq in list(omega_example.index):
  if omega_example.loc[qq,'caliber_info']=='':
    pat=str(omega_example.loc[qq,'Caliber/movement'])
 #   print(pat)
    for hh in list(caliber_base_new.index):
      cnu=caliber_base_new.loc[hh,'Caliber Number'].split(',')
      for w in range(0,len(cnu)):
        if re.search(re.sub(r'\W+','',cnu[w]).lower(),re.sub(r'\W+','',pat).lower()):
         if re.sub(r'\W+','',cnu[w]).lower()==re.sub(r'\W+','',pat).lower():
           if omega_example.loc[qq,'caliber_info']=='':
              list_qq.append(qq)
              list_value.append(caliber_base_new.loc[hh,caliber_columns].to_dict())
omega_example.loc[list_qq,'caliber_info']=list_value

list_qq=[]
list_value=[]
for qq in list(omega_example.index):
    if omega_example.loc[qq,'caliber_info']=='':
        pat=omega_example.loc[qq,'Base caliber']
        for key,value in caliber_referdic.items():
          mask=key.split(':')[-2].split(' ')
          mask.append(key.split(':')[-1])
          if mask[-1] in cal_notrep_num:
            if re.search(r'\d+',pat.lower()).group()==mask[-1]:
              if omega_example.loc[qq,'caliber_info']=='':
                list_qq.append(qq)
                list_value.append(value)
#                print(f'pattern{pat}-mask{mask}-value{value}')
omega_example.loc[list_qq,'caliber_info']=list_value

omega_example

caliber_referdicst={}
for s in list(caliber_base_new.index):
    caliber_referdicst[caliber_base_new.loc[s,'code_caliber']]=caliber_base_new.loc[s,'caliber_stories']

omega_example['caliber_stories']=''

list_qq=[]
list_value=[]
for qq in list(omega_example.index):
 if omega_example.loc[qq,'caliber_stories']=='':
  pat=omega_example.loc[qq,'Base caliber']
  for key,value in caliber_referdicst.items():
    mask=key.split(':')[-2].split(' ')
    mask.append(key.split(':')[-1])
    if re.search(mask[-3].lower(),pat.lower()):
      if re.search(mask[-2].lower(),pat.lower()):
        if re.search(r'\d+',pat.lower()).group()==mask[-1]:
          if omega_example.loc[qq,'caliber_stories']=='':
            list_qq.append(qq)
            list_value.append(value)
omega_example.loc[list_qq,'caliber_stories']=list_value

list_qq=[]
list_value=[]
for qq in list(omega_example.index):
 if omega_example.loc[qq,'caliber_stories']=='':
  pat=str(omega_example.loc[qq,'Caliber/movement'])
  for key,value in caliber_referdicst.items():
    mask=key.split(':')[-2].split(' ')
    mask.append(key.split(':')[-1])
    if mask[-2]!='':
      if re.search(mask[-2].lower(),pat.lower()):
       if re.search(r'\d+',pat.lower()):
        if re.search(r'\d+',pat.lower()).group()==mask[-1]:
          if omega_example.loc[qq,'caliber_stories']=='':
            list_qq.append(qq)
            list_value.append(value)
omega_example.loc[list_qq,'caliber_stories']=list_value

list_qq=[]
list_value=[]
for qq in list(omega_example.index):
  if omega_example.loc[qq,'caliber_stories']=='':
    pat=str(omega_example.loc[qq,'Caliber/movement'])
    for hh in list(caliber_base_new.index):
      cnu=caliber_base_new.loc[hh,'Caliber Number'].split(',')
      for w in range(0,len(cnu)):
        if re.search(re.sub(r'\W+','',cnu[w]).lower(),re.sub(r'\W+','',pat).lower()):
          if re.sub(r'\W+','',cnu[w]).lower()==re.sub(r'\W+','',pat).lower():
            if omega_example.loc[qq,'caliber_stories']=='':
              list_qq.append(qq)
              list_value.append(caliber_base_new.loc[hh,'caliber_stories'])
omega_example.loc[list_qq,'caliber_stories']=list_value

list_qq=[]
list_value=[]
for qq in list(omega_example.index):
    if omega_example.loc[qq,'caliber_stories']=='':
        pat=omega_example.loc[qq,'Base caliber']
        for key,value in caliber_referdicst.items():
          mask=key.split(':')[-2].split(' ')
          mask.append(key.split(':')[-1])
          if mask[-1] in cal_notrep_num:
            if re.search(r'\d+',pat.lower()).group()==mask[-1]:
              if omega_example.loc[qq,'caliber_stories']=='':
                list_qq.append(qq)
                list_value.append(value)
omega_example.loc[list_qq,'caliber_stories']=list_value

#omega_example.drop(0,axis=1,inplace=True)
omega_example=omega_example.fillna('Unknown')

dtsname_=f'map_subrefnew{BRND.lower()}v1'
map_subrefnew=crud(dtsname=dtsname_,read=True,jsn=False)
map_subrefnew['indexcol']=map_subrefnew['indexcol'].astype('string')
#map_subrefnew=pd.read_excel(f'/kaggle/input/map-subref/map_subrefnew{BRND.lower()}v1.xlsx',dtype={'indexcol': str},index_col=0)

map_subrefnew_dic=map_subrefnew.drop('name',axis=1).set_index('0').to_dict()['indexcol']

map_subrefnew_dic

cllist=['Dial','Bracelet material',
 'Bezel material',
 'Dial numerals',
 'Bracelet color',
 'Clasp material',
 'Clasp','Case material']

omega_example_sub=omega_example[cllist]

omega_example_sub_=pd.get_dummies(omega_example_sub, prefix=['Dia','Brm', 'Bem','Din','Brc','Clm','Cla','Cam'])

sub_refrea=[]
for ww in list(omega_example_sub_.index):
    sub_refv=[]
    sub_refva=''
    for vv in list(omega_example_sub_.columns):
        if omega_example_sub_.loc[ww,vv]==True:
            sub_refv.append(map_subrefnew_dic[vv])
    sub_refva=''.join(sub_refv)
    sub_refrea.append(sub_refva)

omega_example['sub_ref']=sub_refrea

omega_example.columns
###
#refnum_list_calibdrop=list(pd.read_csv(f'/kaggle/input/refnum_list_calibdrop/refnum_list_calibdrop{BRND.lower()}v1.csv',index_col=0)['0'])
#for tt in list(omega_example.index):
# if omega_example.loc[tt,'refnum'] in refnum_list_calibdrop:
#    omega_example.drop([tt],axis=0,inplace=True)
       
omega_example.rename(columns={"Frequency": "Frequency from model"},inplace=True)

omega_example.rename(columns={"Caliber/movement": "Caliber Number1"},inplace=True)

omega_example.rename(columns={"Movement": "Movement1"},inplace=True)

omega_example.rename(columns={"Number of jewels": "Number of jewels1"},inplace=True)

omega_example.rename(columns={"Power reserve": "Power reserve1"},inplace=True)

omega_example.rename(columns={"Base caliber": "Base caliber1"},inplace=True)

omega_example=pd.concat([omega_example,omega_example['caliber_info'].apply(pd.Series)],axis=1)

omega_example.drop(0,axis=1,inplace=True)
omega_example.fillna('Unknown',inplace=True)

omega_example.rename(columns={"Frequency": "Frequency from caliber"},inplace=True)

omega_example.rename(columns={"Caliber Number": "Caliber Number2"},inplace=True)    

omega_example.rename(columns={"Movement Type": "Movement2"},inplace=True)

omega_example.rename(columns={"Jewels": "Number of jewels2"},inplace=True)

omega_example.rename(columns={"Power Reserve": "Power reserve2"},inplace=True)

omega_example.rename(columns={"Base Caliber": "Base caliber2"},inplace=True)

for nn in ["Base caliber2","Movement2","Number of jewels2","Power reserve2","Caliber Number2"]:
    for mm in list(omega_example.index):
        if omega_example.loc[mm,nn]=='Unknown':
            omega_example.loc[mm,nn]=omega_example.loc[mm,(nn[0:-1]+'1')]

for tt in list(omega_example.index):
    b=omega_example.loc[tt,'Caliber Number2'].split(',')
    bb=[]
    for x in b:
      if re.search(r'\d+',x): 
         bb.append(re.search(r'\d+',x).group())
    if re.search(r'\d+',omega_example.loc[tt,'Caliber Number1']):
      if re.search(r'\d+',omega_example.loc[tt,'Caliber Number1']).group() not in bb:
            omega_example.loc[tt,'Caliber Number2']=omega_example.loc[tt,'Caliber Number1']
            
omega_example.drop(["Base caliber1","Movement1","Number of jewels1","Power reserve1","Caliber Number1"],axis=1,inplace=True)

omega_example.drop(["Gender","Location"],axis=1,inplace=True)

omega_example.rename(columns={"Movement2":"Movement","Number of jewels2":"Number of jewels","Power reserve2":"Power reserve","Base caliber2":"Base caliber","Caliber Number2":"Caliber Number"},inplace=True)

omega_example

omega_example[omega_example.caliber_info=='']
####
omega_example.rename(columns={"Frequency from model": "Frequency"},inplace=True)

ms='Unknown'
listfreq=['32768','32,768','32.768']
for xx in list(omega_example.index):
  bridge1=omega_example.loc[xx,'Frequency from caliber']  
  if re.search(r'[^a-zA-Z]+',bridge1):
    if re.search('hz',bridge1.lower()):
      if re.search('khz',bridge1.lower()):
        if re.search(r'[^a-zA-Z]+',bridge1).group() in listfreq:
          ms=re.sub(r'\W+','',bridge1)
        else:
            if re.search(r'\d+',re.sub(r'\W+','',bridge1)):
               ms=str(float(re.search(r'\d+',re.sub(r'\W+','',bridge1)).group())*1000)+' Hz'
            else:
                ms='Unknown'
      else:
        ms=re.sub(r'\W+','',bridge1)
    else:
        ms=re.sub(r'\W+','',bridge1)
  else:
    ms='Unknown'
  omega_example.loc[xx,'Frequency from caliber']=ms

for zz in list(omega_example.index):
  if (omega_example.loc[zz,'Movement']).lower()=='quartz':
    bridge2=omega_example.loc[zz,'Frequency from caliber']
    omega_example.loc[zz,'Frequency']=bridge2
    
ms='Unknown'
exclnum=['2.75','3.5']
for yy in list(omega_example.index):
  bridge3=omega_example.loc[yy,'Frequency']
  if re.search('hz',bridge3.lower()):
    if re.search(r'[^a-zA-Z]+',bridge3):
     ms=re.search(r'[^a-zA-Z]+',bridge3).group()
    else:
      ms='Unknown'  
  elif re.search('a/h',bridge3.lower()):
    if re.search(r'[^a-zA-Z]+',bridge3):
      if re.search(r'\d+',re.sub(r'\W+','',bridge3)):      
        ms=str(round(float(re.search(r'\d+',re.sub(r'\W+','',bridge3)).group())/7200,2))
        if ms in exclnum:
             _=0
        else:
             ms=str(round(float(ms),0))
      else:
        ms='Unknown'
    else:
        ms='Unknown'
  else:
    if re.search(r'[^a-zA-Z]+',bridge3):
      ms='Unknown'
    else:
        ms='Unknown'
  omega_example.loc[yy,'Frequency']=ms

for hh in list(omega_example.index):
   bridge4=omega_example.loc[hh,'Frequency']
   if re.search(r'[^a-zA-Z]+',bridge4):
     if re.search(r'[^a-zA-Z]+',re.sub(r'\W+','',bridge4)).group()=='25200':
        omega_example.loc[hh,'Frequency']='3.5'
     elif re.search(r'[^a-zA-Z]+',re.sub(r'\W+','',bridge4)).group()=='28800':  
        omega_example.loc[hh,'Frequency']='4'    

#for jj in list(omega_example.index):
#   bridge5=omega_example.loc[jj,'Frequency'] 
#   if re.search(',',bridge5):
#       print(bridge5) 
#       omega_example.drop(jj,axis=0,inplace=True)        
        
for uu in list(omega_example.index):
   bridge6=omega_example.loc[uu,'Frequency'] 
   if bridge6[-2:]=='.0':   
     omega_example.loc[uu,'Frequency']=bridge6[:-2]

for zz in list(omega_example.index):
  if (omega_example.loc[zz,'Movement']).lower()=='quartz':
    bridge7=omega_example.loc[zz,'Frequency']
    if bridge7=='Unknown':
       omega_example.loc[zz,'Frequency']='32768'

omega_example['Frequency']=omega_example['Frequency'].astype('string')
omega_example['sub_ref']=omega_example['sub_ref'].astype('string')

omega_example['Country of manufacture for the watch']=''

omega_example['Country of manufacture for the watch']='Switzerland'

extn=list(omega_example.columns)[(list(omega_example.columns).index('PriceUSDthou')+1):list(omega_example.columns).index('hodinkee+bezel model description')]

try:
  omega_example=omega_example[['Hierarchy_code', 'refnum','sub_ref','Brand', 'Model','Country of manufacture for the watch',
       'Case material','Bracelet material','Bezel material', 'Clasp material', 'Clasp','Bracelet color',
       'Dial', 'Dial numerals','Crystal','Number of jewels','Power reserve', 'Movement',
       'Case diameter', 'Water resistance','Thickness','Lug width']+extn+['Complications','Manufacturer/Brand','Base caliber', 'Caliber Number','Country of Manufacture','Frequency','In-House',
       'Hacking Seconds?','hodinkee+bezel model description','caliber_stories']]
except:
    print('no columns,order of columns is not correct')

omega_example.rename(columns={"sub_ref": "sub_ref(index order: Dial,Bracelet material,Bezel material,Dial numerals,Bracelet color,Clasp material,Clasp,Case material)"},inplace=True)

k=0
indlist=list(omega_example.columns)
ind_repcolumns=[]
list_repcolumns=[]
for y in list(omega_example.columns):
  try:
   if y==list(omega_example.columns)[k+1]:
     ind_repcolumns.append(k+1)
   k=k+1
  except:
    print('end of list')
for z in ind_repcolumns:
    if list(omega_example.columns)[z] in ['In-House','Hacking Seconds?']:
        indlist[(z-1)]=list(omega_example.columns)[z]+'rep'
        list_repcolumns.append(indlist[(z-1)])
    else:
        indlist[z]=list(omega_example.columns)[z]+'rep'
        list_repcolumns.append(indlist[z])
#pd.Index(indlist)
omega_example=pd.DataFrame(np.array(omega_example),columns=pd.Index(indlist))
omega_example.drop(list_repcolumns,axis=1,inplace=True)
print(f'deleted:{list_repcolumns}')

try:
  omega_example['Power reserve']=[re.search(r'\d+',y).group() if re.search(r'\d+',y) else '0' for y in list(omega_example['Power reserve'])]
except:
    print('no column')

omega_example['Number of jewels']=omega_example['Number of jewels'].astype('string')

try:
   omega_example['Case diameter']=[re.sub(r'[A-Za-z]+','',y) for y in list(omega_example['Case diameter'])]
except:
   print('no column')

try:
   omega_example['Thickness']=[re.sub(r'[A-Za-z]+','',y) for y in list(omega_example['Thickness'])]
except:
   print('no column')

try:
   omega_example['Lug width']=[re.sub(r'\D+','',y) for y in list(omega_example['Lug width'])]
except:
   print('no column')

omega_example['Thickness']=omega_example['Thickness'].astype('string')
omega_example['Lug width']=omega_example['Lug width'].astype('string')
try:
  omega_example['Thickness']=[y if float(re.search(r'\d+',y).group())<100  else 'Unknown' for y in list(omega_example['Thickness'])] 
except:
   print('no column') 
try:
  omega_example['Lug width']=[y if float(re.search(r'\d+',y).group())<100  else 'Unknown' for y in list(omega_example['Lug width'])] 
except:
   print('no column') 

try:
   omega_example['Water resistance']=[re.sub(r'\D+','',y) for y in list(omega_example['Water resistance'])]
except:
   print('no column')

for bb in list(omega_example.index):
  hc_old=omega_example.loc[bb,'Hierarchy_code']
  if len(hc_old.split('/')[1].split(' '))>2:
    hc_new= hc_old.split('/')[0]+'/'+omega_example.loc[bb,'Model']+'/'+hc_old.split('/')[2]+'/'+hc_old.split('/')[3]
    omega_example.loc[bb,'Hierarchy_code']=hc_new


if BRND=='Cartier':
   omega_example['Manufacturer/Brand']=[re.sub(r'\(.*?\)','',y) for y in list(omega_example['Manufacturer/Brand'])]

try:
  for tt in list(omega_example.index):
    if not re.search(omega_example.loc[tt,'Brand'].lower(),omega_example.loc[tt,'Base caliber'].lower()):
      omega_example.loc[tt,'In-House']='No'
except:
    print('error')

for hh in list(omega_example.index):
  if omega_example.loc[hh,'Base caliber'].isdigit():
    omega_example.loc[hh,'Base caliber']=omega_example.loc[hh,'Brand']+' '+omega_example.loc[hh,'Caliber Number']

for hh in list(omega_example.index):
    if omega_example.loc[hh,'Manufacturer/Brand']==' ':
      if re.search(r'[A-Za-z]+',omega_example.loc[hh,'Base caliber']):     
        omega_example.loc[hh,'Manufacturer/Brand']=re.search(r'[A-Za-z]+',omega_example.loc[hh,'Base caliber']).group()
 #       print(omega_example.loc[hh,'Manufacturer/Brand'])

for hh in list(omega_example.index):
    if re.search('Technically no',omega_example.loc[hh,'In-House']):
        omega_example.loc[hh,'In-House']='No'

if BRND=='Patek Philippe':
    try:
      omega_example['In-House']='Yes'
    except:
        print('no column')

listmov=['690','687','057','157']
if BRND=='Cartier':
 for tt in list(omega_example.index):  
  if re.search(r'\d+',omega_example.loc[tt,'Base caliber']):
    if re.search(r'\d+',omega_example.loc[tt,'Base caliber']).group() in listmov:
      omega_example.loc[tt,'In-House']='No'

listmov=['690','687','057','157']
if BRND=='Cartier':
 for tt in list(omega_example.index):  
  if re.search(r'\d+',omega_example.loc[tt,'Base caliber']):
    if re.search(r'\d+',omega_example.loc[tt,'Base caliber']).group() in listmov:
       omega_example.loc[tt,'Base caliber']='Piaget '+re.search(r'\d+',omega_example.loc[tt,'Base caliber']).group()
       omega_example.loc[tt,'Manufacturer/Brand']='Piaget'

####
if BRND=='Longines':
   for tt in list(omega_example.index):
     for b in (omega_example.loc[tt,'Manufacturer/Brand']).split(' '):
        if b=='ETA':
          omega_example.loc[tt,'Manufacturer/Brand']='ETA'
if BRND=='Tudor':
   for tt in list(omega_example.index):
     for b in (omega_example.loc[tt,'Manufacturer/Brand']).split(' '):
        if b=='Kenissi':
          omega_example.loc[tt,'Manufacturer/Brand']='Kenissi'
if BRND=='Audemars Piguet':
   for tt in list(omega_example.index):
     for b in (omega_example.loc[tt,'Caliber Number']).split(','):
       if re.search('AP',b):     
         if re.search(r'\d+',b):
            omega_example.loc[tt,'Caliber Number']=re.search('AP',b).group()+re.search(r'\d+',b).group()
if BRND=='Tudor':
   for tt in list(omega_example.index):
     for b in (omega_example.loc[tt,'Caliber Number']).split(','):
       if re.search('MT',b):     
         if re.search(r'\d+',b):
            omega_example.loc[tt,'Caliber Number']=re.search('MT',b).group()+re.search(r'\d+',b).group()
if BRND=='Longines':
   for tt in list(omega_example.index):
     if re.search('ETA',omega_example.loc[tt,'Manufacturer/Brand']):
       if not re.search('ETA',omega_example.loc[tt,'Base caliber']):       
          omega_example.loc[tt,'Base caliber']='ETA '+omega_example.loc[tt,'Base caliber']
if BRND=='Longines':
   for tt in list(omega_example.index):
      if re.search('L836.6',omega_example.loc[tt,'Caliber Number']):
          omega_example.loc[tt,'Base caliber']='ETA C07.811'          
if BRND=='Longines':
   for tt in list(omega_example.index):
     if re.search('ETA',omega_example.loc[tt,'Base caliber']):
        omega_example.loc[tt,'Manufacturer/Brand']='Longines'
if BRND=='Tudor':
   for tt in list(omega_example.index):
     if re.search('Kenissi',omega_example.loc[tt,'Manufacturer/Brand']):
        omega_example.loc[tt,'Manufacturer/Brand']='Tudor'
        omega_example.loc[tt,'Base caliber']='Kenissi '+omega_example.loc[tt,'Caliber Number']
if BRND=='Tudor':
   for tt in list(omega_example.index):
     if re.search('T603',omega_example.loc[tt,'Caliber Number']):
        omega_example.loc[tt,'Base caliber']='Sellita SW240-1'
if BRND=='Longines':
    for tt in list(omega_example.index):
        if re.search('A31',omega_example.loc[tt,'Caliber Number']):
           omega_example.loc[tt,'Caliber Number']='L888'
           omega_example.loc[tt,'Base caliber']='ETA A31.L11'
if BRND=='Longines':
    for tt in list(omega_example.index):
        if re.search('L888',omega_example.loc[tt,'Caliber Number']):
           omega_example.loc[tt,'Base caliber']='ETA A31.L11'
####                
omega_example[omega_example.caliber_stories!=''].reset_index(drop=True).to_excel(f"data_trulux/{BRND.lower()}_cataloguev3.xlsx")
dtsname_=f"{BRND.lower()}_cataloguev3"
dtsin=omega_example.copy()
crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)

omega_example.drop(['caliber_stories'],axis=1).to_excel(f"data_trulux/{BRND.lower()}_cataloguev4.xlsx")