def filter_entry(entry):
    """
    Filters data out from a hidden (sensitive) entry
    :param entry: The entry to remove it's public data
    :return: The filtered entry
    """

    if entry.get('hidden', None):
        clear_attrs = 'target_author,target_permalink,target_body,target_title,' \
                      'target_fullname,description,details'.split(',')
        entry = {**dict(entry), **zip(clear_attrs, [None] * len(clear_attrs))}

    return entry


def filtered(entries):
    if not entries:
        return entries
    try:
        return [filter_entry(e) for e in entries]
    except (TypeError, AttributeError):
        return filter_entry(entries)


def response(message=None, status=200):
    return {'message': message}, status


def try_int(value, default=None):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default or value
