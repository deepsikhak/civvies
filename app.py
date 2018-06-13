from flask import Flask, jsonify, request, json, render_template, flash, redirect, url_for, session,logging
from data import Categories
from flask_mysqldb import MySQL 
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'civvies'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

#Categories = Categories()


@app.route('/', methods=['GET'])
def getHome():
    return render_template('home.html')


@app.route('/whats-new', methods=['GET'])
def whatsnew():
    return render_template('whats-new.html')

@app.route('/categories', methods=['GET'])
def categories():
    cur = mysql.connection.cursor()
    categories= cur.execute("SELECT * FROM categories ")
    categories = cur.fetchall()
    cur.close()
    if len(categories) > 0:
    	return render_template('categories.html', categories = categories)
    else:
    	msg = 'No Items found'
    	return redirect(url_for('add_categories'))

@app.route('/category/<string:id>/', methods=['GET'])
def category(id):
	cur = mysql.connection.cursor()
	categories= cur.execute("SELECT * FROM categories where id = %s", [int(id)])
	categories = cur.fetchone()
	return render_template('category.html', categories = categories)

class RegisterForm(Form):
	name= StringField('Name',[validators.Length(min=1,max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm',message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password')

@app.route('/register', methods = ['GET','POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data 
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)",(name, email, username, password))
		mysql.connection.commit()
		cur.close()
		flash('You are now registered and can log in', 'success')
		return redirect(url_for('login'))
	return render_template('register.html',form = form)	



@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password_candidate = request.form['password']

		cur = mysql.connection.cursor()

		result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

		if result > 0:
			data = cur.fetchone()
			password = data['password']
			print(password_candidate, password)
			if sha256_crypt.verify(password_candidate, password):
				print("Valid User")
				session['logged_in'] = True
				session['username'] = username
				flash('You are now logged in','success')
				return redirect(url_for('dashboard'))
			else:
				error = 'Invalid login'
				print("Invalid User")
				return render_template('login.html',error=error)
			cur.close()
		else:
			error = 'Username not found'
			print("User Name not found")
			return render_template('login.html',error=error)
	return render_template('login.html')

def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login','danger')
			return redirect(url_for('login'))
	return wrap

@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out','success')
	return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():

	cur = mysql.connection.cursor()

	categories= cur.execute("SELECT * FROM categories")

	categories = cur.fetchall()
	cur.close()
	if len(categories) > 0:
		return render_template('dashboard.html', categories = categories)
	else:
		msg = 'No Items found'
		return render_template('dashboard.html', msg = msg)

	

class category_form(Form):
	title= StringField('Title',[validators.Length(min=1,max=200)])
	body = TextAreaField('Username', [validators.Length(min=30)])
	
@app.route('/add_categories', methods=['GET', 'POST'])
@is_logged_in
def add_categories():
	form = category_form(request.form)
	if request.method == 'POST'and form.validate():
		title = form.title.data
		body = form.body.data

		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO categories(title, body, author) VALUES(%s, %s, %s)",(title,body,session['username']))

		mysql.connection.commit()

		cur.close()


		flash('Items Added', 'success')

		return redirect(url_for('dashboard'))

	return render_template('add_categories.html', form = form)


@app.route('/edit_categories/strind:id', methods=['GET', 'POST'])
@is_logged_in
def edit_categories(id):

	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM Categories WHERE id = %s", [id])

	categories = cur.fetchone()

	form = category_form(request.form)

	form.title.data = request.form['title']
	form.title.data = request.form['body']
	if request.method == 'POST'and form.validate():
		title = form.title.data
		body = form.body.data

		cur = mysql.connection.cursor()

		cur.execute("UPDATE  categories  SET title = %s, body = %s WHERE id = %s", (title,body))

		mysql.connection.commit()

		cur.close()


		flash('Items edited', 'success')

		return redirect(url_for('dashboard'))

	return render_template('add_categories.html', form = form)

@app.route('/delete_items/<string:id>',methods = ['POST'])
@is_logged_in
def delete_items(id):

	cur = mysql.connection.cursor()

	cur.execute("DELETE FROM categories WHERE id=%s",[id])

	mysql.connection.commit()

	cur.close()

	flash("Items Deleted",'success')

	return redirect(url_for('dashboard'))



if __name__ == '__main__':
	app.secret_key = 'secret123'
	app.run(host="localhost", debug=True, port=5001)