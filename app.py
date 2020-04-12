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


########### REGISTER NEW USER ############
# endpoint from main registration form  -> client_profile.html
@app.route('/auth/register', methods=['POST', 'GET'])
def register_user():
    # get admin form data
    # request.args.get('language')  # if key doesn't exist, returns None
    # framework = request.args['framework']  # if key doesn't exist, returns a 400, bad request error

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
        if admin == "1":
            # default code for admin registration
            if admincode == '11111':
                # add another layer by seeing if 'email' contains @specific_company_name
                if Admin.register(name=name, email=email, password=password, usertype='admin', userinfo=acode) is False:
                    return render_template('duplicate_user.html', error='Admin Email Already Registered as User')
                else:
                    Admin.register(name=name, email=email, password=password, usertype='admin', userinfo=acode)
                    meetings = []
                    return render_template('admin_profile.html', email=email, name=name, meetings=meetings)
        else:
            if Client.register(name=name, email=email, password=password, usertype='client',
                               userinfo=cardinfo) is False:
                return render_template('duplicate_user.html', error='Client Email Already Registered as User')
            else:
                Client.register(name=name, email=email, password=password, usertype='client', userinfo=cardinfo)
                meetings = []
                return render_template('client_profile.html', email=email, name=name, meetings=meetings)
    return render_template('registration_error.html', error='Invalid registration')


####### ADMIN LOGIN #########
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
                # start session in admin.py class
                Admin.login(email)
                return render_template('admin_profile.html', email=session['email'])
    return render_template('login_error.html', error='The email or password credentials do not match.')


########### CLIENT LOGIN #############
# create session for logged in user -> client_profile.html
@app.route('/client/login', methods=['POST', 'GET'])
def client_login():
    # get email and password : IN OTHER ITERATIONS WE CAN GET POST from hidden ajax login form
    email = request.form['email']
    password = request.form['password']
    if request.method == 'POST':
        if Client.login_valid(email=email, password=password):
            Client.login(email)
            return render_template('client_profile.html', email=session['email'])
    return render_template('login_error.html', error='The email or password credentials do not match.')


####### FORGOT PASSWORD DIRECTION #########
# link to profile... user must be logged in
@app.route('/pages-forgot-password')
def forgot_password():
    return render_template('pages-forgot-password.html')


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
            return render_template('login_error.html', error='Invalid Request')
    return render_template('login_error.html', error='Invalid Request')


########### CREATE MEETING METHODS ###########
@app.route('/auth/newmeeting', methods=['POST', 'GET'])
def new_meeting():
    return render_template('create_meeting.html')


# CHECK IF ID IS PASSED, may need to add:  /<string:workout_id>
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
            return make_response(back_to_profile())
    return render_template('create_meeting_error.html', error="Meeting Log Error", email=session['email'])

########## Delete Meeting  #############
@app.route('/delete_one/<string:meeting_id>')
def delete_one(meeting_id):
    meeting = Meeting.from_mongo(meeting_id)
    meeting.delete_meeting(meeting_id)
    return make_response(back_to_profile())


########## Display Meetings #############
@app.route('/meetings-participation')
def get_meetings():
    if session['email'] is not None:
        user = User.get_by_email(session['email'])
        if Meeting.get_by_email(session['email']) is not None:
            meetings = Meeting.get_by_email(session['email'])
        else:
            meetings = []
        return render_template('meetings-participation.html', email=session['email'], name=user.name, meetings=meetings)
    return make_response(back_to_profile())


#################### EDIT MEETING  ####################################
# NEED TO MAKE SURE that I bring in the meeting_id in POST request here...
#####################################################################
@app.route('/edit_one/<string:meeting_id>')
def goto_edit_meeting(meeting_id):
    meeting = Meeting.from_mongo(meeting_id)
    return render_template('edit_meeting.html', meeting=meeting)

@app.route('/edit_meeting/<string:meeting_id>', methods=['POST'])
def edit_meeting(meeting_id):
    user = User.get_by_email(session['email'])
    if request.method == 'POST' and user is not None:
        # get meeting from DB
        meeting = Meeting.from_mongo(meeting_id)

        # get Updated Data from user
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

        members = {
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
        if meeting.isAvailable(day, time):
            if day != meeting.day:
                meeting.update_meeting(meeting_id, 'day', day)
            if time != meeting.time:
                meeting.update_meeting(meeting_id, 'time', time)

        # Next Compare dictionaries of user changes vs. original db
        items_to_update = dict_compare(meeting.members, members)
        if items_to_update is not None:
            # meeting.update_meeting(meeting_id, key, items_to_update[key])
            k = items_to_update.keys()
            for key in k:
                # items[key] returns a tuple: ('OLD VALUE', 'NEW VALUE') so we need the second element
                v = items_to_update[key][1]
                meeting.update_members(meeting_id, key, v)

            # GETS MEETINGS ".get_by_email() method"
        meetings = Meeting.get_by_email(session['email'])
        return render_template('meetings-participation.html', email=session['email'], name=user.name, meetings=meetings)
    return render_template('create_meeting_error.html', error='Could not update Meeting')

def dict_compare(d1, d2):
    # convert data to set()
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())

    # Set intersection() method return a set that contains the items that exist in both set a, and set b.
    intersect_keys = d1_keys.intersection(d2_keys)

    # returns dictionary of all items in d1 that are NOT in d2
    added = d1_keys - d2_keys
    # returns dictionary of all items in d2 that are NOT in d1
    removed = d2_keys - d1_keys

    # returns dictionary {key: value, key: value} of all items that exist in both dicts that are different
    modified = {o: (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}

    # returns dictionary of all keys that exist in both dicts that are the same
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    print(modified)
    print(same)
    return modified


#################### EDIT PROFILE  ####################################
#####################################################################
@app.route('/edit/profile')
def send_to_edit_profile():
    user = User.get_by_email(session['email'])
    name = user.name.split(',')
    firstName = name[1]
    lastName = name[0]
    cardname = user.userinfo['cardname']
    cardnumber = user.userinfo['cardnumber']
    cardcode = user.userinfo['cardcode']
    zipcode = user.userinfo['zipcode']
    return render_template('edit_profile.html', user=user, firstName=firstName, lastName=lastName, cardname=cardname, cardnumber=cardnumber, cardcode=cardcode, zipcode=zipcode)

@app.route('/auth/edit_profile', methods=['POST'])
def edit_profile():

    fname = request.form['fname']
    lname = request.form['lname']

    email = request.form['email']
    password = request.form['password']

    cardname = request.form['cardname']
    cardnumber = request.form['cardnumber']
    cardcode = request.form['cardcode']
    zipcode = request.form['zipcode']

    name = lname + ', ' + fname
    cardinfo = {
        'cardname': cardname,
        'cardnumber': cardnumber,
        'cardcode': cardcode,
        'zipcode': zipcode
    }

    user = User.get_by_email(session['email'])
    if name != user.name:
        user.update_profile(user._id, 'name', name)
    if email != user.email:
        user.update_profile(user._id, 'email', email)
    if password != user.password:
        user.update_profile(user._id, 'password', password)

    items_to_update = dict_compare(user.userinfo, cardinfo)

    if items_to_update is not None:
        k = items_to_update.keys()
        for key in k:
            # items[key] returns a tuple: ('OLD VALUE', 'NEW VALUE') so we need the second element
            v = items_to_update[key][1]
            user.update_userinfo(user._id, key, v)
    return make_response(back_to_profile())


########## Search By Participation ############
@app.route('/participation-as-member')
def participation_membership():
    meetings = Meeting.get_members(session['email'])
    return render_template('meetings-participation-2.html', meetings=meetings)


########## PORT and App RUN() METHOD #############

if __name__ == '__main__':
    app.run(debug=True)

