import pymongo
from pymongo import MongoClient
from modlog.common import get_config


class DB:
    def __init__(self):
        self._db = None
        self._col = None
        self.ready = False

        db_uri = get_config('MONGODB_URI')
        if not db_uri:
            print('Database is disabled')
            return

        print('Connecting to the database...')
        client = MongoClient(db_uri)
        self._db = client.get_database()
        self._col = self._db.get_collection('entries')
        self.ready = True
        col_count = self._col.count()

        print('Connected to the database, name:', self._db.name)
        print('DB entry count:', col_count)

        self._col.create_index('id', unique=True)
        self._col.create_index([('created_utc', pymongo.DESCENDING)])

    def get_entries(self, after=None, limit=100):
        if not self.ready:
            return []

        query_filter = {'created_utc': {'$lt': after}} if after else None
        return self._col.find(query_filter, limit=limit, sort=[("created_utc", pymongo.DESCENDING)],
                              projection={'_id': 0})

    def get_entries_since(self, since=None, limit=100):
        if not self.ready:
            return []

        query_filter = {'created_utc': {'$lte': since}} if since else None
        return self._col.find(query_filter, limit=limit, sort=[("created_utc", pymongo.DESCENDING)],
                              projection={'_id': 0})

    def get_entry(self, entry_id):
        if not self.ready:
            return None

        entry = self._col.find_one({'id': entry_id}, projection={'_id': 0})
        return entry

    def insert_entry(self, entry):
        if not self.ready:
            return None

        return self._col.update_one({'id': entry['id']}, {'$set': entry}, upsert=True)

    def insert_entries(self, entries):
        if not self.ready:
            return []

        id_list = [e['id'] for e in entries]
        already_in = self._col.find({'id': {'$in': id_list}}, projection={'_id': 0})
        id_list_already = [e['id'] for e in list(already_in)]

        missing_entries = [e for e in entries.copy() if e['id'] not in id_list_already]
        if len(missing_entries) > 0:
            return self._col.insert_many(missing_entries, ordered=False)
        else:
            return []
