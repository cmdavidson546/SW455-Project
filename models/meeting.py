__author__ = "christopherdavidson"

import uuid
import datetime

from flask import session

from common.database import Database

"""
This MSS keeps track of meetings schedule and which people are in what meeting in which room. 
The application is not required to perform scheduling.
"""

class Meeting(object):
    def __init__(self, day, time, email, members, created_date=datetime.datetime.today(), _id=None):
        self.day = day
        self.time = time
        self.email = email
        self.members = dict() if members is None else members
        self.created_date = created_date
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            'day': self.day,
            'time': self.time,
            'email': self.email,
            'members': self.members,
            '_id': self._id,
            'created_date': self.created_date
        }

    def save_to_mongo(self):
        Database.insert(collection='meeting', data=self.json())

    # return class object rather than pymongo cursor
    @classmethod
    def from_mongo(cls, id):
        meeting = Database.find_one('meeting', {'_id': id})
        return cls(**meeting)

    # search by admin email
    # this does not work with returning pymongo cursor (e.g., 'for d in d for x in x:' )
    # which returns error: TypeError: type object argument after ** must be a mapping, not Cursor
    @classmethod
    def get_by_email(cls, email):
        #data = Database.find('meeting', {'email': email})
        #return cls(**data)
        # ADD SORT TO DATABASE.py:  then add to this func: cls.sort({'email': email}
        return [meeting for meeting in Database.find(collection='meeting', query={'email': email})]

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

    @classmethod
    def delete_meeting(cls, meeting_id):
        Database.remove_one(collection='meeting', searchVal=meeting_id)
