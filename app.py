from flask import Flask, render_template,request,redirect,url_for,session # For flask implementation
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import os
import bcrypt
from collections import Counter

app = Flask(__name__)
app.secret_key = 'mysecret'

#client = MongoClient('mongodb+srv://cluster0-8cf7c.gcp.mongodb.net/test',username='aravindk',password='aravindk')
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.generic_ecommerce_website
products = db.products
users = db.users
admins = db.admins

@app.route('/')
def index():
	if 'username' in session:
		return redirect(url_for('viewProducts'))
	if 'manufacturerName' in session:
		return redirect(url_for('adminIndex'))
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
		existing_admin = admins.find_one({'username' : request.form['username']})
		if existing_user is None and existing_admin is None:
			hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
			users.insert_one({'username' : request.form['username'], 'password' : hashpass, 'cart' : [], 'address': "", 'mobile': "", 'purchased':[], 'rating':{}})
			session['username'] = request.form['username']
			return redirect(url_for('index'))
		return 'That username already exists!'
	return render_template('register.html')

@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username')
	if 'manufacturerName' in session:
		session.pop('manufacturerName')
	return redirect(url_for('index'))

@app.route("/products")
def viewProducts ():
	#Display the Products
	if 'username' in session:
		return render_template("products.html",products = products.find(), user = users.find_one({"username" : session["username"]}))
	return redirect(url_for('index'))

@app.route("/search_products", methods = ['POST', 'GET'])
def searchProducts ():
	#Display the searched Products
	if 'username' in session:
		query = request.form['query']
		return render_template("products.html",products = products.find({"$or": [{"productName":{"$regex":query, \
															"$options": '-i'}},{"tags":{"$regex":query, "$options": '-i'}}]})\
															, user = users.find_one({"username" : session["username"]}))
	return redirect(url_for('index'))

@app.route("/products/<int:productId>")
def viewIndividualProduct (productId):
	#Display the individual product
	if 'username' in session:
		user = users.find_one({"username" : session["username"]})
		rating  = 0
		try:
			rating = user['rating'][str(productId)]
		except:
			rating = "Not rated"
		return render_template('individual_product.html', product = products.find_one({"productId" : productId}), user = user,rating = rating)
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

@app.route("/add_one/<int:productId>")
def addOneToCart (productId):
	#add item to cart
	if 'username' in session:
		username = session["username"]
		user = db.users.find_one({"username": username})
		user['cart'].append(productId)
		db.users.update_one({"username": username}, {"$set": {"cart": user['cart']}})
		user = db.users.find_one({"username": username})
		return redirect(url_for('viewCart'))
	return redirect(url_for('index'))

@app.route("/remove/<int:productId>")
def removeFromCart (productId):
	#remove item from cart
	if 'username' in session:
		username = session["username"]
		user = db.users.find_one({"username": username})
		user['cart'] = list(filter(lambda a: a != productId, user['cart']))
		db.users.update_one({"username": username}, {"$set": {"cart": user['cart']}})
		return redirect(url_for('viewCart'))
	return redirect(url_for('index'))

@app.route("/remove_one/<int:productId>")
def removeOneFromCart (productId):
	#remove an item from cart
	if 'username' in session:
		username = session["username"]
		user = db.users.find_one({"username": username})
		print(user)
		user['cart'].remove(productId)
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
		total = 0
		for i in product:
			productsMap[i["productId"]] = [i["productName"] ,i["price"]]
			total+=productsMap[i["productId"]][1]*cart[i["productId"]]
		return render_template("cart.html",user = user, cart = cart, products = productsMap, total = total)
	return redirect(url_for('index'))

@app.route("/buy/<int:productId>")
def buyNow (productId):
	#buy a product
	return addOneToCart(productId)

@app.route("/place_order")
def placeOrder ():
	#place order
	if 'username' in session:
		username = session["username"]
		user = db.users.find_one({"username": username})
		cart = dict(Counter(user["cart"]))
		product = products.find({"productId" : { "$in" : list(cart.keys())} })
		flag = 1
		for i in product:
			if(i['numOfItemsAvailable']-cart[i['productId']]<0):
				flag = 0
				break
		if(flag==0):
			return "Order can't be placed"
		else:
			product = products.find({"productId" : { "$in" : list(cart.keys())} })
			for i in product:
				purchased = db.users.find_one({"username": username})["purchased"]
				db.users.update_one({"username": username}, {"$set": {"purchased": purchased+[i['productId']]*cart[i['productId']]}})
				db.products.update_one({"productId": i['productId']}, {"$set": {"numOfItemsAvailable": i['numOfItemsAvailable']-cart[i['productId']]}})
			return redirect(url_for('clearCart'))	
	return redirect(url_for('index'))

@app.route("/clear_cart")
def clearCart ():
	#clear cart
	if 'username' in session:
		username = session["username"]
		db.users.update_one({"username": username}, {"$set": {"cart": []}})
		return render_template("success.html")
	return redirect(url_for('index'))

@app.route("/my_orders")
def viewOrders ():
	#view orders by a user
	if 'username' in session:
		username = session["username"]
		user = db.users.find_one({"username": username})
		orders = dict(Counter(user["purchased"]))
		product = products.find({"productId" : { "$in" : list(orders.keys())} })
		productsMap = dict()
		for i in product:
			productsMap[i["productId"]] = [i["productName"] ,i["price"]]
		return render_template("orders.html",user = user, orders = orders, products = productsMap)
	return redirect(url_for('index'))

@app.route("/rating/<int:productId>", methods = ["POST", "GET"])
def rating(productId):
	if 'username' in session:
		username = session["username"]
		user = db.users.find_one({"username": username})
		if productId in user["purchased"]:
			try:
				user['rating'][str(productId)] = request.form['star']
				db.users.update_one({"username": username}, {"$set": {"rating": int(user['rating'])}})
				db.products.update_one({"productId": productId}, { "$set" : {"ratings."+username : request.form['star'] }})
				return redirect(url_for('viewIndividualProduct',productId=productId,rating = int(request.form['star'])))			
			except:
				db.users.update_one({"username": username}, {"$set": {"rating": {str(productId): int(request.form['star'])}}})
				db.products.update_one({"productId": productId}, { "$set" : {"ratings."+username : request.form['star'] }})
				return redirect(url_for('viewIndividualProduct',productId=productId))
		return 'You must buy product to rate it'
	return url_for('index')

@app.route('/admin')
def adminIndex():
	if 'manufacturerName' in session:
		return render_template("admin_products.html",products = products.find({'manufacturer': session['manufacturerName']}), user = admins.find_one({"username" : session['manufacturerName']}))
	if 'username' in session:
		return "You have no rights to access that page!"
	return render_template('admin_login.html')

@app.route("/admin_login", methods=['POST','GET'])
def adminLogin():
	if request.method == 'POST':
		login_user = admins.find_one({'username' : request.form['username']})
		if login_user:
			if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
				session['manufacturerName'] = request.form['username']
				return redirect(url_for('adminIndex'))
		return 'Invalid username/password combination'
	return redirect(url_for('adminIndex'))
@app.route('/admin_signup', methods=['POST', 'GET'])
def adminSignup():
	if request.method == 'POST':
		admins = db.admins
		existing_admin = admins.find_one({'username' : request.form['username']})
		existing_user = users.find_one({'username' : request.form['username']})
		if existing_admin is None and existing_user is None:
			hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
			admins.insert_one({'username' : request.form['username'], 'password' : hashpass, 'products' : [], 'address': "", 'mobile': ""})
			session['manufacturerName'] = request.form['username']
			return redirect(url_for('adminIndex'))
		return 'That Manufacturer name already exists!'
	return render_template('admin_signup.html')

@app.route('/edit_product/<int:productId>', methods=['GET','POST'])
def editProduct(productId):
	if 'manufacturerName' in session:
		username = session["manufacturerName"]
		product = products.find_one({"productId" : productId},{"_id":0,"ratings":0})
		if(product["manufacturer"] == username):
			return render_template("edit_product.html",product = product)
		return "You have no permission to edit that product!"
	if 'username' in session:
		return "You are not permitted to access that page"
	return redirect(url_for('adminIndex'))
 
@app.route('/submit_edit/<int:productId>', methods=['GET','POST'])
def submitEdit(productId):
	if 'manufacturerName' in session:
		username = session["manufacturerName"]
		product = products.find_one({"productId" : productId},{"_id":0,"ratings":0})
		link = str(request.form['images'])
		links = []
		links.append(link)
		if(product["manufacturer"] == username):
			db.products.update_one({"productId": productId}, {"$set": { \
				"productName" : request.form['productName'], \
				"price" : float(request.form['price']), \
				"description" : request.form['description'], \
				"images" : links,\
				"tags" : request.form['tags'],\
				"numOfItemsAvailable" : int(request.form['numOfItemsAvailable'])
				}})
			return redirect(url_for('editSuccess'))
		else:
			return "You have no permission to edit that product!"
	if 'username' in session:
		return "You are not permitted to access that page"
	return redirect(url_for('adminIndex'))

@app.route('/add_product_success', methods=['GET','POST'])
def addProductSuccess():
	if 'manufacturerName' in session:
		username = session["manufacturerName"]
		productId = products.find({}, {"productId": 1, "_id":0}).sort([("productId",-1)]).limit(1)
		pid = 0
		for i in productId:
			pid = i["productId"]
		productId = pid+1
		link = str(request.form['images'])
		links = []
		links.append(link)
		user = db.admins.find_one({"username": username})
		user['products'].append(productId)
		db.admins.update_one({"username": username}, {"$set": {"products": user["products"]}})
		db.products.insert_one( { \
		"productId" : productId, \
		"manufacturer" : username, \
		"productName" : request.form['productName'], \
		"price" : float(request.form['price']), \
		"description" : request.form['description'], \
		"images" : links,\
		"tags" : request.form['tags'],\
		"numOfItemsAvailable" : int(request.form['numOfItemsAvailable'])
		})
		return redirect(url_for('editSuccess'))
	else:
		return redirect(url_for('adminIndex'))

@app.route('/add_product', methods=['GET','POST'])
def addProduct():
	if 'manufacturerName' in session:
		return render_template("add_product.html")
	if 'username' in session:
		return "You are not permitted to access that page"
	return redirect(url_for('adminIndex'))

@app.route('/product_edit_success')
def editSuccess():
	return render_template('product_edit_success.html')

@app.route('/my_customers/<int:productId>')
def myCustomers(productId):
	order = users.find({"purchased": {"$in": [productId]}})
	orders = dict()
	for i in order:
		orders[i["username"]] = i["purchased"].count(productId)
	return render_template('my_customers.html',orders = orders)

if __name__ == "__main__":
	app.debug = True
	app.run()
