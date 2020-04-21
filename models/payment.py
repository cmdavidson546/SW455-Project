__author__ = "christopherdavidson"

import datetime
import uuid
from common.database import Database

#############################################
# PAYMENT CLASS: Keeps track of Payments made for special events
#############################################

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
        Database.insert(collection='payment', data=self.json())

    @classmethod
    def get_from_mongo(cls):
        return [payment for payment in Database.find(collection='payment', query=None)]

    @classmethod
    def get_payment_by_email(cls, email):
        return [payment for payment in Database.find(collection='payment', query={'email': email})]

    @classmethod
    def delete_payment(cls, payment_id):
        Database.remove_one(collection='payment', searchVal=payment_id)

    @classmethod
    def get_by_id(cls, id):
        payment = Database.find_one('payment', {'_id': id})
        if payment is not None:
            return cls(**payment)
        return False