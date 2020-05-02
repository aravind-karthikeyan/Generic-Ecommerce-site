import pandas as pd
from pymongo import MongoClient
from random import randint   
import time
import bcrypt

client = MongoClient('localhost', 27017)
mydatabase = client.generic_ecommerce_website
products = mydatabase.products
users = mydatabase.users
df = pd.read_csv("C:\\Users\\aravi\\adbms_midhilesh\\Generic-Ecommerce-site\\data\\User_info.csv",encoding= 'unicode_escape')
hashpass = bcrypt.hashpw("1234".encode('utf-8'), bcrypt.gensalt())
for i in range(len(df)):
    d = dict()
    d['username'] = df.iloc[i][0]
    d['password'] = hashpass
    d['cart'] = []
    d['address'] = ""
    d['mobile'] = ""
    p_list = []
    purchased = df.iloc[i][2].split('|')
    for i in purchased:
        product = products.find_one({'productName':i})
        if(product):
            p_list.append(product['productId'])
    d['purchased'] = p_list
    d['ratings'] = {}
    users.insert_one(d)