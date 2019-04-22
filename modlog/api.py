from modlog.common import valid_entry_id, serialize, get_config, get_reddit_instance

reddit = get_reddit_instance()
api = reddit.subreddit(get_config('SUBREDDIT', 'chile'))
default_limit = int(get_config('ENTRIES_LIMIT', 100))


def get_entries(*, after=None, before=None, limit=default_limit):
    """
    Fetch entries from the reddit API
    :param after: Fetch entries after this entry `id`
    :param before: Fetch entries before this entry `id`
    :param limit: The maximum amount of entries to retrieve.
    :return: The `list` of entries retrieved from the API.
    """

    # The result is converted to list for easier JSON serialization.
    result = list(map(serialize, api.mod.log(
        limit=limit, params={'after': after, 'before': before}
    )))

    return result


def get_first_entry():
    """
    Get the current first entry from the reddit API.
    :return: The entry. None if no entry was found.
    """
    result = get_entries(limit=1)
    return None if len(result) == 0 else result[0]


def get_entry(entry_id):
    """
    Get a single entry from the reddit API.
    :param entry_id: The entry `id` to look for.
    :return: The entry if it was found, None if not.
    """
    entry_id = valid_entry_id(entry_id)

    # The reddit API does not provide a way to fetch a certain entry, but
    # we can load the one after the one we want, then load the one before
    # what we just loaded. That entry's ID matches with the passed one,
    # then we found it.

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
