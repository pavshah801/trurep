# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
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
# %matplotlib inline
#logging.basicConfig(filename='chrono24_listing_download.log', level=logging.DEBUG, filemode='a')

#os.system('mkdir test')

"""# Chrono24

## Detailed textual content
"""

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

def download_img(img_url, dir_name, zoom_, cookies, headers, verbose=1):
    return img_url
#############################################################

def download_images(links,refn,urls_list, download_path, download_zoom_images=True, download_data_image=False, max_listings = 500, verbose=1):
    list_dataupd=[]
    count = 0
    link_dict = {}
    results = [0]*len(links)

    for www in links:
      if www not in urls_list:
        try:
            if count >= max_listings:
                break

            url = 'https://www.chrono24.com'+www.strip()

 #           logging.debug('{:6d} - {}'.format(count+1, url))

            pattern = r"id(\d+).htm"
            match = re.search(pattern, url)

            if match:
                id_ = match.group(1)
                directory_name = id_

 #           directory_name = os.path.join(download_path, directory_name)
 #           os.makedirs(directory_name, exist_ok=True)

            cookies = {
                'search-session': '|6a179a8c_zuamIi|0|29158964.29940559.24908804.24443649.27561386.27818548.30401334.29746351.30383113.25777492.24056926.27891713.29333387.27561436.28565466.30062052.30145512.30003965.28449728.25554829.22015242.30184127.28561621.29727383.28937335.30143600.29856183.28226551.28644016.28951817.24476162.30398070.30394802.28909285.28755931.29727601.29228144.25777493.24975400.29069179.29986850.30387912.30007212.30089089.27585922.28592010.25592417.30031494.28886644.25911730.29773938.22942059.29632645.28628991.30402696.22107117.29402616.30184149.30193177.29635311.30090003',
                'chronosessid': 'f84e7257-84c8-4d1f-894f-e4868ef0e245',
                'filter-combinations': '2:Man|Mod,0:',
                'csrf-token': '1694171142.2SV2xgqXVvLjDACNnGTKUZ2CbzRvEoYWSXPS58UGy6o.AXG1Vdi64lSwzHjhFKkDZcPXRsl6',
                'timezone': 'Europe/Kiev',
                '__ssid': '48fcab77fc77e691a2f766df428787c',
                'consent-session': '2d85fd1c-d0c6-4041-b254-22c82c846aa0',
                'c24-consent': 'AAAAH8/vwf4=',
                'FPID': 'FPID2.2.SNMSTPBdw09c%2FOemDe2nY1YKAHe20RIAOmbxmmiUlZw%3D.1694171145',
                '_gcl_au': '1.1.1505745328.1694171148',
                '_gid': 'GA1.2.1778751159.1694171148',
                'last-search-result-ids': '29158964.29940559.24908804.24443649.27561386.27818548.30401334.29746351.30383113.25777492.24056926.27891713.29333387.27561436.28565466.30062052.30145512.30003965.28449728.25554829.22015242.30184127.28561621.29727383.28937335.30143600.29856183.28226551.28644016.28951817.24476162.30398070.30394802.28909285.28755931.29727601.29228144.25777493.24975400.29069179.29986850.30387912.30007212.30089089.27585922.28592010.25592417.30031494.28886644.25911730.29773938.22942059.29632645.28628991.30402696.22107117.29402616.30184149.30193177.29635311.30090003',
                'pu': 'true',
                '_hjFirstSeen': '1',
                '_hjIncludedInSessionSample_72519': '0',
                '_hjSession_72519': 'eyJpZCI6ImQ1ZmQxYTE3LWY0OTAtNDJjOS04ZjAwLTU3ZmY3NzEyZmI3NiIsImNyZWF0ZWQiOjE2OTQxNzExNDg1OTMsImluU2FtcGxlIjpmYWxzZX0=',
                '_hjAbsoluteSessionInProgress': '0',
                '_pin_unauth': 'dWlkPU0yRTROalF3TVdFdE16VmtNUzAwWTJObUxUbGxNR1V0TTJGbE56SmhaV0kwTldWaA',
                'FPLC': 'mTIoupLBIcfCnnmb61qDw7xjgXQ%2F5THEPP%2BJeYCB4N0RvK%2Ffy4KJBybBKJxo9rlWA%2FEGH89e32sHMtMAB0vL7pauV0S7ss0d9fGYAHzZ4BmpzeRRUbpg6S1UQifzQQ%3D%3D',
                'cfctGroup': 'DOTS00%3D%26AAA00%3D%26ABSI00%3D%26SWIP00%3D%26COTE00%3D%26NORE01%3D%26SOLR00%3D%26CDCO00%3D',
                '_hjSessionUser_72519': 'eyJpZCI6IjVmZTU3ZWNjLTBjMzctNWUwMC05ZmM5LTQ0MTVkZTVlNzcxOSIsImNyZWF0ZWQiOjE2OTQxNzExNDg1OTIsImV4aXN0aW5nIjp0cnVlfQ==',
                'ln_or': 'eyI0NjQ4OCI6ImQifQ%3D%3D',
                'userHistory': '29158964|1694171215786|2',
                'cto_bundle': 'zuTvyl9GeHZUdE0lMkJlNjlYc3pEZFNIS0ZWYXdjJTJGWkxPSUFFdkF6NTBqVUQzTkNxNlZOSHdESFYlMkZDJTJCbHBRT1BGT3ZSWlJxJTJCVlIlMkZSZnV1VWM2NnFoUFNxSGNrdm1oYmp6Qm5NN0pFa1Jpd0wlMkIlMkZCUUVUZ1F1UEljTVZsbXgyQXdtR0ZuTFhIY0IydXpMODlUeGhIQ3VoUzNEQXo1cGl6bCUyQkJoYVlKSWNKM1g2Zk9tSk1kODE4cDJvWjRiM0VNTFZ6RjklMkJickY0Rk00YUpQSDAwV1dRNEpvZUhvJTJCZyUzRCUzRA',
                '_derived_epik': 'dj0yJnU9WGlGQzdfcU5OTUZQY2U1Y2tZSnFOTVA2eERId1RkLWQmbj01dkpiSXd5TjNFM3FWYzBvVkcyTXFnJm09ZiZ0PUFBQUFBR1Q3QUZFJnJtPWYmcnQ9QUFBQUFHVDdBRkUmc3A9NQ',
                'c24-data': 'eyI1Ijp7ImUiOiIxNjk2NzYzMjE2IiwidiI6IjYifSwiNiI6eyJlIjoiMTY5Njc2MzIxNiIsInYiOiI2In0sIjI3Ijp7ImUiOiIxNzI1NzA3MTQyIiwidiI6IjEifSwiMzYiOnsiZSI6IjE3MjU3MDcxNDIiLCJ2IjoiMTY5NDE3MTE0MjEwMiJ9LCIzNyI6eyJlIjoiMTcyNTcwNzE0MiIsInYiOiIxNjk0MTcxMTQyMTAyIn0sIjM4Ijp7ImUiOiIxNzI1NzA3MTQyIiwidiI6IjE2OTE0OTI3NDIxMDIifSwiNDEiOnsiZSI6IjE3MjU3MDcxNDIiLCJ2IjoiMTY5NDE3MTE0MjAwMCJ9LCI5OCI6eyJlIjoiMTcyNTcwNzIxNiIsInYiOiI2In0sIjExNSI6eyJ2IjoibWQiLCJlIjoiMTcwOTcyMzIzNCJ9LCIyMzIiOnsiZSI6IjE3MjU3MDcyMDciLCJ2IjoiMTY5NDE3MTIwMjcwMyJ9LCI0NjUiOnsiZSI6IjE3ODg3NzkxNDYiLCJ2IjoiMTc4ODc3OTE0NjM2NSJ9fQ==',
                '_ga': 'GA1.2.1621830338.1694171145',
                '_dc_gtm_UA-527734-1': '1',
                '_ga_B8CPBTKGPW': 'GS1.1.1694171145.1.1.1694171446.0.0.0',
            }

            headers = {
                'authority': 'www.chrono24.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6,vi;q=0.5,pt;q=0.4,ka;q=0.3',
                'cache-control': 'max-age=0',
                'referer': 'https://www.upwork.com/',
                'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            }

            response = requests.get(f'{url}', cookies=cookies, headers=headers)

            if response.status_code == 200:
                html_content = response.text

                soup = BeautifulSoup(html_content, 'html.parser')
                prod = soup.find("section", class_='js-details-and-security-tabs').find_all('tbody')

                data = {}
                data["URL"] = {"url": url}
                data['refnum']=refn

                for i in prod:
                    tr_s = i.find_all('tr')

                    current_category = ''
                    category_data = {}

                    for y in i.find_all('tr'):

                        try:
                            current_category = y.find('h3').text.strip()
                        except:
                            td_s = y.find_all('td')
                            if len(td_s) > 1:
                                key = td_s[0].text.strip()
                                value_ = td_s[1].text.strip()
                                value = ' '.join(value_.split())
                            else:
                                key = 'data'
                                value = td_s[0].text.strip()

                            category_data[key] = value

                    data[current_category] = category_data

                params = {
                    'id': f'{id_}',
                    'notes': '',
                    't': '1694190268107',
                }

                response = requests.get('https://www.chrono24.com/search/detail.htm', params=params, cookies=cookies, headers=headers)

                # Получаем текстовое содержимое ответа
                xml_response = response.text

                # Разбор XML
                root = ET.fromstring(xml_response)

                # Получаем текст из CDATA элемента
                cdata_text = root.text
                if cdata_text is not None:
                    # Заменяем "<br>" на пробелы
                    text_without_br = cdata_text.replace("<br>", " ")
                    # Удаляем лишние пробелы
                    cleaned_text = " ".join(text_without_br.split())

                    data["Description"]["data"] = cleaned_text
                else:
                    pass
                    # data["Description"]["data"] = ''

                try:
                    rev_tag = soup.find('strong', class_='text-xlg text-bold')
                    rev_ = rev_tag.text.strip()  # "(99)"
                except:
                    rev_ = ''

                try:
                    span_tag = soup.find('span', class_='rating')
                    tit_ = span_tag.text.strip()  # "4.4"
                except:
                    tit_ = ''

                merchant_button = soup.find('button', class_='js-link-merchant-name')
                merchant_name = merchant_button.text.strip()

                data["Seller INFO"] = {
                    "Seller": merchant_name,
                    "Seller rating": f'{tit_} {rev_}',
                    "SellerID": id_
                }

                cookies = {
                    '__ssid': '48fcab77fc77e691a2f766df428787c',
                    'FPID': 'FPID2.2.SNMSTPBdw09c%2FOemDe2nY1YKAHe20RIAOmbxmmiUlZw%3D.1694171145',
                    '_gcl_au': '1.1.1505745328.1694171148',
                    '_gid': 'GA1.2.1778751159.1694171148',
                    '_pin_unauth': 'dWlkPU0yRTROalF3TVdFdE16VmtNUzAwWTJObUxUbGxNR1V0TTJGbE56SmhaV0kwTldWaA',
                    'FPLC': 'mTIoupLBIcfCnnmb61qDw7xjgXQ%2F5THEPP%2BJeYCB4N0RvK%2Ffy4KJBybBKJxo9rlWA%2FEGH89e32sHMtMAB0vL7pauV0S7ss0d9fGYAHzZ4BmpzeRRUbpg6S1UQifzQQ%3D%3D',
                    '_hjSessionUser_72519': 'eyJpZCI6IjVmZTU3ZWNjLTBjMzctNWUwMC05ZmM5LTQ0MTVkZTVlNzcxOSIsImNyZWF0ZWQiOjE2OTQxNzExNDg1OTIsImV4aXN0aW5nIjp0cnVlfQ==',
                    '_ga': 'GA1.1.1621830338.1694171145',
                    'cto_bundle': 'BBulvF9GeHZUdE0lMkJlNjlYc3pEZFNIS0ZWYXh3WGFTd1MlMkJTdFhMR2d0TjUzQk9EWTVXSGdSM1d5ak4xbmZmemM3a3F2RWgySkJmbmk3amk3WDZ0N0slMkJnbGdyanhiSkd2YlU3TXp5OHMxSVM0bGQ3a25NNWtpQmRDUXJpcjR6dDBMQVYxaTI0ak43aUJaSkQlMkYwRDN2ckxtcloyUjZtZEhvN3pzcWVYMGU0c0pPeGtmRSUyRjZSSGFNZmhDV2dMM2VRZGFiSENxR21CMElqQnJCbXJBQ2hoWVN0SEZ6dyUzRCUzRA',
                    '_derived_epik': 'dj0yJnU9cW5LaHVlakl1UmtHSGQ1bXoyd0N6S2ViT3VYSzhLc3Ambj0xQlJ2b3N6R3FnNHpjTjV4R25jUWN3Jm09ZiZ0PUFBQUFBR1Q3QVdzJnJtPWYmcnQ9QUFBQUFHVDdBV3Mmc3A9NQ',
                    '_ga_B8CPBTKGPW': 'GS1.1.1694173427.2.0.1694173427.0.0.0',
                }

                headers = {
                    'authority': 'cdn2.chrono24.com',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6,vi;q=0.5,pt;q=0.4,ka;q=0.3',
                    'cache-control': 'max-age=0',
                    'if-modified-since': 'Fri, 09 Jun 2023 17:01:38 GMT',
                    'if-none-match': '"905f5f32cad22055c6ea8e23505c9119"',
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

                headers.update({"If-Modified-Since": "Thu, 01 Jan 1970 00:00:00 GMT"})  # Добавляем новый заголовок

                if download_zoom_images:
                    zoom = True
                    link_dict['zoom'] = []

                    img_zoom_select = "div.js-carousel-zoom-image-container.watch-image-carousel-image.content.image-container.bg-center-center.bg-no-repeat"
                    zoom_image_urls=[img["data-zoom-image"] for img in soup.select(img_zoom_select)]

                    if len(zoom_image_urls)>0:
                        for image_url in zoom_image_urls:
                            img_url = download_img(image_url, directory_name, zoom, cookies, headers, verbose=verbose)
                    #        ur_path = os.path.join(directory_name, "_zoom_")
                            link_dict['zoom'].append(img_url)
                    else:
                        print(f'\n!!! Zoom images are NOT AVAILABLE for id = {id_} !!!\n')

                if download_data_image:
                    zoom = False
                    link_dict['data'] = []

                    img_select1 = 'div.js-carousel-zoom-image-container.watch-image-carousel-image.content.image-container.bg-center-center.bg-no-repeat'
                    image_urls = [img['style'].split("'")[1] for img in soup.select(img_select1)]
                    if len(image_urls)==0:
                        img_select2 = 'div.watch-image-carousel-image.content.image-container.bg-center-center.bg-no-repeat'
                        image_urls = [img['style'].split("'")[1] for img in soup.select(img_select2)]


                    if len(image_urls)>0:
                        for image_url in image_urls:
                   #         img_url = download_img(image_url, directory_name, zoom, cookies, headers, verbose=verbose)
                   #         ur_path = directory_name
                            link_dict['data'].append(img_url)
                    else:
                        print(f'\n!!! Images are NOT AVAILABLE for id = {id_} !!!\n')

                data["IMG"] = link_dict

  #              with open(os.path.join(directory_name, f'info_{id_}.json'), 'w', encoding='utf-8') as json_file:
  #                  json.dump(data, json_file, ensure_ascii=False, indent=4)
                list_dataupd.append(data)
                results[count]=1

            count+=1
        except Exception as err:
            count+=1
  #          logging.error(f'!!!!ERROR!!!!   during processing of {www}\nProcessing next url')
  #          logging.error(str(err))

    return results,list_dataupd


###############
if __name__ == "__main__":
    if UPDATE:
#      urls_list=list(pd.read_csv('/kaggle/input/urls-list/urls_listnew.csv',index_col=0)['0'])
       dtsname_='urls_listnew'
       urls_list=list(crud(dtsname=dtsname_,read=True,jsn=False)['0'])
    else:
       urls_list=[]
    if UPDATE:
 #     with open('/kaggle/input/listings1/listings') as json_file:
 #       listings1=json.load(json_file)
       listings1=crud(dtsname='listings',read=True,jsn=True)
    else:
       listings1=[]  
    download_path = ''
    get_zoom = True     # True or False
    get_standard = False      # True or False
    max_listings = 500
    s=0
 #   with open('/kaggle/input/testmodels0-4/model_links_listings.json') as json_file:
 #     data_dict = json.load(json_file)
    data_dict=crud(dtsname='model_links_listings',read=True,jsn=True)
    for  g in data_dict:
      s=s+1
      print(f'model: {s}')
      links=g['listing_urls']
      refn=g['refnum']
      res = download_images(links,refn,urls_list, download_path, download_zoom_images=get_zoom, download_data_image=get_standard, max_listings=max_listings, verbose=10)[0]
      listings1.extend(download_images(links,refn,urls_list, download_path, download_zoom_images=get_zoom, download_data_image=get_standard, max_listings=max_listings, verbose=10)[1])
      print(res)
  #    logging.debug(res)
    if UPDATE:
       dtsname_="listings"
       dtsin=pd.json_normalize(listings1,max_level=0).drop('_id',axis=1).fillna('Unknown')
       crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)     
    else:
       dtsname_="listings"
       dtsin=pd.json_normalize(listings1,max_level=0).fillna('Unknown')
       crud(dtsname=dtsname_,read=False,jsn=False,dtsin=dtsin)      
#    with open("listings", "w", encoding="utf-8") as file:
#       file.write(json.dumps(listings1, indent=4))