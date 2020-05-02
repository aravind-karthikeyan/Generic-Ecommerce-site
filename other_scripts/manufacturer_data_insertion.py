import pandas as pd
from pymongo import MongoClient
from random import randint   
import time
import bcrypt

client = MongoClient('localhost', 27017)
mydatabase = client.generic_ecommerce_website
products = mydatabase.products
users = mydatabase.admins
df = pd.read_csv("C:\\Users\\aravi\\adbms_midhilesh\\Generic-Ecommerce-site\\data\\manufacturer.csv",encoding= 'unicode_escape')
hashpass = bcrypt.hashpw("1234".encode('utf-8'), bcrypt.gensalt())
for i in range(len(df)):
    d = dict()
    d['username'] = df.iloc[i][0]
    d['password'] = hashpass
    product = products.find({"manufacturer": d['username']})
    p_list = []
    for i in product:
        p_list.append(i['productId'])
    d['products'] = p_list
    d['address'] = ""
    d['mobile'] = ""
    user = users.find_one({"username": d['username']})
    if(user):
        print(0)
    else:
        print(1)
        users.insert_one(d)