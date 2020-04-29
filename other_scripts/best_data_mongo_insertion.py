import pandas as pd
from pymongo import MongoClient
from random import randint   
import time

client = MongoClient('localhost', 27017)
mydatabase = client.generic_ecommerce_website
mycollection = mydatabase.products
df = pd.read_csv("C:\\Users\\aravi\\adbms_midhilesh\\Generic-Ecommerce-site\\data\\Product_info.csv",encoding= 'unicode_escape')
links = pd.read_csv("C:\\Users\\aravi\\Generic-Ecommerce-site\\other_scripts\\output.csv",encoding= 'unicode_escape')

for i in range(len(df)):
    d = dict()
    d['productId'] = int(df.iloc[i][13])
    d['productName'] = df.iloc[i][1]
    d['manufacturer'] = df.iloc[i][2]
    d['price'] = float(df.iloc[i][11])
    d['description'] = df.iloc[i][7]
    d['ratings'] = dict()
    if(not eval(links.iloc[i][1])):
        d['images'] = []
    else:
        d['images'] = eval(links.iloc[i][1])
    #d['images'] = fetch_image_urls(d['productName'],1,wd)
    #d['images'] = []
    d['tags'] = df.iloc[i][9]
    try:
        d['numOfItemsAvailable'] = int(df.iloc[i][12])+100
    except:
        d['numOfItemsAvailable'] = 100
    #mycollection.insert_one(d)