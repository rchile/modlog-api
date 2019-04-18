from modlog.common import valid_entry_id, filter_entry
from modlog.db import DB
from modlog import api

db = DB()


def get_entries(after=None, limit=100):
    """
    Loads entries from the cache first, then, if not enough entries were
    loaded from the cache, then the missing required ones are loaded from
    the reddit API.
    :param limit: The maximum of entries to be loaded.
    :param after: The entry ID to load entries after that one.
    :return: A `list` of entries.
    """

    after = valid_entry_id(after)

    # If the database is not ready, directly load from the database.
    if not db.ready:
        return api.get_entries(after=after)

    # Get the first entry or the `after` one.
    since = get_entry(after) if after else api.get_first_entry()
    entries = []

    # If the cache has the first entry. If not, the cache is ignored.
    if db.get_entry(since['id']):
        # If the `after` parameter is not passed, then the first entry is
        # included in the query.
        entries = list(db.get_entries(after=since['created_utc'], limit=limit, include=(not after)))

        # Store the last entry's ID to know after what entry we need to load
        # more entries if the required amount of entries was not met.
        if len(entries) > 0:
            after = entries[-1]['id']

    # Load entries from the API if the required amount of entries was not met
    if len(entries) < limit:
        more_entries = api.get_entries(after=after, limit=limit - len(entries))
        # Insert the new entries to the cache.
        db.insert_entries(more_entries)
        # For some reason, the pymongo library adds the _id attribute to the inserted entries.
        # Delete that from the entries because they can't be serialized.
        for entry in more_entries:
            if '_id' in entry:
                del entry['_id']
        entries += more_entries

    return [filter_entry(x) for x in entries]


def get_entry(entry_id):
    """
    Retrieve an entry from the cache first, or from the API if
    the entry is not on the cache. Note that entries loaded from the
    API are not inserted into the cache.
    :param entry_id: The entry `id` to look for.
    :return: The requested entry if found. `None` if not.
    """
    entry_id = valid_entry_id(entry_id)

    # Try to fetch the entry from the db and return it if it was found
    entry = db.get_entry(entry_id)
    if entry is not None:
        return filter_entry(entry)

    return api.get_entry(entry_id)
