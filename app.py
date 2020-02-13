__author__ = "christopherdavidson"

from flask import Flask, render_template, request, session, jsonify, make_response
from common.database import Database
from models.meeting import Meeting
from models.admin import Admin
from models.client import Client
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
    #request.args.get('language')  # if key doesn't exist, returns None
    #framework = request.args['framework']  # if key doesn't exist, returns a 400, bad request error

    admin = request.form['admin']
    if request.form['admincode'] is not None:
        admincode = request.form['admincode']
    else:
        admincode = ""


    # make name suitable for db
    fname = request.form['fname']
    lastname = request.form['lastname']
    name = lastname + ', ' + fname

        # get email and password
    email = request.form['email']
    password = request.form['password']

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
        print(admin == "1")
        if admin == "1":
            print(admincode == "11111")
            # default code for admin registration
            if admincode == '11111':
                # add another layer by seeing if 'email' contains @specific_company_name
                if Admin.register(name=name, email=email, password=password, usertype='admin', userinfo=acode) is False:
                    return render_template('duplicate_user.html', error='Email Already Registered as User')
                else:
                    Admin.register(name=name, email=email, password=password, usertype='admin', userinfo=acode)
                    meetings = []
                    return render_template('admin_profile.html', email=email, name=name, meetings=meetings)
        else:
            if Client.register(name=name, email=email, password=password, usertype='client', userinfo=cardinfo) is False:
                return render_template('duplicate_user.html', error='Email Already Registered as User')
            else:
                Client.register(name=name, email=email, password=password, usertype='client', userinfo=cardinfo)
                meetings = []
                return render_template('client_profile.html', email=email, name=name, meetings=meetings)
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
                #meetings = Meeting.get_by_email(email)
                #print(user.userinfo[0]) prints '1' for the first digit in 11111
                if user.usertype == 'admin':
                    # send user to profile page...also can send any information needed including user email
                    return make_response(back_to_profile())
                    #return render_template('admin_profile.html', email=session['email'], name=user.name, user=user, meetings=meetings)
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
            #meetings = Meeting.get_by_email(email)
            #print(user.usertype)
            if user.usertype == 'client':
                return make_response(back_to_profile())
                #return render_template('client_profile.html', email=session['email'], name=user.name, user=user, meetings=meetings)
    return render_template('login_error.html', error='NOT ALLOWED!')

                
            
####### BACK TO MENU LINK METHODS #########
# link to profile... user must be logged in
@app.route('/back_to_profile')
def back_to_profile():
    if session['email'] is not None:
        user = User.get_by_email(session['email'])
        if Meeting.get_by_email(session['email']) is not None:
            meetings = Meeting.get_by_email(session['email'])
        else:
            meetings = []
        if user.check_if_client():
            return render_template('client_profile.html', email=session['email'], name=user.name, meetings=meetings)
        elif user.check_if_admin():
            return render_template('admin_profile.html', email=session['email'], name=user.name, meetings=meetings)
        else:
            print("error")
    return render_template('login_error.html', error='Invalid Request')



########### CREATE MEETING METHODS
@app.route('/auth/newmeeting', methods=['POST', 'GET'])
def new_meeting():
    return render_template('create_meeting.html')

# /<string:workout_id>
@app.route('/meeting/createnew', methods=['POST', 'GET'])
def create_meeting():

    if request.method == 'POST':
        email = session['email']
        
        day = request.form['day']
        time = request.form['time']
        p1 = request.form['p1']
        p2 = request.form['p2']
        p3 = request.form['p3']
        p4 = request.form['p4']
        p5 = request.form['p5']
        p6 = request.form['p6']
        p7 = request.form['p7']
        p8 = request.form['p8']
        p9 = request.form['p9']
        p10 = request.form['p10']


        member_emails = {
            'p1': p1,
            'p2': p2,
            'p3': p3,
            'p4': p4,
            'p5': p5,
            'p6': p6,
            'p7': p7,
            'p8': p8,
            'p9': p9,
            'p10': p10
        }
        meeting = Meeting(day=day, time=time, email=email, members=member_emails)
        if meeting.isAvailable(day, time):
            meeting.save_to_mongo()
            return make_response( back_to_profile() )
        else:
            return make_response( back_to_profile() )
    return render_template('login_error.html', error="Meeting Log Error")

@app.route('/delete_one/<string:meeting_id>')
def delete_one(meeting_id):
    meeting = Meeting.from_mongo(meeting_id)
    meeting.delete_meeting(meeting_id)
    return make_response(back_to_profile())


      ########## App Run() METHOD #############

if __name__ == '__main__':
    app.run(debug=True)

