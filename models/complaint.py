__author__ = "christopherdavidson"

import datetime
import uuid
from common.database import Database

####################################
# COMPLAINT CLASS: Keeps Track of Complaints from Clients 
####################################

class Complaint(object):

    def __init__(self, email, message, created_date=datetime.datetime.today(), _id=None):
        self.email = email
        self.message = message
        self.created_date = created_date
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            "email": self.email,
            "message": self.message,
            "created_date": self.created_date,
            "_id": self._id
        }

    def save_to_mongo(self):
        Database.insert(collection='complaint', data=self.json())

    @classmethod
    def get_from_mongo(cls):
        return [complaint for complaint in Database.find(collection='complaint', query=None)]

    # DELETE Complaint
    @classmethod
    def delete_complaint(cls, complaint_id):
        Database.remove_one(collection='complaint', searchVal=complaint_id)

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("complaint", {"_id": _id})
        if data is not None:
            return cls(**data)
        return False