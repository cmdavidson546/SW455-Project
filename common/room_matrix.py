__author__ = 'christopherdavidson'

import uuid

from common.database import Database
from models.room import Room


class RoomMatrix(object):
    counter = 0     # shared for all instances

    # CONSTRUCTOR
    def __init__(self, roomNum=None, room_id=None, _id=None):
        RoomMatrix.counter += 1
        self.roomNum = RoomMatrix.counter
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
        self.room_id = room._id
        room.save_to_mongo()
        Database.insert(collection='office', data=self.json())
        return room._id

    @classmethod
    def get_rooms(cls):
        return [room for room in Database.find(collection='office', query={})]

    @classmethod
    def get_by_id(cls, m_id):
        office = Database.find_one('office', {'_id': m_id})
        r_id = office['room_id']
        return r_id

    @classmethod
    def delete_room(cls, office_id, room_id=None):
        if room_id is not None:
            RoomMatrix.counter -= 1
            # room.from_mongo(by_id) should return a class object
            # so we can use (.) operator to access members of room
            room = Room.get_from_mongo(room_id)
            # need to make sure we don't delete room and its corresponding matrix_id
            # if there are existing meetings in the room object; else don't delete either object
            if room.meetings is None:
                room.delete_room_base(room_id)
                Database.remove_one(collection='office', searchVal=office_id)
                return True
        return False


