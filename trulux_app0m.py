# Commented out IPython magic to ensure Python compatibility.
import requests
import shutil
from bs4 import BeautifulSoup
import re
import json
import os
import time
import xml.etree.ElementTree as ET
import logging
from tqdm import tqdm
import numpy as np
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
UPDATE=False
NPAGES=25
# %matplotlib inline
#logging.basicConfig(filename='chrono24_listing_download.log', level=logging.DEBUG, filemode='a')

#os.system('mkdir test')
#os.system('mkdir testmodels')
#os.system('mkdir testmodelsupd')

"""# Chrono24

## Brief textual and visual content
"""
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
# watch explorer
url_str = "https://www.chrono24.com/api/windowshopping/search.json?modelName=&sortOrder=0&offset={}"

max_valid_models = 50000

######################
cookies = {
    'chronosessid': '59112bbd-82c2-422c-8618-4c4a928be465',
    'timezone': 'Europe/Kiev',
    '__ssid': '5b6ac70e100f9753032a5253253e00b',
    'c24-consent': 'AAAAH8/vwf4=',
    'FPID': 'FPID2.2.ewR6ig5bjRErJUoUmfBskHaLO%2BV6wFAeMPwxuVCHDKg%3D.1694189024',
    '_gcl_au': '1.1.6707372.1694189026',
    '_gid': 'GA1.2.529648636.1694189026',
    '_pin_unauth': 'dWlkPVpHVmtObUZoTURVdE9UWmxOaTAwTkRFeExUa3dOMlF0T1RjNU4ySXdNbVZqWm1RMA',
    '_hjSessionUser_72519': 'eyJpZCI6IjU5ZTQ4N2FlLWViMTItNTZmMy1hMGVjLThjYzVjZDMwY2MxMSIsImNyZWF0ZWQiOjE2OTQxODkwMjU3MjcsImV4aXN0aW5nIjp0cnVlfQ==',
    'pu': 'true',
    'ln_or': 'eyI0NjQ4OCI6ImQifQ%3D%3D',
    'filter-combinations': '2:Man|Mod,0:',
    'userHistory': '29158964|1694371157854|11+24443649|1694370593442|1+29940559|1694370584302|1+28827802|1694368707869|1+22967785|1694368607501|3+29264730|1694368145529|15',
    'search-session': '|6a179a8c_AQ0Yht|0|29158964.29940559.30210271.24908804.27818548.29746351.27561386.30126971.30062052.25777492.27585922.29333387.30473070.22015242.30145512.27561436.24056926.30401334.28449728.30003965.24476162.28565466.28951817.29632645.27891713.25554829.28561621.30383113.28937335.28886644.29727383.24975400.29261498.28226551.27404613.30398070.28909285.28644016.24443649.30448476.29986850.30292707.29727601.8665661.25777493.30007212.29228144.20500268.29773938.25911730.30143600.30228880.24924969.25592417.22942059.28592010.30184127.29402616.30324033.27842937.30000166',
    'csrf-token': '1694444982.CGjT4UDmOYsNaaMI5T0HXqY9TFanfhT_ljtbeyBlmFc.AXG1VdjbkDAJA_goE5-Sb3V3CRmE',
    'last-search-result-ids': '29158964.29940559.30210271.24908804.27818548.29746351.27561386.30126971.30062052.25777492.27585922.29333387.30473070.22015242.30145512.27561436.24056926.30401334.28449728.30003965.24476162.28565466.28951817.29632645.27891713.25554829.28561621.30383113.28937335.28886644.29727383.24975400.29261498.28226551.27404613.30398070.28909285.28644016.24443649.30448476.29986850.30292707.29727601.8665661.25777493.30007212.29228144.20500268.29773938.25911730.30143600.30228880.24924969.25592417.22942059.28592010.30184127.29402616.30324033.27842937.30000166',
    'cfctGroup': 'AAA02%3D%26DOTS01%3D%26SWIP01%3D%26ABSI00%3D%26COTE01%3D%26NORE01%3D%26SOLR00%3D%26CDCO00%3D',
    '_dc_gtm_UA-527734-1': '1',
    '_ga_B8CPBTKGPW': 'GS1.1.1694444983.14.0.1694444983.0.0.0',
    '_hjIncludedInSessionSample_72519': '0',
    '_hjSession_72519': 'eyJpZCI6ImM5MGYyMzQxLWRhM2MtNGNlYy1iMjgxLWMyNzQxYjcwMmJlMyIsImNyZWF0ZWQiOjE2OTQ0NDQ5ODM3NzMsImluU2FtcGxlIjpmYWxzZX0=',
    '_hjAbsoluteSessionInProgress': '0',
    'FPLC': 'kL7KeQOmhjB49i8oz34NZ0bEa7rPl2Ddc%2F6vAWnKSecwgIfzNccg1h8wxbd1lI%2B03X3Rf7Sr0VkGABLLL%2BBIKb2FZ8f%2FZUwSCSyqfMVJszllG9c8yXy8TJWzN2X8BQ%3D%3D',
    'cto_bundle': '0nPIjl9Kb1ZyOERVYWVselhxOXMlMkJZRnZ2SWtsVWpzd08ycDdOTWtFMFBIaCUyRjJiNXRsRU1FNXR4bDJVT2MlMkZPODF0N2EzTlpZcUFoSmxYNmRyNkRQU2Z0S3BMYTRxdFBtZFVnZTdXN0xJcmlvTGpmR3ZSRldIa25aS2dTZWtLODVEenVCcDBOeGN4MzU2NDJoeHNmbldna2k0QjVkejRHYlhFS25aMlcyUkdvS2FrejQ5NXpuTkNPM01LMDlPYVFrZkxJcEJPb05oaGM3ekdyd29lQlklMkIlMkZrRmVoY21haURvYkcwckhGZkFad2NIMWxpYzFxNFYlMkZIaHd0bTJBOFZ4V3JOMk5GRHh5U1J3UWJBeUJKRDJnY3ZBQ3BwQSUzRCUzRA',
    '_ga': 'GA1.2.889355546.1694189024',
    'c24-data': 'eyI1Ijp7ImUiOiIxNjk3MDM2OTgyIiwidiI6IjEifSwiNiI6eyJlIjoiMTY5NzAzNjk4MiIsInYiOiIxIn0sIjkiOnsiZSI6IjE2OTU1ODYwNTIiLCJ2IjoiMTY5NDI5MDA0NzY0MyJ9LCIyNyI6eyJlIjoiMTcyNTk4MDk4MiIsInYiOiIxMyJ9LCIzMCI6eyJlIjoiMTY5NTU4NjA1MyIsInYiOiI4In0sIjM3Ijp7ImUiOiIxNzI1OTgwOTgyIiwidiI6IjE2OTQ0NDQ5ODI5ODQifSwiMzgiOnsiZSI6IjE3MjU3MjUwMjMiLCJ2IjoiMTY5MTUxMDYyMzI1MCJ9LCI0MSI6eyJlIjoiMTcyNTcyNTAyMyIsInYiOiIxNjk0MTg5MDIzMDAwIn0sIjQ0Ijp7ImUiOiIxNjk1NTg2MDUzIiwidiI6IjEifSwiOTgiOnsiZSI6IjE3MjU5ODA5ODIiLCJ2IjoiMSJ9LCIxMTUiOnsidiI6Im1kIiwiZSI6IjE3MDk5OTY5OTkifSwiMjMyIjp7ImUiOiIxNzI1NzI1MDI1IiwidiI6IjE2OTQxODkwMjMzMDEifSwiMjQ3Ijp7ImUiOiIxNzI1NzI2MjI1IiwidiI6IjE2OTQxOTAyMjMxNTkifSwiMjQ4Ijp7ImUiOiIxNzI1NzI2MjI1IiwidiI6IjEifSwiMjQ5Ijp7ImUiOiIxNzI1NzI2MjI1IiwidiI6IjEifSwiNDMzIjp7ImUiOiIxNjk2NzkwMTYxIiwidiI6IjIifSwiNDY1Ijp7ImUiOiIxNzg4Nzk3MDI2IiwidiI6IjE3ODg3OTcwMjYzNzQifX0=',
}

headers = {
    'authority': 'www.chrono24.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6,vi;q=0.5,pt;q=0.4,ka;q=0.3',
    'cache-control': 'max-age=0',
    # 'cookie': 'chronosessid=59112bbd-82c2-422c-8618-4c4a928be465; timezone=Europe/Kiev; __ssid=5b6ac70e100f9753032a5253253e00b; c24-consent=AAAAH8/vwf4=; FPID=FPID2.2.ewR6ig5bjRErJUoUmfBskHaLO%2BV6wFAeMPwxuVCHDKg%3D.1694189024; _gcl_au=1.1.6707372.1694189026; _gid=GA1.2.529648636.1694189026; _pin_unauth=dWlkPVpHVmtObUZoTURVdE9UWmxOaTAwTkRFeExUa3dOMlF0T1RjNU4ySXdNbVZqWm1RMA; _hjSessionUser_72519=eyJpZCI6IjU5ZTQ4N2FlLWViMTItNTZmMy1hMGVjLThjYzVjZDMwY2MxMSIsImNyZWF0ZWQiOjE2OTQxODkwMjU3MjcsImV4aXN0aW5nIjp0cnVlfQ==; pu=true; ln_or=eyI0NjQ4OCI6ImQifQ%3D%3D; filter-combinations=2:Man|Mod,0:; userHistory=29158964|1694371157854|11+24443649|1694370593442|1+29940559|1694370584302|1+28827802|1694368707869|1+22967785|1694368607501|3+29264730|1694368145529|15; search-session=|6a179a8c_AQ0Yht|0|29158964.29940559.30210271.24908804.27818548.29746351.27561386.30126971.30062052.25777492.27585922.29333387.30473070.22015242.30145512.27561436.24056926.30401334.28449728.30003965.24476162.28565466.28951817.29632645.27891713.25554829.28561621.30383113.28937335.28886644.29727383.24975400.29261498.28226551.27404613.30398070.28909285.28644016.24443649.30448476.29986850.30292707.29727601.8665661.25777493.30007212.29228144.20500268.29773938.25911730.30143600.30228880.24924969.25592417.22942059.28592010.30184127.29402616.30324033.27842937.30000166; csrf-token=1694444982.CGjT4UDmOYsNaaMI5T0HXqY9TFanfhT_ljtbeyBlmFc.AXG1VdjbkDAJA_goE5-Sb3V3CRmE; last-search-result-ids=29158964.29940559.30210271.24908804.27818548.29746351.27561386.30126971.30062052.25777492.27585922.29333387.30473070.22015242.30145512.27561436.24056926.30401334.28449728.30003965.24476162.28565466.28951817.29632645.27891713.25554829.28561621.30383113.28937335.28886644.29727383.24975400.29261498.28226551.27404613.30398070.28909285.28644016.24443649.30448476.29986850.30292707.29727601.8665661.25777493.30007212.29228144.20500268.29773938.25911730.30143600.30228880.24924969.25592417.22942059.28592010.30184127.29402616.30324033.27842937.30000166; cfctGroup=AAA02%3D%26DOTS01%3D%26SWIP01%3D%26ABSI00%3D%26COTE01%3D%26NORE01%3D%26SOLR00%3D%26CDCO00%3D; _dc_gtm_UA-527734-1=1; _ga_B8CPBTKGPW=GS1.1.1694444983.14.0.1694444983.0.0.0; _hjIncludedInSessionSample_72519=0; _hjSession_72519=eyJpZCI6ImM5MGYyMzQxLWRhM2MtNGNlYy1iMjgxLWMyNzQxYjcwMmJlMyIsImNyZWF0ZWQiOjE2OTQ0NDQ5ODM3NzMsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; FPLC=kL7KeQOmhjB49i8oz34NZ0bEa7rPl2Ddc%2F6vAWnKSecwgIfzNccg1h8wxbd1lI%2B03X3Rf7Sr0VkGABLLL%2BBIKb2FZ8f%2FZUwSCSyqfMVJszllG9c8yXy8TJWzN2X8BQ%3D%3D; cto_bundle=0nPIjl9Kb1ZyOERVYWVselhxOXMlMkJZRnZ2SWtsVWpzd08ycDdOTWtFMFBIaCUyRjJiNXRsRU1FNXR4bDJVT2MlMkZPODF0N2EzTlpZcUFoSmxYNmRyNkRQU2Z0S3BMYTRxdFBtZFVnZTdXN0xJcmlvTGpmR3ZSRldIa25aS2dTZWtLODVEenVCcDBOeGN4MzU2NDJoeHNmbldna2k0QjVkejRHYlhFS25aMlcyUkdvS2FrejQ5NXpuTkNPM01LMDlPYVFrZkxJcEJPb05oaGM3ekdyd29lQlklMkIlMkZrRmVoY21haURvYkcwckhGZkFad2NIMWxpYzFxNFYlMkZIaHd0bTJBOFZ4V3JOMk5GRHh5U1J3UWJBeUJKRDJnY3ZBQ3BwQSUzRCUzRA; _ga=GA1.2.889355546.1694189024; c24-data=eyI1Ijp7ImUiOiIxNjk3MDM2OTgyIiwidiI6IjEifSwiNiI6eyJlIjoiMTY5NzAzNjk4MiIsInYiOiIxIn0sIjkiOnsiZSI6IjE2OTU1ODYwNTIiLCJ2IjoiMTY5NDI5MDA0NzY0MyJ9LCIyNyI6eyJlIjoiMTcyNTk4MDk4MiIsInYiOiIxMyJ9LCIzMCI6eyJlIjoiMTY5NTU4NjA1MyIsInYiOiI4In0sIjM3Ijp7ImUiOiIxNzI1OTgwOTgyIiwidiI6IjE2OTQ0NDQ5ODI5ODQifSwiMzgiOnsiZSI6IjE3MjU3MjUwMjMiLCJ2IjoiMTY5MTUxMDYyMzI1MCJ9LCI0MSI6eyJlIjoiMTcyNTcyNTAyMyIsInYiOiIxNjk0MTg5MDIzMDAwIn0sIjQ0Ijp7ImUiOiIxNjk1NTg2MDUzIiwidiI6IjEifSwiOTgiOnsiZSI6IjE3MjU5ODA5ODIiLCJ2IjoiMSJ9LCIxMTUiOnsidiI6Im1kIiwiZSI6IjE3MDk5OTY5OTkifSwiMjMyIjp7ImUiOiIxNzI1NzI1MDI1IiwidiI6IjE2OTQxODkwMjMzMDEifSwiMjQ3Ijp7ImUiOiIxNzI1NzI2MjI1IiwidiI6IjE2OTQxOTAyMjMxNTkifSwiMjQ4Ijp7ImUiOiIxNzI1NzI2MjI1IiwidiI6IjEifSwiMjQ5Ijp7ImUiOiIxNzI1NzI2MjI1IiwidiI6IjEifSwiNDMzIjp7ImUiOiIxNjk2NzkwMTYxIiwidiI6IjIifSwiNDY1Ijp7ImUiOiIxNzg4Nzk3MDI2IiwidiI6IjE3ODg3OTcwMjYzNzQifX0=',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
}
params = {
    'sortorder': '5',
}

##################################################

cnt1=0
cnt2=50
link_index=30*cnt1
product_links = list()

with tqdm(desc="Model listings links collection", total=max_valid_models) as pbar:

  while len(product_links) < max_valid_models:
  #      if link_index>(30*cnt2):
  #        break
        url_ = url_str.format(link_index)
 #       print(link_index)
        response = requests.get(f'{url_}', params=params, cookies=cookies, headers=headers)
        products_json = response.json()['products']

        if len(products_json)==0:
            print('No more links')
            break

        ii = 0   # count valid links
        link_index += len(products_json)   # count total links
        for prod in products_json:
            try:
                resp = requests.get(
                  prod['imageUrl2x'],
                  cookies=cookies,
                  headers=headers,
                )
                if UPDATE:
                  dtsname_='refnum_list'  
                  if prod['referenceNumber'] not in list(crud(dtsname=dtsname_,read=True,jsn=False)['0']):
                     file_path_mod=os.path.join('testmodelsupd', prod['referenceNumber'])
                     if resp.status_code == 200:
                       with open(file_path_mod, "wb") as image_file_model:
                         image_file_model.write(resp.content)
                else:
                   file_path_mod=os.path.join('testmodels', prod['referenceNumber'])
                   if resp.status_code == 200:
                     with open(file_path_mod, "wb") as image_file_model:
                       image_file_model.write(resp.content)
                prod_url = prod['url']
                name = f"{prod['manufacturerName']}={prod['name']}={prod['referenceNumber']}"
                # product_links.append({'name':name, 'url':prod_url})
                product_links.append({'brand':prod['manufacturerName'], 'name':prod['name'], 'refnum':prod['referenceNumber'], 'url':prod_url})

                ii+=1
            except Exception as err:
                print(err)

        pbar.update(ii)
        time.sleep(0.1)

#with open("/kaggle/working/model_links_all1.json", "w", encoding="utf-8") as file:
#    file.write(json.dumps(product_links, indent=4))
dtsname_="model_links_all1"
dtsin=product_links
crud(dtsname=dtsname_,read=False,jsn=True,dtsin=dtsin)                                      

def get_model_listing_links(root_url, cookies, headers):

    response = requests.get(root_url, cookies=cookies, headers=headers)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    prefix = ""  # saving some space in the file. full url would include "https://www.chrono24.com"
    arr_ = [prefix+a['href'] for a in soup.select('div.article-item-container.wt-search-result.article-image-carousel a')]

    return arr_

def get_model_listing_links_multipage(npages,root_url, cookies, headers):
  arr_=[]
  response = requests.get(root_url, cookies=cookies, headers=headers)
  if response.status_code != 200:
        return []
  soup = BeautifulSoup(response.text, 'html.parser')
  prefix = ""  # saving some space in the file. full url would include "https://www.chrono24.com"
  arr_.extend([prefix+a['href'] for a in soup.select('div.article-item-container.wt-search-result.article-image-carousel a')])

  for cnt in range(1,npages):
   try:
    rootp_url=f'{root_url}&showpage={cnt+1}'
    response = requests.get(rootp_url, cookies=cookies, headers=headers)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    prefix = ""  # saving some space in the file. full url would include "https://www.chrono24.com"
    arr_.extend([prefix+a['href'] for a in soup.select('div.article-item-container.wt-search-result.article-image-carousel a')])
   except:
    print('no page')
   # break
  return arr_

listings_threshold = 20    # how many link for model to be valid
max_valid_models = 50000     # how many valid models to collect
save_intervals = 50
save_intervals_wait = 5
wait_time = 0.5
if UPDATE:
     productsold=crud(dtsname='model_links_listings',read=True,jsn=True)                                 
     dtsname_="model_links_listingsold"
     dtsin=pd.json_normalize(productsold,max_level=0).drop('_id',axis=1).fillna('Unknown')
     crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)

products=crud(dtsname='model_links_all1',read=True,jsn=True)                                      

#collect valid models
valid_models=0
with tqdm(desc="Valid model collection", total=max_valid_models) as pbar:
    for ii, prod in enumerate(products):
        pbar.set_description(f"Processing item {ii}")
        if 'listings' in prod.keys():
            if prod['listings']>0:
                continue

        try:
            listings_urls = get_model_listing_links_multipage(NPAGES,prod['url'], cookies, headers)
            products[ii]['listings']=len(listings_urls)
            products[ii]['listing_urls']=listings_urls
            time.sleep(wait_time)

            if len(listings_urls) > listings_threshold:
                valid_models+=1
                pbar.update(1)

                if valid_models>=max_valid_models:
                    break

                if valid_models%save_intervals==0:
                                      
                     dtsname_="model_links_listings"
                     dtsin=pd.json_normalize(products,max_level=0).drop('_id',axis=1).fillna('Unknown')
                     crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)                                                 
        except Exception as err:
            print(err, '\n', prod)
            products[ii]['listings']=0
            products[ii]['listing_urls']=[]
            continue
dtsname_="model_links_listings"
dtsin=pd.json_normalize(products,max_level=0).drop('_id',axis=1).fillna('Unknown')
crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)                                      
#with open(fname_listings, "w", encoding="utf-8") as file:
#       file.write(json.dumps(products, indent=4))
print('Completed!')