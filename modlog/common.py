import os
import random
import re
from praw.models import ModAction

pat_modentry = re.compile(r'^(ModAction_)?[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$')
pat_oauth_code = re.compile(r'^[a-zA-Z0-9\-_]{27}$')
pat_oauth_state = re.compile(r'^[a-zA-Z0-9]{12}$')


def get_config(name, default=None):
    """
    Attempts to retrieve a value from the settings module. If not, tries to get
    the value as a environment variable. If also is not found there, the default
    value is returned.
    :param name: The configuration value.
    :param default: The default value.
    :return: The requested configuration value, or the default value if the configuration was not found.
    """

    value = os.environ.get(name, default)
    try:
        import settings
        value = getattr(settings, name, default) or default
    except ModuleNotFoundError:
        pass

    return value


def random_string(length=12, alpha=True):
    str_set = 'abcdefghijklmnopqrstuvwxyz0123456789'
    if not alpha:
        str_set += '!@#$%^&*(-_=+)'

    return ''.join(random.SystemRandom().choice(str_set) for _ in [0] * length)


def serialize(item: ModAction):
    """
    Converts a ``ModAction`` object to a JSON serializable ``dict``.
    :param item:
    :return:
    """
    d = vars(item)
    del d['_reddit']
    d['mod'] = d.pop('_mod')
    return d


def valid_entry_id(value):
    """
    Validates and normalizes an entry ID in the format [ModAction_]<UUID>
    (abcdef01-cdef-0123-4567-0123456789ab), where the first part is optional,
    but is added if it's not found.

    :param value: The value to check and normalize.
    :return: The normalized value.
    :raises InvalidUsage if the entry id does not meet the required format.
    """
    if value is not None:
        if not pat_modentry.match(value):
            raise InvalidUsage('Invalid entry id')
        if not value.startswith('ModAction_'):
            value = 'ModAction_' + value

    return value


def filter_entry(entry):
    """
    Filters data out from a hidden entry
    :param entry: The entry to remove it's public data
    :return: The filtered entry
    """

    if 'hidden' in entry and entry['hidden']:
        clear_attrs = 'target_author,target_permalink,target_body,target_title,' \
                      'target_fullname,description,details'.split(',')
        for x in clear_attrs:
            entry[x] = None

    return entry


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
