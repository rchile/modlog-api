import pymongo
from pymongo import MongoClient
from common import get_config


class DB:
    def __init__(self):
        self._db = None
        self._col = None
        self.ready = False

        db_uri = get_config('MONGODB_URI')
        if not db_uri:
            print('Database is disabled')
            return

        client = MongoClient(db_uri)
        self._db = client.get_database()
        self._col = self._db.get_collection('entries')
        self.ready = True

        print('Connected to the database, name:', self._db.name)
        print('DB entry count:', self._col.count())

    def get_entries(self, after=None, limit=100):
        if not self.ready:
            return []

        query_filter = {'$lt': {'created_utc': after['created_utc']}} if after else None
        return self._col.find(filter=query_filter, limit=limit, sort=("created_utc", pymongo.DESCENDING))

    def get_entries_since(self, since=None, limit=100):
        if not self.ready:
            return []

        query_filter = {'$le': {'created_utc': since}} if since else None
        return self._col.find(filter=query_filter, limit=limit, sort=("created_utc", pymongo.DESCENDING))

    def get_entry(self, entry_id):
        if not self.ready:
            return None

        entry = self._col.find_one({'id': entry_id})
        del entry['_id']
        return entry

    def insert_entry(self, entry):
        if not self.ready:
            return None

        return self._col.update_one({'id': entry['id']}, {'$set': entry}, upsert=True)

    def insert_entries(self, entries):
        if not self.ready:
            return []

        return []
