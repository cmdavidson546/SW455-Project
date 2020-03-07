__author__ = 'christopherdavidson'

import pymongo
import os

class Database(object):
    URI = os.environ.get("MONGODB_URI")
    DATABASE = None                                     # shared for all instances

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)      # connect to mongodb instance
        Database.DATABASE = client.get_default_database()   

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)
    
    @staticmethod
    def update_one(collection, searchVal, newKey, newVal):
        query = {'_id': searchVal}
        newdata = {'$set': {newKey: newVal}}
        Database.DATABASE[collection].update_one(query, newdata)

    @staticmethod
    def remove_one(collection, searchVal):
        Database.DATABASE[collection].delete_one({'_id': searchVal})