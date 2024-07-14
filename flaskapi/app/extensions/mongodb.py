from flask import g, current_app
from pymongo import MongoClient
import os
import pymongo.database

def get_mongodb(db_name="min_object_storage") -> pymongo.database.Database:
    if 'mongodb' not in g:
        mongo_uri = current_app.config.get("MONGO_URI", None)
        if not mongo_uri:
            raise EnvironmentError("MONGO_URI not set.")
        client = MongoClient(mongo_uri)
        db = client[db_name]
        g.mongodb = db
    return g.mongodb