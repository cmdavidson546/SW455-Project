__author__ = "christopherdavidson"

import datetime
import uuid

from common.database import Database


class Payment(object):

    def __init__(self, email, cardinfo, created_date=datetime.datetime.today(), _id=None):
        self.email = email
        self.cardinfo = cardinfo
        self.created_date = created_date
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            "email": self.email,
            "cardinfo": self.cardinfo,
            "created_date": self.created_date,
            "_id": self._id
        }

    def save_to_mongo(self):
        Database.DATABASE.insert(collection='payment', query=self.json())

    @classmethod
    def get_from_mongo(cls):
        # return [cls(**complaints) for complaint in Database.find(collection='complaint', query=None)]

        # return list object of all payments in DB
        return [payment for payment in Database.find(collection='payment', query=None)]

    @classmethod
    def get_payment_by_email(cls, email):
        return [payment for payment in Database.find(collection='payment', query={'email': email})]