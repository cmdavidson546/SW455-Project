__author__ = "christopherdavidson"

import uuid
import datetime

from flask import session

from common.database import Database


class Meeting(object):

    # CONSTRUCTOR
    def __init__(self, day, time, email, members, created_date=datetime.datetime.today(), _id=None):
        self.day = day
        self.time = time
        self.email = email
        self.members = dict() if members is None else members
        self.created_date = created_date
        self._id = uuid.uuid4().hex if _id is None else _id

    # STORED DATA IN MEETING CLASS
    def json(self):
        return {
            'day': self.day,
            'time': self.time,
            'email': self.email,
            'members': self.members,
            '_id': self._id,
            'created_date': self.created_date
        }

    # SAVE MEETINGS TO DB
    def save_to_mongo(self):
        Database.insert(collection='meeting', data=self.json())

    # FIND ONE BY MEETING ID
    # return **class object rather than pymongo cursor
    @classmethod
    def from_mongo(cls, id):
        meeting = Database.find_one('meeting', {'_id': id})
        return cls(**meeting)

    @classmethod
    def get_all_meetings(cls):
        return [meeting for meeting in Database.find(collection='meeting', query=None)]

    # TIME CONFLICT CHECK FOR SCHEDULING NEW MEETING
    @classmethod
    def isAvailable(cls, day, time):
        data = Database.find_one(collection='meeting', query={'day': day})
        print(data)
        # get list with DAY as cls.day
        if data is None:
            return True
        for d in data:
            print(d)
            # if time slot is taken
            if d == 'time':
                print(data[d], time)
                if data[d] == time:
                    return False
        return True

    # FIND MANY BY USER EMAIL
    @classmethod
    def get_by_email(cls, email):
        return [meeting for meeting in Database.find(collection='meeting', query={'email': email})]

    # REGISTER NEW MEETING
    @classmethod
    def register(cls, day, time, email, members):
        # check if user has already registered email
        user = cls.get_by_email(email)

        # if not...create new user
        if user is None:
            new_user = cls(day, time, email, members)
            new_user.save_to_mongo()
            # start session upon registering
            session['email'] = email
        # else return invalid registration
        else:
            return False

    # DELETE MEETING
    @classmethod
    def delete_meeting(cls, meeting_id):
        Database.remove_one(collection='meeting', searchVal=meeting_id)


    # EDIT MEETING METHOD
    # Here I am setting a flag to return 0 for not updated and 1 for update successful
    @classmethod
    def update_meeting(cls, meeting_id, newKey, newVal):
        if meeting_id is not None:
            Database.update_one('meeting', meeting_id, newKey, newVal)
            return 1
        return 0

    # UPDATE MEMBERS OF MEETING
    @classmethod
    def update_members(cls, meeting_id, newKey, newVal):
        if meeting_id is not None:
            Database.update_member(meeting_id, newKey, newVal)
            return 1
        return 0

    # GET MEMBERSHIP
    @classmethod
    def get_members(cls, email):
        if email is not None:
            list1 = [meeting for meeting in Database.find(collection='meeting', query={'members.p1': email})]
            list1.append([meeting for meeting in Database.find(collection='meeting', query={'members.p2': email})])
            list1.append([meeting for meeting in Database.find(collection='meeting', query={'members.p3': email})])
            list1.append([meeting for meeting in Database.find(collection='meeting', query={'members.p4': email})])
            list1.append([meeting for meeting in Database.find(collection='meeting', query={'members.p5': email})])
            list1.append([meeting for meeting in Database.find(collection='meeting', query={'members.p6': email})])
            list1.append([meeting for meeting in Database.find(collection='meeting', query={'members.p7': email})])
            list1.append([meeting for meeting in Database.find(collection='meeting', query={'members.p8': email})])
            list1.append([meeting for meeting in Database.find(collection='meeting', query={'members.p9': email})])
            list1.append([meeting for meeting in Database.find(collection='meeting', query={'members.p10': email})])
            return list1

    @classmethod
    def get_by_day(cls, usr_day):
        return [ meeting for meeting in Database.find(collection='meeting', query={'day': usr_day}) ]

    @classmethod
    def get_by_time(cls, usr_time):
        return [ meeting for meeting in Database.find(collection='meeting', query={'time': usr_time}) ]

    @classmethod
    def get_by_usr(cls, usr_day):
        pass

