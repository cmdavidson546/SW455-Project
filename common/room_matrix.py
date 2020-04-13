__author__ = 'christopherdavidson'

import uuid

from common.database import Database
from models.room import Room


class RoomMatrix(object):
    counter = 0     # shared for all instances

    # CONSTRUCTOR
    def __init__(self, roomNum=None, room_id=None, _id=None):
        self.roomNum = roomNum
        self.room_id = room_id
        self._id = uuid.uuid4().hex if _id is None else _id

    # STORED DATA IN MEETING CLASS
    def json(self):
        return {
            'room': self.roomNum,
            'room_id': self.room_id,
            '_id': self._id
        }

    def create_room(self):
        room = Room(meetings=None)
        RoomMatrix.counter = RoomMatrix.counter + 1
        self.roomNum = str(RoomMatrix.counter)
        self.room_id = room._id
        room.save_to_mongo()
        Database.insert(collection='office', data=self.json())
        return room._id

    @classmethod
    def get_rooms(cls):
        return [room for room in Database.find(collection='office', query={})]

    # DON"T WORK
    # since the Database method .find returns a pymongo cursor
    # we use cls(**item) which returns a new dict for
    # each list element instead of a pymongo cursor object
    # the double **item says to pass in all arguments.
    # TRY SOMETHING LIKE:
    #return [cls(**item) for item in items_from_db]

    @classmethod
    def get_by_id(cls, m_id):
        office = Database.find_one('office', {'_id': m_id})
        print(office)
        return m_id

    @classmethod
    def from_mongo(cls, id):
        meeting = Database.find_one('meeting', {'_id': id})
        return cls(**meeting)

    @classmethod
    def delete_room(cls, office_id):
        Database.remove_one(collection='office', searchVal=office_id)



