__author__ = "christopherdavidson"

import uuid

from flask import session

from src.common.database import Database


class User(object):
    def __init__(self, name, email, password, _id=None):
        self.name = name
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "_id": self._id
        }

    def save_to_mongo(self):
        Database.insert("users", self.json())

    @staticmethod
    def login_valid(email, password):
        user = User.get_by_email(email)
        if user is not None:
            return user.password == password
        return False

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login(user_email):
        #login_valid already called in app.py
        # create new session using user's email account
        session['email'] = user_email

    @staticmethod
    def logout():
        # do we want to use:  session.clear() ???
        # [session.pop(key) for key in list(session.keys()) if key != '_flashes']
        session['email'] = None

    @classmethod
    def register(cls, name, email, password):
        # check if user has already registered email
        user = cls.get_by_email(email)
        # if not...create new user
        if user is None:
            new_user = cls(name, email, password)
            new_user.save_to_mongo()
            # start session upon registering
            session['email'] = email
        # else return invalid registration
        else:
            return False