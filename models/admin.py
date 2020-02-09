from flask import session

from common.database import Database
from models.user import User


class Admin(User):
    def __init__(self, name, email, password, usertype, userinfo, _id=None):
        super().__init__(name, email, password, usertype, userinfo, _id)

    def isAdmin(self):
        return True

    def json(self):
        return {
            "usertype": self.usertype,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "userinfo": self.userinfo,
            "_id": self._id
        }


    @classmethod
    def register(cls, name, email, password, usertype, userinfo, _id=None):
        # check if user has already registered email
        user = cls.get_by_email(email)
        # if not...create new user
        if user is None:
            new_user = cls(name, email, password, usertype, userinfo, _id=None)
            new_user.save_to_mongo()
            # start session upon registering
            session['email'] = email
        # else return invalid registration
        else:
            return False

    def save_to_mongo(self):
        Database.insert("users", self.json())

