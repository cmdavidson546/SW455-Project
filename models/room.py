__author__ = "christopherdavidson"

import uuid

from common.database import Database

class Room(object):

    def __init__(self, meetings, isAvailable=True, _id=None):
        self.meetings = dict() if meetings is None else meetings
        self._id = uuid.uuid4().hex if _id is None else _id
        self.isAvailable = isAvailable

    def json(self):
         return {
             'meetings': self.meetings,
             '_id': self._id
         }

    def save_to_mongo(self):
        Database.insert(collection='room', data=self.json())


    @classmethod
    def get_from_mongo(cls, id):
        room = Database.find_one('room', {'_id': id})
        return cls(**room)

    # UPDATE MEMBERS OF MEETING
    @classmethod
    def update_meetings(cls, room_id, newKey, newVal):
        if room_id is not None:
            Database.update_meeting(room_id, newKey, newVal)
            return 1
        return 0






