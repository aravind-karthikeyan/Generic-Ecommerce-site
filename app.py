from flask import Flask, render_template,request,redirect,url_for,session # For flask implementation
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import os
import bcrypt
from collections import Counter

app = Flask(__name__)
title = "TODO sample application with Flask and MongoDB"
heading = "TODO Reminder with Flask and MongoDB"

client = MongoClient("mongodb://127.0.0.1:27017") #host uri
db = client.generic_ecommerce_website
products = db.products
users = db.users

@app.route('/')
def index():
    if 'username' in session:
        return render_template("products.html",products = products.find(), user = users.find_one({"username" : session["username"]}))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
	login_user = users.find_one({'username' : request.form['username']})
	if login_user:
		if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
			session['username'] = request.form['username']
			return redirect(url_for('index'))
	return 'Invalid username/password combination'

@app.route('/register', methods=['POST', 'GET'])
def register():
	if request.method == 'POST':
		users = db.users
		existing_user = users.find_one({'username' : request.form['username']})
		if existing_user is None:
			hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
			users.insert_one({'username' : request.form['username'], 'password' : hashpass, 'cart' : [], 'address': "", 'mobile': "", 'purchased':[]})
			session['username'] = request.form['username']
			return redirect(url_for('index'))
		return 'That username already exists!'
	return render_template('register.html')

@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username')
	return redirect(url_for('index'))

def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('index')

@app.route("/products")
def viewProducts ():
	#Display the Products
	if 'username' in session:
		return render_template("products.html",products = products.find(), user = users.find_one({"username" : session["username"]}))
	return redirect(url_for('index'))

@app.route("/products/<int:productId>")
def viewIndividualProduct (productId):
	#Display the individual product
	if 'username' in session:
		return render_template('individual_product.html', product = products.find_one({"productId" : productId}), user = users.find_one({"username" : session["username"]}))
	return redirect(url_for('index'))
@app.route("/cart/<int:productId>")
def addToCart (productId):
	#add item to cart
	if 'username' in session:
		username = session["username"]
		user = db.users.find_one({"username": username})
		user['cart'].append(productId)
		db.users.update_one({"username": username}, {"$set": {"cart": user['cart']}})
		user = db.users.find_one({"username": username})
		return redirect(url_for('index'))
	return redirect(url_for('index'))
@app.route("/remove/<int:productId>")
def removeFromCart (productId):
	#add item to cart
	if 'username' in session:
		username = session["username"]
		user = db.users.find_one({"username": username})
		user['cart'] = list(filter(lambda a: a != productId, user['cart']))
		db.users.update_one({"username": username}, {"$set": {"cart": user['cart']}})
		return redirect(url_for('viewCart'))
	return redirect(url_for('index'))
@app.route("/view_cart")
def viewCart ():
	#view cart
	if 'username' in session:
		username = session["username"]
		user = db.users.find_one({"username": username})
		cart = dict(Counter(user["cart"]))
		product = products.find({"productId" : { "$in" : list(cart.keys())} })
		productsMap = dict()
		for i in product:
			productsMap[i["productId"]] = [i["productName"] ,i["price"]]
		return render_template("cart.html",user = user, cart = cart, products = productsMap)
	return redirect(url_for('index'))
if __name__ == "__main__":
	app.secret_key = 'mysecret'
	app.run()
