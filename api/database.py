from pymongo import MongoClient, DESCENDING

import settings
from .functions import filtered

if not settings.MONGODB_URL:
    raise RuntimeError('MONGODB_URL is not set')

client = MongoClient(settings.MONGODB_URL, connect=False)


class Modlog:
    def __init__(self) -> None:
        self.db = client.get_default_database()
        self.c_entries = self.db['entries']
    
    def entry(self, entry_id):
        entry = self.c_entries.find_one({'id': entry_id}, projection={'_id': 0})
        return filtered(entry)
    
    def entries(self, entry_id, limit=20, filters=None):
        after_entry = self.entry(entry_id)

        if not filters:
            filters = {}

        if after_entry:
            filters['created_utc'] = {'$lt': after_entry['created_utc']}
    
        entries = self.c_entries.find(filters, limit=limit, sort=[('created_utc', DESCENDING)], projection={'_id': 0})
        return filtered(entries)

    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
