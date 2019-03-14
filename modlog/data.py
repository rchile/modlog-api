from modlog.common import valid_entry_id
from modlog.db import DB
from modlog import api

LIMIT = 100
db = DB()


def get_entries(after=None):
    after = valid_entry_id(after)
    if not db.ready:
        return api.get_entries(after=after)

    since = get_entry(after) if after else api.get_first_entry()
    entries = []

    if db.get_entry(since['id']):
        entries = list(db.get_entries(after=since['created_utc'], limit=LIMIT, include=(not after)))
        if len(entries) > 0:
            after = entries[-1]['id']

    if len(entries) < LIMIT:
        more_entries = api.get_entries(after=after, limit=LIMIT - len(entries))
        db.insert_entries(more_entries)
        for entry in more_entries:
            if '_id' in entry:
                del entry['_id']
        entries += more_entries

    return entries


def get_entry(entry_id):
    entry_id = valid_entry_id(entry_id)

    # Try to fetch the entry from the db and return it if it was found
    entry = db.get_entry(entry_id)
    if entry is not None:
        return entry

    return api.get_entry(entry_id)
