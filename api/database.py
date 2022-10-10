from datetime import datetime, timedelta

from pymongo import MongoClient, DESCENDING

import settings
from .functions import filtered, filter_entry, try_int

if not settings.MONGODB_URL:
    raise RuntimeError('MONGODB_URL is not set')

client = MongoClient(settings.MONGODB_URL, connect=False)


class Modlog:
    def __init__(self) -> None:
        self.db = client.get_default_database()
        self.c_entries = self.db['entries']
    
    def entry(self, entry_id):
        entry = self.c_entries.find_one({'id': entry_id}, projection={'_id': 0})
        return filter_entry(entry)
    
    def entries(self, entry_id, limit=20, filters=None):
        after_entry = self.entry(entry_id)

        if not filters:
            filters = {}
        
        # Hide defined actions
        if settings.HIDDEN_ACTIONS:
            filters['action'] = {'$nin': settings.HIDDEN_ACTIONS}

        if after_entry:
            filters['created_utc'] = {'$lt': after_entry['created_utc']}
    
        entries = self.c_entries.find(filters, limit=limit, sort=[('created_utc', DESCENDING)], projection={'_id': 0})
        return filtered(entries)
    
    def entry_count(self, entry_type, since=None):
        result = self.c_entries
        since_utc = 0

        if since:
            since = str(since)
            if 2 > len(since) > 5:
                raise ValueError('Invalid since parameter length')
            
            since_val = try_int(since[:-1])
            unit = since[-1].lower()

            if unit not in ['h', 'd', 'm', 'y']:
                raise ValueError('Invalid `since` unit')
            if not since_val or since_val < 1:
                raise ValueError('Invalid `since` value')
            
            tdelta = None
            if unit == 'h':
                tdelta = timedelta(hours=since_val)
            elif unit == 'd':
                tdelta = timedelta(days=since_val)
            elif unit == 'm':
                tdelta = timedelta(days=since_val*30)
            else:
                tdelta = timedelta(days=tdelta*365)
            
            since = datetime.now() + tdelta
            since_utc = since.total_seconds()

        find_filter = {'created_utc': {'$gte': since_utc}} if since_utc else {}
        result = result.find(find_filter).aggregate([{'$group': {
            '_id': f'${entry_type}',
            'count': {
                '$sum': 1
            }
        }}])

        return {i['_id']: i['count'] for i in result}
    
    def action_count(self):
        return self.entry_count('action')
    
    def mod_action_count(self):
        return self.entry_count('mod')

    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
