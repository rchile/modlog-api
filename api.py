from common import valid_entry_id, serialize, get_reddit_instance, get_config

reddit = get_reddit_instance()
api = reddit.subreddit(get_config('SUBREDDIT', 'chile'))


def get_entries(*, after=None, before=None, limit=100):
    result = list(map(serialize, api.mod.log(limit=limit, params={'after': after, 'before': before})))

    return result


def get_first_entry():
    result = get_entries(limit=1)
    return None if len(result) == 0 else result[0]


def get_entry(entry_id):
    entry_id = valid_entry_id(entry_id)

    # Fetch the first after the selected one
    after_entries = get_entries(after=entry_id, limit=1)
    if len(after_entries) == 0:
        return None

    # Fetch the entry before the previous one, it should be the entry we want
    entry = get_entries(limit=1, before=after_entries[0].id)
    if len(entry) == 0:
        return None

    # If the fetched entry does not match the ID, then the entry does not exist
    entry = serialize(entry[0])
    if entry['id'] != entry_id:
        return None

    return entry
