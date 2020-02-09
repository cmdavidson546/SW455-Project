__author__ = "christopherdavidson"

from flask import Flask, render_template, request, session, jsonify
from common.database import Database
from models.user import User
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# initialize db
@app.before_first_request
def initialize_database():
    Database.initialize()

# set home endpoint
@app.route('/')
def open_app():
    return render_template('user_type.html')

                    ####### INITIAL STARTUP, LOGIN, LOGOFF, REGISTER METHODS #########
@app.route('/auth/user_type', methods=['POST', 'GET'])
def log_in_by_user_type():
    account = request.form['account']
    if account == "0":
        return render_template('login_admin.html')
    if account == "1":
        return render_template('login_client.html')
    if account == "2":
        return render_template('register.html')
    return render_template('user_type.html')

# set route path to login
@app.route('/login')
def user_home():
    return render_template('user_type.html')

# path to logout - NEED TO SEE IF "User.logout()" is buggy for Admin and Client users
@app.route('/auth/logout')
def user_logout():
    User.logout()
    return render_template('user_type.html')

# route to register page
@app.route('/register')
def register_page():
    return render_template('register.html')

    ########### REGISTER NEW USER METHOD ############
    # endpoint from main registration form  -> client_profile.html
@app.route('/auth/register', methods=['POST', 'GET'])
def register_user():
        # get admin form data

    admin = request.form['admin']
    admincode = request.form['admincode']

        # make name suitable for db
    fname = request.form['fname']
    lastname = request.form['lastname']
    name = lastname + ', ' + fname

        # get email and password
    email = request.form['email']
    password = request.form['password']

    # create userinfo dictionaries for User.object 
    cardinfo = {
        'cardname': request.form['cardname'],
        'cardnumber': request.form['cardnumber'],
        'cardcode': request.form['cardcode'],
        'zipcode': request.form['zipcode']
    }
    acode = {
        'admincode': admincode
    }
    
    if request.method == 'POST':
        if admin == "1":
            # default code for admin registration
            if admincode == '11111':
                # add another layer by seeing if 'email' contains @specific_company_name
                Admin.register(name=name, email=email, password=password, usertype='admin', userinfo=acode)
                return render_template('admin_profile.html', email=email, name=name)
        else:
            Client.register(name=name, email=email, password=password, usertype="client", userinfo=cardinfo)
            return render_template('client_profile.html', email=email, name=name)
    return render_template('registration_error.html', error='Invalid registration')

        ####### LOGIN EXISTING USER METHODS #########
# create session for logged in user -> admin_profile.html
@app.route('/admin/login', methods=['POST', 'GET'])
def admin_login():
    # get email and password : IN OTHER ITERATIONS WE CAN GET POST from hidden ajax login form
    email = request.form['email']
    password = request.form['password']
    admincode = request.form['admincode']

    # if POST used properly passed through Ajax created form in process_login.js .done() function
    if request.method == 'POST':
        # if login_valid method in user.py class returns TRUE
        if Admin.login_valid(email=email, password=password):
            # check on admincode code verification HERE
            if admincode == '11111':
            # start session in user.py class
                Admin.login(email)
            # return name data from user profile
                user = Admin.get_by_email(email)
                #print(user.userinfo[0]) prints '1' for the first digit in 11111
                if user.usertype == 'admin':
            # send user to profile page...also can send any information needed including user email
                    return render_template('admin_profile.html', email=session['email'], name=user.name)
    return render_template('login_error.html', error='NOT ALLOWED!')

# create session for logged in user -> client_profile.html
@app.route('/client/login', methods=['POST', 'GET'])
def client_login():
    # get email and password : IN OTHER ITERATIONS WE CAN GET POST from hidden ajax login form
    email = request.form['email']
    password = request.form['password']

    if request.method == 'POST':
            # if login_valid method in user.py class returns TRUE
        if Client.login_valid(email=email, password=password):
            Client.login(email)
            user = Client.get_by_email(email)
            #print(user.usertype)
            if user.usertype == 'client':
                return render_template('client_profile.html', email=session['email'], name=user.name)
    return render_template('login_error.html', error='NOT ALLOWED!')

                
            ####### BACK TO MENU LINK METHODS #########
# link to profile... user must be logged in
@app.route('/back_to_profile')
def back_to_profile():
    if session['email'] is not None:
        user = User.get_by_email(session['email'])
        if user.check_if_client():
            return render_template('client_profile.html', email=session['email'], name=user.name)
        elif user.check_if_admin():
            return render_template('admin_profile.html', email=session['email'], name=user.name)
        else:
            print("error")
    return render_template('login_error.html')

      ########## App Run() METHOD #############

if __name__ == '__main__':
    app.run(debug=True)

