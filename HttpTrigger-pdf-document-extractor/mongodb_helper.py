#!/usr/bin/env python

import os
import pymongo

class MongoDBHelper(object):
    def __init__(self, uri, database, collection) -> None:
        self.client = pymongo.MongoClient(uri)
        self.db = self.client.get_database(database)
        self.collection = self.db.get_collection(collection)
    
    # def insert_one(self, document) -> pymongo.results.InsertOneResult:
    #     return self.collection.insert_one(document)
    
    def upsert_one(self, document) -> pymongo.results.UpdateResult:
        return self.collection.update_one({'attributes.sha256_file_hash': document['attributes']['sha256_file_hash']}, {'$set': document}, upsert=True)
    
    def delete_all(self) -> pymongo.results.DeleteResult:
        return self.collection.delete_many({})

    def close(self) -> None:
        self.client.close()


if __name__ == '__main__':
    mongo_helper = MongoDBHelper(os.environ['MY_MONGODB_URI'], os.environ['MY_MONGODB_DATABASE'], os.environ['MY_MONGODB_COLLECTION'])
    mongo_helper.delete_all()
    mongo_helper.client.close()
