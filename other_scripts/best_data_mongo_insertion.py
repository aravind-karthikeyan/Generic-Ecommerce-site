import pandas as pd
from pymongo import MongoClient
from random import randint   
from collections import *
from selenium import webdriver
import time
#wd = webdriver.Chrome(executable_path="C:\\Users\\aravi\\Downloads\\Compressed\\chromedriver_win32_1\\chromedriver.exe")
#wd.get('https://google.com')
#search_box = wd.find_element_by_css_selector('input.gLFyf')
#search_box.send_keys('Dogs')
def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return list(image_urls)

client = MongoClient('localhost', 27017)
mydatabase = client.generic_ecommerce_website
mycollection = mydatabase.products
df = pd.read_csv("C:\\Users\\aravi\\Downloads\\Best_Product_Data.csv")
#dd = defaultdict(lambda: 0)
for i in range(len(df)):
	d = dict()
	d['productId'] = int(df.iloc[i][0])
	d['productName'] = df.iloc[i][1]
	d['price'] = float(df.iloc[i][11])
	d['description'] = df.iloc[i][7]
	d['ratings'] = dict()
	#d['images'] = fetch_image_urls(d['productName'],1,wd)
	d['images'] = []
	d['tags'] = df.iloc[i][9]
	try:
		d['numOfItemsAvailable'] = int(df.iloc[i][12])
	except:
		d['numOfItemsAvailable'] = 0
	mycollection.insert_one(d)
	#print(d)
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
