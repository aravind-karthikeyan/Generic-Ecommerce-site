import pandas as pd
from pymongo import MongoClient   
client = MongoClient('localhost', 27017)
mydatabase = client.generic_ecommerce_website
mycollection = mydatabase.products
df = pd.read_csv("C:\\Users\\aravi\\Downloads\\nike_2020_04_13.csv")

for i in range(631):
	d = dict()
	d['productId'] = df.iloc[i]["Product ID"]
	d['productName'] = df.iloc[i][1]
	d['price'] = float(df.iloc[i][4])
	d['description'] = df.iloc[i][7]
	d['ratings'] = dict()
	try:
		d['images'] = eval(df.iloc[i][10])
	except:
		d['images'] = []
	mycollection.insert_one(d)
	print(d)
#mydatabase.students.insert_one(rec) 
#cursor = mycollection.find()
#for record in cursor: 
#    print(record) 
"""
d['productId'] = record[2]
d['name'] = record[1]
d['price'] = record[4]
d['description'] = record[7]
d['ratings'] = {}
d['images'] = record[10]
"""