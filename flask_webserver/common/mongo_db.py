from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError

import sys
import os


class MongoDB():
    def __init__(self, table):

        # get uri and login from environment variables
        db_uri = os.environ["PETRA_DATABASE_URI"]
        database = os.environ["MONGO_DATABASE"]
        username = os.environ["MONGO_USERNAME"]
        password = os.environ["MONGO_PASSWORD"]
        uri_prefix = db_uri.find("//") + 2
        uri = f'{db_uri[:uri_prefix]}{username}:{password}@{db_uri[uri_prefix:]}/{database}'
        print(f'* Database Connection: {uri}')

        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=20)
            self.client.server_info()
        except ServerSelectionTimeoutError as err:
            print("*" * 50)
            print("* Mongod instance is not running ...")
            print('* Start mongodb: sudo systemctl start mongod')
            print('* The databse may started but is not yet ready to accept connections.')
            print('* Increase the waiting time with env WAIT_AFTER (default: 10)')
            print("*" * 50)

            self.client = None
            exit(1)

        self.db = self.client["petra"]

        self.table_name = table
        self.table = self.db[table]

    def select_one(self, id):

        return self.table.find_one({"_id": id})

    def select_filtered(self, mask):
        return [matching for matching in self.table.find(mask)]

    def select_all(self):
        elements = []

        for elem in self.table.find():
            elements.append(elem)

        return elements

    def insert(self, data):

        return self.table.insert_one(data)

    def update(self, id, data):

        return self.table.update_one({"_id": id}, {"$set": data})

    def delete_all(self):

        return self.table.drop()

    def delete_one(self, id):

        return self.table.delete_one({"_id": id})

    def get_highest_id(self):

        if self.table.count_documents(filter={}) == 0:
            return 0

        return self.table.find().sort('_id', DESCENDING).limit(1).next()['_id']

    def filter(self, filter_data):

        elements = []

        for elem in self.table.find(filter_data):
            elements.append(elem)

        return elements
