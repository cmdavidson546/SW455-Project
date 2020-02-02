__author__ = "christopherdavidson"

from flask import Flask, render_template, request, session
from common.database import Database
from models.user import User
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

@app.before_first_request
def initialize_database():
    Database.initialize()

@app.route('/')
def open_app():
    return render_template('login.html')

@app.route('/login')
def user_home():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/back_to_profile')
def back_to_profile():
    if session['email'] is not None:
        user = User.get_by_email(session['email'])
        return render_template('profile.html', email=session['email'], name=user.name)
    return render_template('login.html')

@app.route('/auth/logout')
def user_logout():
    #[session.pop(key) for key in list(session.keys()) if key != '_flashes']
    User.logout()
    return render_template('login.html')

# create endpoint '/process_form
@app.route('/process_login', methods=['POST'])
def process():
    email = request.form['email']
    password = request.form['password']
    if password and email:
        if User.login_valid(email=email, password=password):
            return jsonify({'email': email, 'password': password})
        else:
            return jsonify({'error': 'Email or Password Entry Invalid!'})
    return jsonify({'error' : 'Missing data in form!'})

@app.route('/auth/login', methods=['POST', 'GET'])
def user_login():
    # get email and password from hidden ajax login form
    email = request.form['email']
    password = request.form['password']

    # if POST used properly passed through Ajax hidden form
    if request.method == 'POST':
        # if login_valid method in user.py class returns TRUE
        if User.login_valid(email=email, password=password):
            # start session in user.py class
            User.login(email)
            # return name data from user profile
            user = User.get_by_email(email)
            # send user to profile page...also can send any information needed including user email
            # by sending the session email we can then look up in db for all the other info
            return render_template('profile.html', email=session['email'], name=user.name)
    return render_template('login_error.html', error='GET POST NOT ALLOWED!')


# create endpoint '/process_form
@app.route('/process_register', methods=['POST'])
def processRegister():

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    if name and password and email:
    #if email and password:
        # this one is too restrictive...does not allow regular emails...
        #if re.match("/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2, 3})+$/", email) != None:

        # This one works so/so...most bad emails are still allowed
        # However, it covers...emails Not allowed:
        # @you.me.net [ No character before @ ]
        # mysite.ourearth.com [@ is not present]
        if re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email) != None:
            return jsonify( { 'name': name, 'email': email, 'password': password } )
        else:
            return jsonify({'error': 'Email Invalid!'})
    return jsonify({'error' : 'Missing data in form!'})

@app.route('/auth/register', methods=['POST', 'GET'])
def register_user():
    # Get from hidden Ajax form: name, email, password
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    if request.method == 'POST':
        User.register(name, email, password)
        return render_template('profile.html', email=email, name=name)
    return render_template('registration_error.html', error='Invalid registration')


if __name__ == '__main__':
    app.run(debug=True)

