from flask import Flask, render_template,request,redirect,url_for,session # For flask implementation
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import os
import bcrypt
from flask_login import logout_user

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
        return render_template("products.html",products = products.find())

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
			users.insert({'username' : request.form['username'], 'password' : hashpass})
			session['username'] = request.form['username']
			return redirect(url_for('index'))
		return 'That username already exists!'
	return render_template('register.html')

@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username')
	return render_template('index.html')

def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('index')

@app.route("/products")
def viewProducts ():
	#Display the Products
	if 'username' in session:
		return render_template("products.html",products = products.find())
	return render_template('index.html')

@app.route("/products/<int:productId>")
def viewIndividualProduct (productId):
	#Display the Products
	if 'username' in session:
		return render_template('individual_product.html', product = products.find_one({"productId" : productId}))
	return render_template('index.html')
if __name__ == "__main__":
	app.secret_key = 'mysecret'
	app.run()
