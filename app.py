__author__ = "christopherdavidson"

##########################################################
#################### IMPORTS #############################
##########################################################

from flask import Flask, render_template, request, session, jsonify, make_response
from common.database import Database
from common.room_matrix import RoomMatrix
from models.complaint import Complaint
from models.payment import Payment
from models.meeting import Meeting
from models.room import Room
from models.admin import Admin
from models.client import Client
from models.user import User
import os
import re
import random

##########################################################
##### Start App, initialize DB, set SERVER HOME ENDPOINT ####
##########################################################

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
newRoom = RoomMatrix()

# initialize db
@app.before_first_request
def initialize_database():
    Database.initialize()

# set home endpoint
@app.route('/')
def open_app():
    return render_template('user_type.html')

##################################################################
####### INITIAL STARTUP, LOGIN, LOGOFF, REGISTER METHODS #########
##################################################################

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


####################################
########### REGISTRATION ###########
####################################

# route to register page
@app.route('/register')
def register_page():
    return render_template('register.html')

# route to register page from admin
@app.route('/register_by_admin')
def register_page_byadmin():
    return render_template('register-by-admin.html')

@app.route('/auth/register_by_admin', methods=['POST'])
def register_user_by_admin():

    # make name suitable for db
    fname = request.form['fname']
    lastname = request.form['lastname']
    name = lastname + ', ' + fname

    # get email and password
    email = request.form['email']
    password = request.form['password']

    admincode = request.form['admincode']
    acode = {
        'admincode': admincode
    }

    if request.method == 'POST':
        # add another layer by seeing if 'email' contains @specific_company_name
        if Admin.register(name=name, email=email, password=password, usertype='admin', userinfo=acode) is False:
            return render_template('duplicate_user.html', error='Admin Email Already Registered as User')
        else:
            Admin.register(name=name, email=email, password=password, usertype='admin', userinfo=acode)
            return make_response(back_to_profile())
    return render_template('registration_error.html', error='Invalid registration')

# endpoint from main registration form  -> client_profile.html
@app.route('/auth/register', methods=['POST', 'GET'])
def register_user():
    # get admin form data
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


############################################
####### LOGIN EXISTING USER METHODS #########
############################################

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

# create session for logged in user -> client_profile.html
@app.route('/client/login', methods=['POST', 'GET'])
def client_login():
    # get email and password : IN OTHER ITERATIONS WE CAN GET POST from hidden ajax login form
    email = request.form['email']
    password = request.form['password']
    if password is None:
        password = ""
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

############################################
####### BACK TO MENU LINK METHODS #########
############################################

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
            return render_template('client_profile.html', email=session['email'], name=user.name)
        elif user.check_if_admin():
            return render_template('admin_profile.html', email=session['email'], name=user.name)
        else:
            return render_template('login_error.html', error='Invalid Request')
    return render_template('login_error.html', error='Invalid Request')

############################################
########### MEETING METHODS ###########
############################################

@app.route('/auth/newmeeting', methods=['POST', 'GET'])
def new_meeting():
    return render_template('create_meeting.html')

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

        # get all available rooms in DB
        rooms = RoomMatrix.get_rooms()

        # gets random room number to assign new meetings to random room number
        random.random()
        # random.randint selects (start, end) with both ends inclusive
        r_int = random.randint(0, (len(rooms)-1))
        # get room object using a random room_id assigned from the RoomMatrix
        room = Room.get_from_mongo(rooms[r_int]['room_id'])
        # room object stores room number
        r_number = room.roomNum
        # create the meeeting
        meeting = Meeting(day=day, time=time, r_number=r_number, email=email, members=member_emails)

        # if meeting day/time available, ALSO update room list with new meeting and save meeting to DB
        if meeting.isAvailable(day, time):
            room.update_meetings(room._id, day + time, meeting._id)
            meeting.save_to_mongo()
            return make_response(back_to_profile())
    return render_template('create_meeting_error.html', error="Meeting Day-Time already taken", email=session['email'])

########## Delete Meeting  #############
@app.route('/delete_one/<string:meeting_id>')
def delete_one(meeting_id):
    # need day and time of meeting
    meeting = Meeting.from_mongo(meeting_id)
    day = meeting.day
    time = meeting.time
    searchKey = day+time

    # find rooms with the given meeting_id in the 'meetings.**' field
    # to delete them from 'room' collection
    # .get_rooms() returns a dict() object which must be access like a python dict().
    # room_id is accessed as room['room_id'] but not room.room_id (class access)

    # search rooms by a meeting_id; if search returns True
    if Room.find_by_meeting(searchKey=searchKey, meeting_id=meeting_id):
        room_object = Room.find_by_meeting(searchKey=searchKey, meeting_id=meeting_id)

        # update the room using _id to erase the meeting from the existing meeting. list
        Room.erase_meeting(room_id=room_object._id, searchKey=searchKey)

    # delete the meeting from 'meetings' collection and return to profile dashboard
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
        return render_template('meetings-by-creator.html', email=session['email'], name=user.name, meetings=meetings)
    return make_response(back_to_profile())

# EDIT MEETING
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
        # make json object (or python dict...same thing)
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

        # double check the meeeting day-time combo is not taken already
        # proceed to check if anything has changed from original...
        # if so swap using update_meeting()
        if meeting.isAvailable(day, time):
            if day != meeting.day:
                meeting.update_meeting(meeting_id, 'day', day)
            if time != meeting.time:
                meeting.update_meeting(meeting_id, 'time', time)

        # Next Compare dictionaries of user made member-list vs. original member-list
        # returns the different items between the two dictionaries in the member dicts
        items_to_update = dict_compare(meeting.members, members)

        if items_to_update is not None:
            # get keys of the elements in the update list
            k = items_to_update.keys()
            for key in k:
                # items[key] returns a tuple: ('OLD VALUE', 'NEW VALUE') so we need the second element
                v = items_to_update[key][1]
                meeting.update_members(meeting_id, key, v)
        # GET MEETINGS
        meetings = Meeting.get_by_email(session['email'])
        return render_template('meetings-by-creator.html', email=session['email'], name=user.name, meetings=meetings)
    return render_template('create_meeting_error.html', error='Could not update Meeting')

############################################
########### COMPARE 2 DICTIONARIES ###########
############################################

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
    #print(modified)
    #print(same)
    return modified

#######################################################
####### PROFILE and BILLING METHODS ###########
#######################################################

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
    return render_template('edit_profile.html', user=user, firstName=firstName, lastName=lastName, cardname=cardname,
                           cardnumber=cardnumber, cardcode=cardcode, zipcode=zipcode)


@app.route('/edit_billing_admin', methods=['POST'])
def send_to_edit_billing():
    email = request.form['update-bill-input']
    if email is not None:
        user = User.get_by_email(email)
        if user is not False:
            name = user.name.split(',')
            firstName = name[1]
            lastName = name[0]
            cardname = user.userinfo['cardname']
            cardnumber = user.userinfo['cardnumber']
            cardcode = user.userinfo['cardcode']
            zipcode = user.userinfo['zipcode']
            return render_template('edit-profile-by-admin.html', email=email, firstName=firstName, lastName=lastName,
                                   cardname=cardname, cardnumber=cardnumber, cardcode=cardcode, zipcode=zipcode)
    return render_template('update-billing-error.html', error='No User found by that email address.')

@app.route('/auth/edit_profile_by_admin', methods=['POST'])
def edit_profile_by_admin():
    email = request.form['email']
    cardname = request.form['cardname']
    cardnumber = request.form['cardnumber']
    cardcode = request.form['cardcode']
    zipcode = request.form['zipcode']
    cardinfo = {
        'cardname': cardname,
        'cardnumber': cardnumber,
        'cardcode': cardcode,
        'zipcode': zipcode
    }
    user = User.get_by_email(email)
    items_to_update = dict_compare(user.userinfo, cardinfo)

    if items_to_update is not None:
        k = items_to_update.keys()
        for key in k:
            # items[key] returns a tuple: ('OLD VALUE', 'NEW VALUE') so we need the second element
            v = items_to_update[key][1]
            user.update_userinfo(user._id, key, v)
    return make_response(back_to_profile())

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


################################################
########### CREATE, EDIT, VIEW ROOMS ###########
############################################

@app.route('/add_room')
def add_rooms():
    # create room returns room _id
    room_id = newRoom.create_room()
    return render_template('add-room-success.html')

@app.route('/view_rooms')
def view_rooms():
    rooms = RoomMatrix.get_rooms()
    return render_template('view-avail-rooms.html', rooms=rooms)

@app.route('/delete_room')
def delete_room_redirect():
    rooms = RoomMatrix.get_rooms()
    return render_template('view-avail-rooms.html', rooms=rooms)

# ######### delete room from room_matrix and room.py #############
@app.route('/delete_room/<string:office_id>')
def delete_room(office_id):
    room_id = RoomMatrix.get_by_id(office_id)
    RoomMatrix.delete_room(office_id, room_id)
    return make_response(back_to_profile())

############################################
########### SEARCH AND DISPLAY METHODS ###########
############################################

########## Search By Participation ############
@app.route('/participation-as-member')
def participation_membership():
    meetings = Meeting.get_members(session['email'])
    return render_template('meetings-participation-2.html', meetings=meetings)

########## Display Meetings by Room #############
@app.route('/display_by_room')
def display_meetings_by_room():
    # for room number and room_id
    # returns list type
    rooms = RoomMatrix.get_rooms()

    # get meetings
    meetings = dict()
    for room in rooms:
        # get room_id's from matrix list iteratively
        room_id = room['room_id']

        # obtain room in Room class format
        meetingRoom = Room.get_from_mongo(room_id)
        meetings.update({meetingRoom.roomNum : meetingRoom.meetings})
    return render_template('meetings-by-room.html', meetings=meetings)



########## Display All Meetings #############
@app.route('/display_by_week')
def display_all():
    meetings = Meeting.get_all_meetings()
    return render_template('meetings-by-week.html', meetings=meetings)

########## Display Meetings by Day of the Week #############
@app.route('/display_by_day', methods=['POST'])
def display_by_day():
    day_select = request.form['day-select']
    meetings = Meeting.get_by_day(day_select)
    return render_template('meetings-by-day.html', meetings=meetings)

########## Display Meetings by Time of the Day #############
@app.route('/display_by_time', methods=['POST'])
def display_by_time():
    time_select = request.form['time-select']
    meetings = Meeting.get_by_time(time_select)
    return render_template('meetings-by-time.html', meetings=meetings)

########## Display Meetings by User #############
@app.route('/display_by_user', methods=['POST'])
def display_by_user():
    user_email = request.form['user-select-input']
    meetingsC = Meeting.get_by_email(user_email)
    meetingsP = Meeting.get_members(user_email)
    return render_template('meetings-by-usr.html', email=user_email, meetingsC=meetingsC, meetingsP=meetingsP)


#############################################
######### COMPLAINT CLASS METHODS #########
#############################################

@app.route('/file_complaint')
def fileComplaint():
    return render_template('file-complaint.html', email=session['email'])

@app.route('/auth/file_complaint', methods=['POST'])
def file_complaint():
    email = request.form['email']
    message = request.form['message']
    complaint = Complaint(email, message)
    complaint.save_to_mongo()
    return make_response(back_to_profile())

@app.route('/view_complaints')
def view_complaints():
    complaints = Complaint.get_from_mongo()
    return render_template('view-complaints.html', complaints=complaints)


@app.route('/comp_respond_one/<string:complaint_id>')
def respond_to_complaint(complaint_id):
    complaint = Complaint.get_by_id(complaint_id)
    return render_template('respond-to-complaint.html', complaint=complaint)

@app.route('/auth/comp_respond_one', methods=['POST'])
def response_to_complaint():
    message = request.form['message']
    print(message)
    return make_response(back_to_profile())

@app.route('/comp_delete_one/<string:complaint_id>')
def delete_complaint(complaint_id):
    Complaint.delete_complaint(complaint_id)
    return make_response(back_to_profile())


#############################################
######### PAYMENT CLASS METHODS #########
#############################################

@app.route('/pay_for_special')
def paySpecial():
    user = User.get_by_email(session['email'])
    cardname = user.userinfo['cardname']
    cardnumber = user.userinfo['cardnumber']
    cardcode = user.userinfo['cardcode']
    zipcode = user.userinfo['zipcode']
    return render_template('pay-for-special-room.html', email=user.email, cardname=cardname, cardnumber=cardnumber, cardcode=cardcode, zipcode=zipcode)


@app.route('/auth/pay_for_special', methods=['POST'])
def pay_special_payments():
    email = request.form['email']
    cardname = request.form['cardname']
    cardnumber = request.form['cardnumber']
    cardcode = request.form['cardcode']
    zipcode = request.form['zipcode']
    cardinfo = {
        'cardname': cardname,
        'cardnumber': cardnumber,
        'cardcode': cardcode,
        'zipcode': zipcode
    }
    payment = Payment(email=email, cardinfo=cardinfo)
    payment.save_to_mongo()
    return make_response(back_to_profile())

@app.route('/view/special_payments')
def view_special_payments():
    payments = Payment.get_from_mongo()
    return render_template('view-payments.html', payments=payments)

@app.route('/pay_delete_one/<string:payment_id>')
def delete_payment(payment_id):
    Payment.delete_payment(payment_id)
    return make_response(back_to_profile())

# Does not do anything... final version should allow user to edit payment
@app.route('/pay_edit_one/<string:payment_id>')
def edit_payment(payment_id):
    payment = Payment.get_by_id(payment_id)
    return make_response(back_to_profile())


#############################################
########## PORT and App.RUN METHOD ########
#############################################

if __name__ == '__main__':
    app.run(debug=True)

