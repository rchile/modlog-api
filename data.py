from common import get_reddit_instance, serialize, valid_entry_id, get_config
from db import DB

LIMIT = 100
reddit = get_reddit_instance()
api = reddit.subreddit(get_config('SUBREDDIT', 'chile'))
db = DB()


def get_entries(after=None):
    after = valid_entry_id(after)
    if not db.ready:
        return get_entries_api(after=after)

    since = after if after else get_first_entry_api()['created_utc']
    entries = db.get_entries_since(since, limit=LIMIT)

    if len(entries) < LIMIT:
        after = None if len(entries) == 0 else entries[-1]['created_utc']
        more_entries = get_entries_api(after=after, limit=LIMIT-len(entries))
        entries += more_entries

    return entries


def get_entry(entry_id):
    entry_id = valid_entry_id(entry_id)

    # Try to fetch the entry from the db and return it if it was found
    entry = db.get_entry(entry_id)
    if entry is not None:
        return entry

    # Fetch the first after the selected one
    after_entries = get_entries_api(after=entry_id, limit=1)
    if len(after_entries) == 0:
        return None

    # Fetch the entry before the previous one, it should be the entry we want
    entry = get_entries_api(limit=1, before=after_entries[0].id)
    if len(entry) == 0:
        return None

    # If the fetched entry does not match the ID, then the entry does not exist
    entry = serialize(entry[0])
    if entry['id'] != entry_id:
        return None

    return entry


def get_first_entry_api():
    result = get_entries_api(limit=1)
    return None if len(result) == 0 else result[0]


def get_entries_api(*, after=None, before=None, limit=100):
    print('[API] Loading entries... (limit: {}, after: {}, before: {})'.format(limit, after, before))
    result = list(map(serialize, api.mod.log(limit=limit, params={'after': after, 'before': before})))

    if limit > 1:
        db.insert_entries(result)

    return result
