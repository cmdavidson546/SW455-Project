__author__ = "christopherdavidson"

from flask import Flask, render_template, request, session
from src.common.database import Database
from src.models.user import User
import os

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


@app.route('/auth/login', methods=['POST', 'GET'])
def user_login():
    # get email from login page
    email = request.form['email']
    # set error flag to none
    error = None
    # if POST used properly passed through endpoint
    if request.method == 'POST':
        # if login_valid method in user.py class returns TRUE
        if User.login_valid(request.form['email'],request.form['password']):
            # start session in user.py class
            User.login(email)
            # return name data from user profile
            user = User.get_by_email(email)
            # send user to profile page...also can send any information needed including user email
            # by sending the session email we can then look up in db for all the other info
            return render_template('profile.html', email=session['email'], name=user.name)
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login_error.html', error=error)


@app.route('/auth/register', methods=['POST', 'GET'])
def register_user():
    # Get from Form: name, email, password, height, weight, country
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    # sanitize
    error = None
    if request.method == 'POST':
        User.register(name, email, password)
        return render_template('profile.html', email=email, name=name)
    else:
        error = 'Invalid registration'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('registration_error.html', error=error)


if __name__ == '__main__':
    app.run(port=4995, debug=True)

