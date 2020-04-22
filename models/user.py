__author__ = "christopherdavidson"

import uuid
from flask import session
from common.database import Database


class User(object):
    def __init__(self, name, email, password, usertype, userinfo, _id=None):
        self.name = name
        self.email = email
        self.password = password
        self.usertype = usertype
        self.userinfo = dict() if userinfo is None else userinfo
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            "usertype": self.usertype,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "userinfo": self.userinfo,
            "_id": self._id
        }

    def check_if_admin(self):
        if self.usertype == 'admin':
            return True
        return False

    def check_if_client(self):
        if self.usertype == 'client':
            return True
        return False

    @classmethod
    def login_valid(cls, email, password):
        user = cls.get_by_email(email)
        if user is not False:
            return user.password == password
        return False

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)
        return False

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)
        return False

    @staticmethod
    def login(user_email):
        #login_valid already called in app.py -> register
        session['email'] = user_email

    @staticmethod
    def logout():
        session['email'] = None

        
    # GET MEETINGS FOR ONES USER CREATED
    def get_meetings(self):
        return Meeting.get_by_email(self.email)
    
        # EDIT PROFILE
    # Here I am setting a flag to return 0 for not updated and 1 for update successful
    @classmethod
    def update_profile(cls, user_id, newKey, newVal):
        if user_id is not None:
            Database.update_one('users', user_id, newKey, newVal)
            return 1
        return 0

    @classmethod
    def update_userinfo(cls, user_id, newKey, newVal):
        if user_id is not None:
            Database.update_userinfo(user_id, newKey, newVal)
