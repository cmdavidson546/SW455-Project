__author__ = 'christopherdavidson'

import pymongo

class Database(object):
    URI = "mongodb://127.0.0.1:27017"
    DATABASE = None                                     # shared for all instances

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)      # connect to mongodb instance
        Database.DATABASE = client['sweng455project']       # get the db using dictionary style access

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)