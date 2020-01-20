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
        #Database.DATABASE = client['heroku_qrf111l3']

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)